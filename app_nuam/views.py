from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from app_nuam.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os, hashlib
from utils.pandas import procesar_archivo

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

def calificaciones(request):
    return render(request, 'calificaciones.html')

def crear_calificacion(request):
    return render(request, 'crear_calificacion.html')

def eliminar_calificacion(request):
    return render(request, 'eliminar_calificacion.html')

def editar_calificacion(request):
    return render(request, 'editar_calificacion.html')