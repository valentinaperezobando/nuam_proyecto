# cree este para hacer el modulo de admintracion
# de usuario y roles,bitacoras, DEL SISTEMA NUAM
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from .models import UserProfile, Bitacora, Notificacion

# usuario admin puede entrar
def es_admin(user):
    # Verifica si el usuario tiene rol de admin
    return hasattr(user, 'usuario') and user.usuario.rol == 'admin'

# pag lista de usuario
@user_passes_test(es_admin) #funcion tipi tag para cambiar la vista q le corresponde al admin
def lista_usuarios(request):   
    usuarios = UserProfile.objects.select_related('user') 
    return render(request, 'admin/usuarios.html', {'usuarios': usuarios})

# pag bitacora
@user_passes_test(es_admin)
def lista_bitacora(request):
    registros = Bitacora.objects.all().order_by('-fecha') #ordenar por fecha descendente
    return render(request, 'admin/bitacora.html', {'registros': registros})

# pag notificaciones
@user_passes_test(es_admin)
def lista_notificaciones(request):
    notificaciones = Notificacion.objects.all().order_by('-fecha') #ordenar por fecha descendente
    return render(request, 'admin/notificaciones.html', {'notificaciones': notificaciones})

#
@user_passes_test(es_admin)
def panel_admin(request):
    usuarios_count = UserProfile.objects.count()
    bitacora = Bitacora.objects.all().order_by('-fecha')[:5]  # Últimos 5 registros
    notificacion = Notificacion.objects.all().order_by('-fecha')[:5]  # Últimas 5 notificaciones

    contexto = {
        'usuarios_count': usuarios_count,
        'bitacora': bitacora,
        'notificacion': notificacion,
    }
    return render(request, 'admin/panel_admin.html',contexto)