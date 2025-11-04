# cree este para hacer el modulo de admintracion
# de usuario y roles,bitacoras, DEL SISTEMA NUAM
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, Bitacora, Notificacion

# usuario admin puede entrar
def es_admin(user):
    # Verifica si el usuario tiene rol de admin
    return hasattr(user, 'usuario') and user.usuario.rol == 'admin'

# pag lista de usuario
@user_passes_test(es_admin) #funcion tipi tag para cambiar la vista q le corresponde al admin
def lista_usuarios(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        nuevo_rol = request.POST.get("rol")

        roles_validos = {"admin", "contador", "analista", "auditor"}
        if user_id and nuevo_rol in roles_validos:
            usuario = UserProfile.objects.select_related('user').get(id=user_id)
            rol_anterior = usuario.rol
            usuario.rol = nuevo_rol
            usuario.save()

            # registra en bitácora
            Bitacora.objects.create(
                entidad="Usuario",
                accion=f"Actualización de rol de {rol_anterior} a {nuevo_rol}",
                usuario=request.user
            )

            # notifica
            Notificacion.objects.create(
                usuario=usuario.user,
                tipo="Cambio de rol",
                mensaje=f"Tu rol ha sido actualizado a {nuevo_rol.title()}",
                nivel="info"
            )

            messages.success(
                request,
                f"Se actualizó el rol de {usuario.user.username} a {nuevo_rol.title()} correctamente"
            )
        else:
            messages.warning(request, "Datos inválidos al actualizar rol")

    return redirect('panel_admin')


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
    usuarios = UserProfile.objects.select_related('user')
    usuarios_count = usuarios.count()
    bitacora = Bitacora.objects.all().order_by('-fecha')[:5]
    notificacion = Notificacion.objects.all().order_by('-fecha')[:5]

    contexto = {
        'usuarios': usuarios,
        'usuarios_count': usuarios_count,
        'bitacora': bitacora,
        'notificacion': notificacion,
    }

    return render(request, 'admin/panel_admin.html', contexto)