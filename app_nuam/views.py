from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.models import User
from app_nuam.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from utils.pandas import procesar_archivo
from .forms import CalificacionForm, FiltroCalificacionesForm
from decimal import Decimal
from datetime import datetime
import os, hashlib
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
def redirigir_despues_login(request):
    perfil = getattr(request.user, 'usuario', None) # obtener el perfil asociado al usuario
    
    if perfil and perfil.rol == 'admin':
        return redirect('/administracion/')
    elif perfil and perfil.rol == 'contador':
        return redirect('/calificaciones/')
    elif perfil and perfil.rol == 'analista':
        return redirect('/carga_masiva/')
    elif perfil and perfil.rol == 'auditor':
        return redirect('/auditoria/')
    else:
        messages.warning(request, 'Tu rol no tiene asignado un módulo de acceso.')
        return redirect('/')
    
@login_required
def carga_masiva(request):
    perfil = getattr(request.user, 'usuario', None)
    if not perfil or perfil.rol != 'analista':
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
    
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
                
                notificacion = Notificacion.objects.create(
                    usuario = request.user,
                    tipo = 'ERROR',
                    mensaje = f'Error al procesar el archivo {file.name}',
                    nivel = 'medio'
                )
                notificacion.save()
            
        archivos = Archivo.objects.all()    
        messages.success(request, f"{len(archivos_subidos)} archivos cargados en el lote {lote_actual.id}")
        return render(request, 'carga_masiva.html',  {'archivos': archivos})
    
    archivos = Archivo.objects.all()    
    return render(request, 'carga_masiva.html', {'archivos': archivos}) 

def normalizar_archivo(request, id):
    archivo = Archivo.objects.get(id = id)
    plantilla = Plantilla.objects.get(nombre = 'Plantilla generica dividendos' )
    registro_bruto = RegistroBruto.objects.get(archivo=archivo)
    
    mapping = plantilla.mappingJson
    factores= plantilla.factoresJson
    filas = registro_bruto.payloadJson.get("datos", [])
    ok =True
    errores = 0
    
    if isinstance(filas, str):
        filas = json.loads(filas)
    if isinstance(filas, dict):
        filas = [filas]
    registros_creados = 0
        
    for fila in filas:
        try:
            data_factores = {}
            for clave, nombre_col in factores.items():
                valor = fila.get(nombre_col)
                if valor is not None:
                    try:
                        data_factores[clave] = float(valor)
                    except (ValueError, TypeError):
                        try:
                            data_factores[clave] = datetime.strptime(valor, "%d-%m-%Y").date()
                        except Exception:
                            data_factores[clave] = valor
                
            # crear registro normalizado
            rn = RegistroNormalizado.objects.create(
                plantilla = plantilla,
                archivo = archivo,
                ejercicio = int(fila.get(mapping['ejercicio'])),
                instrumento = fila.get(mapping['instrumento']),
                fecha_pago_dividendo=datetime.strptime(fila.get(mapping['fecha_pago_dividendo']), "%d-%m-%Y").date(),
                descripcion_dividendo = fila.get(mapping['descripcion_dividendo']),
                secuencia_evento = fila.get(mapping['secuencia_evento']),
                acogido_isfut = fila.get(mapping.get('acogido_isfut')) if mapping.get('acogido_isfut') else fila.get('acogido_isfut'),
                origen = fila.get(mapping.get('origen') or 'carga_masiva'),
                factor_actualizacion = Decimal(fila.get(mapping.get('factor_actualizacion')) or 0),
                factores = data_factores
            )
            registros_creados += 1

            # Crear Calificacion asociada a este RegistroNormalizado
            # Mapear factores del registro normalizado a la estructura esperada por Calificacion
            cal_factores = {}
            rn_factores = rn.factores or {}
            for i in range(8, 38):
                # posibles claves en registro: 'factor_8', 'factor8', '8'
                keys_to_try = [f'factor_{i}', f'factor{i}', str(i), f'F{i}', f'factor_{i:02d}', f'factor{i:02d}']
                value = 0
                for k in keys_to_try:
                    if k in rn_factores and rn_factores.get(k) is not None:
                        try:
                            value = float(rn_factores.get(k))
                        except (ValueError, TypeError):
                            value = 0
                        break
                cal_factores[f'factor_{i}'] = round(float(value or 0), 8)

            # determinar usuario creador (si no hay, usar primer superuser para no violar FK)
            creador = request.user if request.user.is_authenticated else (User.objects.filter(is_superuser=True).first() or User.objects.first())

            cal = Calificacion.objects.create(
                ejercicio = rn.ejercicio,
                mercado = getattr(rn, 'mercado', 'AC') if hasattr(rn,'mercado') else 'AC',
                instrumento = rn.instrumento,
                descripcion = rn.descripcion_dividendo,
                fecha_pago = rn.fecha_pago_dividendo,
                secuencia_evento = rn.secuencia_evento,
                evento_capital = '',
                valor_historico = Decimal('0.00'),
                dividendo = Decimal('0.00'),
                factores = cal_factores,
                factores_calculados = {}, 
                estado = 'pendiente',
                origen = 'carga_masiva',
                creado_por = creador,
                registro_normalizado = rn,
                lote_carga = archivo.lote_carga,
                observaciones = ''
            )

            # crear historial mínimo
            HistorialCalificacion.objects.create(
                calificacion=cal,
                usuario=creador,
                accion='creacion',
                cambios={'via': 'carga_masiva', 'registro_normalizado_id': rn.id}
            )

            archivo.estado = "NORMALIZADO"
            archivo.save()
            
        except Exception as e:
            ok = False
            notificacion = Notificacion.objects.create(
                usuario = request.user,
                tipo = 'ERROR',
                mensaje = f'Error al normalizar el archivo {archivo.nombre}, no hay correspondencia de datos tributarios',
                nivel = 'ERROR'
            )
            notificacion.save()
            errores+=1
    if ok == False:
        messages.error(request, f'Error al normalizar {errores} registros en {archivo.nombre}. No hay correspondencia con datos tributarios' )
    else:
        messages.success(request, f'{registros_creados} registros normalizados exitosamente')
    return redirect('carga_masiva')

def detalles_registro(request, id):
    archivo = Archivo.objects.get(id=id)
    normalizados = RegistroNormalizado.objects.filter(archivo = archivo)
    return render(request, 'detalles_registro.html', {'normalizados': normalizados})

def eliminar_archivo(request, id):
    try: 
        archivo = Archivo.objects.get(id=id)
        archivo.delete()
        messages.success(request, 'Archivo eliminado correctamente.')
        return redirect('/carga_masiva/')
    except Exception as e:
        messages.error(request, f"Error al eliminar el archivo: {str(e)}")

def auditoria(request):
    perfil = getattr(request.user, 'usuario', None)
    if not perfil or perfil.rol != 'auditor':
        messages.warning(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('home')
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
        # pasar estados a la plantilla para renderizar select
        return render(request, 'calificaciones/editar_calificacion.html', {
            'form': form,
            'calificacion': calificacion,
            'estados': Calificacion.ESTADOS
        })
    
    def post(self, request, pk):
        calificacion = get_object_or_404(Calificacion, pk=pk)
        
        # Guardar estado anterior para historial
        datos_anteriores = getattr(calificacion, 'to_dict', lambda: None)()
        
        form = CalificacionForm(request.POST, instance=calificacion)
        
        if form.is_valid():
            calificacion_actualizada = form.save(commit=False)

            # Validar y asignar nuevo estado conservando el tipo original de la choice
            nuevo_estado_raw = request.POST.get('estado')
            nuevo_estado_assignado = None
            if nuevo_estado_raw is not None:
                # Buscar la key original en Calificacion.ESTADOS (respetando tipos)
                for key, label in getattr(Calificacion, 'ESTADOS', []):
                    try:
                        # comparar por string para evitar problemas de tipo
                        if str(key) == str(nuevo_estado_raw):
                            nuevo_estado_assignado = key
                            break
                    except Exception:
                        continue

            if nuevo_estado_assignado is not None:
                calificacion_actualizada.estado = nuevo_estado_assignado

            # Guardar cambios (primera pasada)
            calificacion_actualizada.save()

            # Forzar persistencia del estado tal como el usuario lo pidió (evita sobreescrituras posteriores)
            if nuevo_estado_assignado is not None:
                # actualizamos directamente en la BD con el valor original (tipo correcto)
                Calificacion.objects.filter(pk=calificacion_actualizada.pk).update(estado=nuevo_estado_assignado)

            # Crear entrada en historial
            HistorialCalificacion.objects.create(
                calificacion=calificacion_actualizada,
                usuario=request.user,
                accion='modificacion',
                cambios={
                    'anterior': datos_anteriores,
                    'nuevo': getattr(calificacion_actualizada, 'to_dict', lambda: None)()
                }
            )
            
            messages.success(request, 'Calificación actualizada exitosamente')
            return redirect('listar_calificaciones')
        else:
            messages.error(request, 'Error al actualizar la calificación')
        
        return render(request, 'calificaciones/editar_calificacion.html', {
            'form': form,
            'calificacion': calificacion,
            'estados': Calificacion.ESTADOS
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

