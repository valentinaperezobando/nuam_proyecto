from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from app_nuam.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import os, hashlib
from utils.pandas import procesar_archivo
from .forms import CalificacionForm, FiltroCalificacionesForm
import json

# Create your views here.
def home(request): 
    return render(request, 'home.html')

class RegistroView(View):

    def get(self, req):
        return render(req, 'registration/registro.html')
    
    def post(self, req):
        # 1. Recuperamos los datos del formulario
        email = req.POST['email']
        password = req.POST['password']
        pass_repeat = req.POST['pass_repeat']
        # 2. Validamos que contraseñas concidan
        if password != pass_repeat:
            messages.warning(req, 'Contraseñas no coinciden')
            return redirect('/registro')
        
        if User.objects.filter(username=email).exists():
            messages.warning(req, 'El usuario ya existe')
        # 3. Creamos al usuario
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()
        messages.success(req, 'Usuario creado')
        return redirect('/')
    
@login_required
def carga_masiva(request):
    if request.method == 'POST':
        archivos_subidos = request.FILES.getlist('archivo')
        if not archivos_subidos:
            messages.error(request, "Debes seleccionar un archivo.")
            return redirect('carga_masiva')
        
        lote_actual = LoteCarga.objects.create(
            usuario = request.user, 
            estado = 'en proceso',
            origen = 'Ingresado desde la interfaz web'
        )
        
        for file in archivos_subidos:
            hash_archivo = hashlib.md5(file.read()).hexdigest()
            file.seek(0)  # importante: volver al inicio antes de guardar el archivo

            if Archivo.objects.filter(hash=hash_archivo).exists():
                continue
            
            extensiones_validas = ['.pdf', '.csv', '.xls', '.xlsx']
            extension = os.path.splitext(file.name)[1].lower()
            if extension not in extensiones_validas:
                messages.error(request, "Formato no permitido. Solo se aceptan PDF, CSV o Excel.")
                return redirect('carga_masiva')
            
            nuevo_archivo = Archivo()
            nuevo_archivo.archivo = file
            nuevo_archivo.nombre = file.name
            nuevo_archivo.tipo = extension.replace('.', '')
            nuevo_archivo.hash = hash_archivo
            nuevo_archivo.estado = 'CARGADO'
            nuevo_archivo.lote_carga=lote_actual
            nuevo_archivo.save()
            
            try:
                procesar_archivo(nuevo_archivo)
            except Exception as e:
                messages.error(request, f'Error procesando {file.name}; {e}')
            
        messages.success(request, f"{len(archivos_subidos)} archivos cargados en el lote {lote_actual.id}")
        return render(request, 'carga_masiva.html')
    return render(request, 'carga_masiva.html') 

def auditoria(request):
    return render(request, 'auditoria.html')

@login_required
def listar_calificaciones(request):
    # Verificar rol
    if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
        messages.warning(request, 'No tienes permisos para acceder a esta sección')
        return redirect('home')
    
    # Obtener todas las calificaciones
    calificaciones = Calificacion.objects.all().select_related('creado_por')
    
    # Aplicar filtros
    filtro_form = FiltroCalificacionesForm(request.GET)
    if filtro_form.is_valid():
        mercado = filtro_form.cleaned_data.get('mercado')
        origen = filtro_form.cleaned_data.get('origen')
        ejercicio = filtro_form.cleaned_data.get('ejercicio')
        estado = filtro_form.cleaned_data.get('estado')
        
        if mercado:
            calificaciones = calificaciones.filter(mercado=mercado)
        if origen:
            calificaciones = calificaciones.filter(origen=origen)
        if ejercicio:
            calificaciones = calificaciones.filter(ejercicio=ejercicio)
        if estado:
            calificaciones = calificaciones.filter(estado=estado)
    
    # Búsqueda por texto
    search = request.GET.get('search', '')
    if search:
        calificaciones = calificaciones.filter(
            Q(instrumento__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(secuencia_evento__icontains=search)
        )
    
    context = {
        'calificaciones': calificaciones,
        'filtro_form': filtro_form,
        'search': search,
    }
    
    return render(request, 'calificaciones/listar_calificaciones.html', context)


class CrearCalificacionView(LoginRequiredMixin, View):
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar rol de contador
        if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
            messages.warning(request, 'No tienes permisos para acceder a esta sección')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = CalificacionForm()
        return render(request, 'calificaciones/crear_calificacion.html', {'form': form})
    
    def post(self, request):
        form = CalificacionForm(request.POST)
        
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.creado_por = request.user
            calificacion.origen = 'manual'
            calificacion.estado = 'pendiente'
            calificacion.save()
            
            # Crear entrada en historial
            HistorialCalificacion.objects.create(
                calificacion=calificacion,
                usuario=request.user,
                accion='creacion',
                cambios={'tipo': 'creacion_manual'}
            )
            
            messages.success(request, f'Calificación creada exitosamente. ID: {calificacion.id}')
            return redirect('listar_calificaciones')
        else:
            messages.error(request, 'Error al crear la calificación. Por favor revisa los campos.')
        
        return render(request, 'calificaciones/crear_calificacion.html', {'form': form})


class EditarCalificacionView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
            messages.warning(request, 'No tienes permisos para acceder a esta sección')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        calificacion = get_object_or_404(Calificacion, pk=pk)
        form = CalificacionForm(instance=calificacion)
        return render(request, 'calificaciones/editar_calificacion.html', {
            'form': form,
            'calificacion': calificacion
        })
    
    def post(self, request, pk):
        calificacion = get_object_or_404(Calificacion, pk=pk)
        
        # Guardar estado anterior para historial
        datos_anteriores = calificacion.to_dict()
        
        form = CalificacionForm(request.POST, instance=calificacion)
        
        if form.is_valid():
            calificacion_actualizada = form.save(commit=False)
            calificacion_actualizada.save()
            
            # Crear entrada en historial
            HistorialCalificacion.objects.create(
                calificacion=calificacion_actualizada,
                usuario=request.user,
                accion='modificacion',
                cambios={
                    'anterior': datos_anteriores,
                    'nuevo': calificacion_actualizada.to_dict()
                }
            )
            
            messages.success(request, 'Calificación actualizada exitosamente')
            return redirect('listar_calificaciones')
        else:
            messages.error(request, 'Error al actualizar la calificación')
        
        return render(request, 'calificaciones/editar_calificacion.html', {
            'form': form,
            'calificacion': calificacion
        })


@login_required
def eliminar_calificacion(request, pk):
    # Verificar rol
    if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
        messages.warning(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    calificacion = get_object_or_404(Calificacion, pk=pk)
    
    if request.method == 'POST':
        # Guardar datos antes de eliminar para historial/bitácora
        datos_eliminados = calificacion.to_dict()
        
        # Crear registro en Bitacora
        from .models import Bitacora
        Bitacora.objects.create(
            entidad='Calificacion',
            accion='eliminacion',
            antes=datos_eliminados,
            despues=None,
            usuario=request.user
        )
        
        calificacion.delete()
        messages.success(request, 'Calificación eliminada exitosamente')
        return redirect('listar_calificaciones')
    
    return render(request, 'calificaciones/confirmar_eliminar.html', {
        'calificacion': calificacion
    })


@login_required
def calcular_factores_calificacion(request, pk):
    if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
        messages.warning(request, 'No tienes permisos para realizar esta acción')
        return redirect('home')
    
    calificacion = get_object_or_404(Calificacion, pk=pk)
    
    # Recalcular factores
    calificacion.calcular_factores_automaticos()
    calificacion.save()
    
    # Crear entrada en historial
    HistorialCalificacion.objects.create(
        calificacion=calificacion,
        usuario=request.user,
        accion='calculo',
        cambios={'factores_calculados': calificacion.factores_calculados}
    )
    
    messages.success(request, 'Factores recalculados exitosamente')
    return redirect('editar_calificacion', pk=pk)


@login_required
def detalle_calificacion(request, pk):
    if not hasattr(request.user, 'usuario') or request.user.usuario.rol != 'contador':
        messages.warning(request, 'No tienes permisos para acceder a esta sección')
        return redirect('home')
    
    calificacion = get_object_or_404(Calificacion, pk=pk)
    historial = calificacion.historial.all()[:10]  # Últimas 10 modificaciones
    
    context = {
        'calificacion': calificacion,
        'historial': historial,
    }
    
    return render(request, 'calificaciones/detalle_calificacion.html', context)