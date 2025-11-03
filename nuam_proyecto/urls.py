from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app_nuam.views import home, RegistroView, carga_masiva, auditoria, calificaciones, crear_calificacion, eliminar_calificacion, editar_calificacion  
from django.conf import settings
from django.conf.urls.static import static
from app_nuam import admin_views
from app_nuam.views import redirigir_despues_login
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),      
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name= 'login'),
    path('logout/', LogoutView.as_view(next_page= 'home'), name= 'logout'),
    path('carga_masiva/', carga_masiva, name='carga_masiva'),
    path('auditoria/', auditoria, name='auditoria'),
    path('calificaciones/', calificaciones, name='calificaciones'),
    path('crear_calificacion/', crear_calificacion, name='crear_calificacion'),
    path('eliminar_calificacion/', eliminar_calificacion, name='eliminar_calificacion'),
    path('editar_calificacion/', editar_calificacion, name='editar_calificacion'),
    path('post_login/', redirigir_despues_login, name='post_login'),
    path('administracion/', admin_views.panel_admin, name='panel_admin'),
    path('administracion/usuarios/', admin_views.lista_usuarios, name='lista_usuarios'),
    path('administracion/bitacora/', admin_views.lista_bitacora, name='lista_bitacora'),
    path('administracion/notificaciones/',admin_views.lista_notificaciones),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)