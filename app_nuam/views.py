from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages

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
