from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app_nuam.views import (
    home, RegistroView, carga_masiva, auditoria, 
    listar_calificaciones, CrearCalificacionView, EditarCalificacionView,
    eliminar_calificacion, calcular_factores_calificacion, detalle_calificacion)
from django.conf import settings
from django.conf.urls.static import static
from app_nuam import admin_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),      
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('logout/', LogoutView.as_view(next_page= 'home'), name= 'logout'),
    path('carga_masiva/', carga_masiva, name='carga_masiva'),
    path('auditoria/', auditoria, name='auditoria'),
    path('calificaciones/', listar_calificaciones, name='listar_calificaciones'),
    path('calificaciones/crear/', CrearCalificacionView.as_view(), name='crear_calificacion'),
    path('calificaciones/<int:pk>/editar/', EditarCalificacionView.as_view(), name='editar_calificacion'),
    path('calificaciones/<int:pk>/eliminar/', eliminar_calificacion, name='eliminar_calificacion'),
    path('calificaciones/<int:pk>/calcular/', calcular_factores_calificacion, name='calcular_factores'),
    path('calificaciones/<int:pk>/', detalle_calificacion, name='detalle_calificacion'),
    
    path('administracion/usuarios/', admin_views.lista_usuarios, name='lista_usuarios'),
    path('administracion/bitacora/', admin_views.lista_bitacora, name='lista_bitacora'),
    path('administracion/notificaciones/',admin_views.lista_notificaciones),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)