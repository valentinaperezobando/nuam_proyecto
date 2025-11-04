from django.contrib.auth.models import User
from app_nuam.models import Notificacion

def notificar_error_admin(origen: str, detalle: str):
    """
    Envía una notificación al administrador ante un error en procesamiento o calificación.
    """
    admin = User.objects.filter(usuario__rol="admin").first()
    if admin:
        Notificacion.objects.create(
            usuario=admin,
            tipo=f"Error en {origen}",
            mensaje=detalle[:500],  # corta mensajes muy largos
            nivel="error"
        )
