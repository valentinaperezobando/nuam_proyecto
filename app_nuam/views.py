from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from app_nuam.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from datetime import datetime
import os, hashlib
from utils.pandas import procesar_archivo
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
                
        archivos = Archivo.objects.all()    
        messages.success(request, f"{len(archivos_subidos)} archivos cargados en el lote {lote_actual.id}")
        return render(request, 'carga_masiva.html',  {'archivos': archivos})
    
    archivos = Archivo.objects.all()    
    return render(request, 'carga_masiva.html', {'archivos': archivos}) 

def normalizar_archivo(request, id):
    archivo = Archivo.objects.get(id = id)
    plantilla = Plantilla.objects.get(id = 2)
    registro_bruto = RegistroBruto.objects.get(archivo=archivo)
    
    mapping = plantilla.mappingJson
    factores= plantilla.factoresJson
    filas = registro_bruto.payloadJson.get("datos", [])
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
                    except ValueError:
                        try:
                            data_factores[clave] = datetime.strptime(valor, "%d-%m-%Y").date()
                        except ValueError:
                            data_factores[clave] = valor  # mantener como string si nada funciona
                    
                print("Fila:", fila)
                print("Mapping ejercicio:", mapping['ejercicio'])
                print("Valor ejercicio:", fila.get(mapping['ejercicio']))
        
            RegistroNormalizado.objects.create(
                plantilla = plantilla,
                archivo = archivo,
                ejercicio = int(fila.get(mapping['ejercicio'])),
                instrumento = fila.get(mapping['instrumento']),
                fecha_pago_dividendo=datetime.strptime(fila.get(mapping['fecha_pago_dividendo']), "%d-%m-%Y").date(),
                descripcion_dividendo = fila.get(mapping['descripcion_dividendo']),
                secuencia_evento = fila.get(mapping['secuencia_evento']),
                acogido_isfut = fila.get(mapping['acogido_isfut']),
                origen = fila.get(mapping['origen']),
                factor_actualizacion = Decimal(fila.get(mapping['factor_actualizacion']) or 0),
                factores = data_factores
            )
            registros_creados += 1
            archivo.estado = "NORMALIZADO"
            archivo.save()
        except Exception as e:
            messages.error(request, e )
    messages.success(request, f'{registros_creados} registros normalizados exitosamente')
    return redirect('carga_masiva')

def detalles_registro(request, id):
    archivo = Archivo.objects.get(id=id)
    normalizados = RegistroNormalizado.objects.filter(archivo = archivo)
    return render(request, 'detalles_registro.html', {'normalizados': normalizados})

def auditoria(request):
    return render(request, 'auditoria.html')

def calificaciones(request):
    return render(request, 'calificaciones.html')

def crear_calificacion(request):
    return render(request, 'crear_calificacion.html')

def eliminar_calificacion(request):  
    return render(request, 'eliminar_calificacion.html')

def editar_calificacion(request):
    return render(request, 'editar_calificacion.html')