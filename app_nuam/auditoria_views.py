# app_nuam/auditoria_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from datetime import datetime
from .models import Archivo, LoteCarga, RegistroNormalizado, Calificacion, HistorialCalificacion, Bitacora
from django.utils import timezone
from django.db.models.functions import TruncDate
import json


def es_auditor(user):
    return hasattr(user, 'usuario') and user.usuario.rol == 'auditor'

def _parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except Exception:
        return None

@login_required
def panel_auditoria(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    total_lotes = LoteCarga.objects.count()
    total_archivos = Archivo.objects.count()
    total_norm = RegistroNormalizado.objects.count()
    total_calif = Calificacion.objects.count()

    from django.utils import timezone
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    hoy = timezone.now().date()
    hace_14 = hoy - timezone.timedelta(days=13)

    lotes_por_dia = list(
        LoteCarga.objects.filter(fecha_creacion__date__gte=hace_14)
        .annotate(dia=TruncDate('fecha_creacion'))
        .values('dia').annotate(c=Count('id')).order_by('dia')
    )
    serie = []
    for i in range(14):
        d = hace_14 + timezone.timedelta(days=i)
        serie.append({'dia': d.strftime('%Y-%m-%d'),
                      'c': next((x['c'] for x in lotes_por_dia if x['dia'] == d), 0)})

    ctx = {
        'total_lotes': total_lotes,
        'total_archivos': total_archivos,
        'total_norm': total_norm,
        'total_calif': total_calif,
        'chart_lotes_14d': json.dumps({
            'labels': [x['dia'] for x in serie],
            'values': [x['c'] for x in serie],
        }),
        'ult_hist': HistorialCalificacion.objects.select_related('calificacion','usuario').order_by('-fecha')[:8],
        'ult_bitacora': Bitacora.objects.select_related('usuario').order_by('-fecha')[:8],
    }
    return render(request, 'auditoria/panel.html', ctx)

@login_required
def auditar_archivos(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    q = request.GET.get('q','').strip()
    estado = request.GET.get('estado','').strip()
    tipo = request.GET.get('tipo','').strip()
    lote = request.GET.get('lote','').strip()
    fdesde = _parse_date(request.GET.get('desde',''))
    fhasta = _parse_date(request.GET.get('hasta',''))

    archivos = Archivo.objects.select_related('lote_carga')
    if q: archivos = archivos.filter(Q(nombre__icontains=q)|Q(hash__icontains=q))
    if estado: archivos = archivos.filter(estado__iexact=estado)
    if tipo: archivos = archivos.filter(tipo__iexact=tipo)
    if lote: archivos = archivos.filter(lote_carga__id=lote)
    if fdesde: archivos = archivos.filter(lote_carga__fecha_creacion__date__gte=fdesde.date())
    if fhasta: archivos = archivos.filter(lote_carga__fecha_creacion__date__lte=fhasta.date())
    archivos = archivos.order_by('-lote_carga__fecha_creacion','id')
    page = Paginator(archivos, 25).get_page(request.GET.get('page'))

    por_estado = list(Archivo.objects.values('estado').annotate(c=Count('id')).order_by('-c'))
    por_tipo   = list(Archivo.objects.values('tipo').annotate(c=Count('id')).order_by('-c'))

    return render(request, 'auditoria/archivos.html', {
        'page': page,
        'filtros': {'q':q,'estado':estado,'tipo':tipo,'lote':lote,'desde':request.GET.get('desde',''),'hasta':request.GET.get('hasta','')},
        'chart_por_estado': json.dumps({'labels':[e['estado'] or '—' for e in por_estado], 'values':[e['c'] for e in por_estado]}),
        'chart_por_tipo': json.dumps({'labels':[t['tipo'] or '—' for t in por_tipo], 'values':[t['c'] for t in por_tipo]}),
    })

@login_required
def auditar_lotes(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    estado = request.GET.get('estado', '').strip()
    usuario = request.GET.get('usuario', '').strip()

    lotes = LoteCarga.objects.select_related('usuario').annotate(num_archivos=Count('archivo'))
    if estado:
        lotes = lotes.filter(estado=estado)
    if usuario:
        lotes = lotes.filter(usuario__username__icontains=usuario)

    lotes = lotes.order_by('-fecha_creacion')
    page = Paginator(lotes, 25).get_page(request.GET.get('page'))

    return render(request, 'auditoria/lotes.html', {
        'page': page,
        'estado': estado,
        'usuario': usuario,
    })

@login_required
def auditar_calificaciones(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')

    q = request.GET.get('q','').strip()
    usuario = request.GET.get('usuario','').strip()
    accion = request.GET.get('accion','').strip()
    fdesde = _parse_date(request.GET.get('desde',''))
    fhasta = _parse_date(request.GET.get('hasta',''))

    historial = HistorialCalificacion.objects.select_related('calificacion','usuario')
    if q:
        historial = historial.filter(Q(calificacion__instrumento__icontains=q) | Q(calificacion__descripcion__icontains=q))
    if usuario: historial = historial.filter(usuario__username__icontains=usuario)
    if accion: historial = historial.filter(accion=accion)
    if fdesde: historial = historial.filter(fecha__date__gte=fdesde.date())
    if fhasta: historial = historial.filter(fecha__date__lte=fhasta.date())
    historial = historial.order_by('-fecha')
    page = Paginator(historial, 30).get_page(request.GET.get('page'))

    # Series 14 días por acción
    from django.utils import timezone
    from django.db.models.functions import TruncDate
    from django.db.models import Count
    hoy = timezone.now().date()
    hace_14 = hoy - timezone.timedelta(days=13)
    hist_por_dia = list(
        HistorialCalificacion.objects.filter(fecha__date__gte=hace_14)
        .annotate(dia=TruncDate('fecha'))
        .values('dia','accion').annotate(c=Count('id')).order_by('dia','accion')
    )
    acciones = ['creacion','modificacion','calculo']
    mapa = { (r['dia'].strftime('%Y-%m-%d'), r['accion']): r['c'] for r in hist_por_dia }
    serie = []
    for i in range(14):
        d = hace_14 + timezone.timedelta(days=i)
        row = {'dia': d.strftime('%Y-%m-%d')}
        for a in acciones:
            row[a] = mapa.get((row['dia'], a), 0)
        serie.append(row)

    calif_por_estado = list(Calificacion.objects.values('estado').annotate(c=Count('id')).order_by('-c'))
    hace_30 = hoy - timezone.timedelta(days=30)
    top_users = list(
        HistorialCalificacion.objects.filter(fecha__date__gte=hace_30)
        .values('usuario__username').annotate(c=Count('id')).order_by('-c')[:10]
    )

    return render(request, 'auditoria/calificaciones.html', {
        'page': page,
        'filtros': {'q':q,'usuario':usuario,'accion':accion,'desde':request.GET.get('desde',''),'hasta':request.GET.get('hasta','')},
        'chart_hist_14d': json.dumps({
            'labels': [x['dia'] for x in serie],
            'creacion': [x['creacion'] for x in serie],
            'modificacion': [x['modificacion'] for x in serie],
            'calculo': [x['calculo'] for x in serie],
        }),
        'chart_calif_estado': json.dumps({
            'labels': [e['estado'] or '—' for e in calif_por_estado],
            'values': [e['c'] for e in calif_por_estado],
        }),
        'chart_top_users': json.dumps({
            'labels': [u['usuario__username'] or '—' for u in top_users],
            'values': [u['c'] for u in top_users],
        }),
    })



# Exportar reportes CSV
from django.http import HttpResponse
import csv
from urllib.parse import urlencode

@login_required
def exportar_archivos_csv(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para esta acción.')
        return redirect('home')

    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    lote = request.GET.get('lote', '').strip()
    fdesde = _parse_date(request.GET.get('desde', ''))
    fhasta = _parse_date(request.GET.get('hasta', ''))

    qs = Archivo.objects.select_related('lote_carga')
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(hash__icontains=q))
    if estado:
        qs = qs.filter(estado__iexact=estado)
    if tipo:
        qs = qs.filter(tipo__iexact=tipo)
    if lote:
        qs = qs.filter(lote_carga__id=lote)
    if fdesde:
        qs = qs.filter(lote_carga__fecha_creacion__date__gte=fdesde.date())
    if fhasta:
        qs = qs.filter(lote_carga__fecha_creacion__date__lte=fhasta.date())
    qs = qs.order_by('-lote_carga__fecha_creacion', 'id')

    # CSV
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="auditoria_archivos.csv"'
    writer = csv.writer(resp)
    writer.writerow(['ID', 'Nombre', 'Tipo', 'Estado', 'Lote', 'Fecha Lote', 'Hash'])

    for a in qs:
        writer.writerow([
            a.id, a.nombre, a.tipo, a.estado,
            getattr(a.lote_carga, 'id', ''),
            getattr(a.lote_carga, 'fecha_creacion', ''),
            a.hash
        ])
    return resp


@login_required
def exportar_lotes_csv(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para esta acción.')
        return redirect('home')

    estado = request.GET.get('estado', '').strip()
    usuario = request.GET.get('usuario', '').strip()

    qs = LoteCarga.objects.select_related('usuario').annotate(num_archivos=Count('archivo'))
    if estado:
        qs = qs.filter(estado=estado)
    if usuario:
        qs = qs.filter(usuario__username__icontains=usuario)
    qs = qs.order_by('-fecha_creacion')

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="auditoria_lotes.csv"'
    writer = csv.writer(resp)
    writer.writerow(['ID Lote', 'Estado', 'Usuario', 'Fecha creación', 'N° Archivos'])
    for l in qs:
        writer.writerow([l.id, l.estado, l.usuario.username, l.fecha_creacion, getattr(l, 'num_archivos', '')])
    return resp


@login_required
def exportar_calificaciones_csv(request):
    if not es_auditor(request.user):
        messages.warning(request, 'No tienes permisos para esta acción.')
        return redirect('home')

    q = request.GET.get('q', '').strip()
    usuario = request.GET.get('usuario', '').strip()
    accion = request.GET.get('accion', '').strip()
    fdesde = _parse_date(request.GET.get('desde', ''))
    fhasta = _parse_date(request.GET.get('hasta', ''))

    hist = HistorialCalificacion.objects.select_related('calificacion', 'usuario')
    if q:
        hist = hist.filter(Q(calificacion__instrumento__icontains=q) | Q(calificacion__descripcion__icontains=q))
    if usuario:
        hist = hist.filter(usuario__username__icontains=usuario)
    if accion:
        hist = hist.filter(accion=accion)
    if fdesde:
        hist = hist.filter(fecha__date__gte=fdesde.date())
    if fhasta:
        hist = hist.filter(fecha__date__lte=fhasta.date())
    hist = hist.order_by('-fecha')

    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="auditoria_calificaciones_historial.csv"'
    writer = csv.writer(resp)
    writer.writerow([
        'Fecha', 'Acción', 'Usuario',
        'ID Calificación', 'Instrumento', 'Descripción',
        'Cambios (JSON)'
    ])
    for h in hist:
        writer.writerow([
            h.fecha, h.accion, h.usuario.username,
            getattr(h.calificacion, 'id', ''),
            getattr(h.calificacion, 'instrumento', ''),
            (getattr(h.calificacion, 'descripcion', '') or '')[:150],
            h.cambios 
        ])
    return resp
