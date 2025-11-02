from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app_nuam.views import home, RegistroView, carga_masiva, auditoria, calificaciones, crear_calificacion, eliminar_calificacion, editar_calificacion  
from app_nuam import admin_views
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
    path('administracion/usuarios/', admin_views.lista_usuarios, name='lista_usuarios'),
    path('administracion/bitacora/', admin_views.lista_bitacora, name='lista_bitacora'),
    path('administracion/notificaciones/',admin_views.lista_notificaciones),
]