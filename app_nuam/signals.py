# singals.py para registrar acciones en la bitacora y notificaciones
# sensores cuando se crean, actualizan o eliminan usuarios por ejemplo
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Bitacora, Notificacion, UserProfile

# Cuando este sensor se active (se cree o actualice un usuario), se ejecuta la funcion
@receiver(post_save, sender=User) #post_save sensor que se activa dsp de guardar un usuario
def registrar_accion_usuario(sender, instance, created, **kwargs): #sender escucha si solo el cambio fue en modelo USER
    #intance es el usuario exactoq se guardo (ejemplo@gmail.com)
    # dice si se creo (true) o actualizo (false)
    if created:
        accion = "Creación de usuario"
        mensaje = f"Se ha creado el usuario: {instance.username}"
    else:
        accion = "Actualización de usuario"
        mensaje = f"Se actualizó el usuario: {instance.username}"

    Bitacora.objects.create(
        entidad="Usuario",
        accion=accion,
        usuario=instance,
        despues={"username": instance.username}
    )

    Notificacion.objects.create(
        usuario=instance,
        tipo="Usuario",
        mensaje=mensaje,
        nivel="info"
    )

# se activa cuando se elimina un usuario
@receiver(post_delete, sender=User)
def registrar_eliminacion_usuario(sender, instance, **kwargs):
    Bitacora.objects.create(
        entidad="Usuario",
        accion="Eliminación de usuario",
        usuario=instance,
        antes={"username": instance.username}
    )

    Notificacion.objects.create(
        usuario=instance,
        tipo="Usuario",
        mensaje=f"El usuario {instance.username} fue eliminado",
        nivel="warning"
    )
