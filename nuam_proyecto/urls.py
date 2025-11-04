from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app_nuam.views import (
    home, RegistroView, carga_masiva, auditoria, 
    listar_calificaciones, CrearCalificacionView, EditarCalificacionView,
    eliminar_calificacion, calcular_factores_calificacion, detalle_calificacion)
from app_nuam.views import home, RegistroView, carga_masiva, auditoria, eliminar_calificacion, normalizar_archivo, detalles_registro, eliminar_archivo
from django.conf import settings
from django.conf.urls.static import static
from app_nuam import admin_views
from app_nuam.views import redirigir_despues_login
from app_nuam import auditoria_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),      
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('logout/', LogoutView.as_view(next_page= 'home'), name= 'logout'),
    path('carga_masiva/', carga_masiva, name='carga_masiva'),
    path('calificaciones/', listar_calificaciones, name='listar_calificaciones'),
    path('calificaciones/crear/', CrearCalificacionView.as_view(), name='crear_calificacion'),
    path('calificaciones/<int:pk>/editar/', EditarCalificacionView.as_view(), name='editar_calificacion'),
    path('calificaciones/<int:pk>/eliminar/', eliminar_calificacion, name='eliminar_calificacion'),
    path('calificaciones/<int:pk>/calcular/', calcular_factores_calificacion, name='calcular_factores'),
    path('calificaciones/<int:pk>/', detalle_calificacion, name='detalle_calificacion'),
    path('carga_masiva/normalizar/<int:id>', normalizar_archivo, name='normalizar_archivo'),
    path('carga_masiva/detalles_registro/<int:id>', detalles_registro, name='detalles_registro'),
    path('carga_masiva/eliminar_archivo/<int:id>', eliminar_archivo, name='eliminar_archivo'),
    path('post_login/', redirigir_despues_login, name='post_login'),
    path('administracion/', admin_views.panel_admin, name='panel_admin'),
    path('administracion/usuarios/', admin_views.lista_usuarios, name='lista_usuarios'),
    path('administracion/bitacora/', admin_views.lista_bitacora, name='lista_bitacora'),
    path('administracion/notificaciones/',admin_views.lista_notificaciones),
    path('auditoria/', auditoria_views.panel_auditoria, name='auditoria'),
    path('auditoria/archivos/', auditoria_views.auditar_archivos, name='auditoria_archivos'),
    path('auditoria/calificaciones/', auditoria_views.auditar_calificaciones, name='auditoria_calificaciones'),
    path('auditoria/reporte/archivos.csv', auditoria_views.exportar_archivos_csv, name='auditoria_rep_archivos'),
    path('auditoria/reporte/calificaciones.csv', auditoria_views.exportar_calificaciones_csv, name='auditoria_rep_calificaciones'),
    path('auditoria/reporte/lotes.csv', auditoria_views.exportar_lotes_csv, name='auditoria_rep_lotes')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)