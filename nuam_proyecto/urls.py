"""
URL configuration for nuam_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from app_nuam.views import home, RegistroView, carga_masiva, auditoria, calificaciones, crear_calificacion, eliminar_calificacion, editar_calificacion, normalizar_archivo, detalles_registro
from django.conf import settings
from django.conf.urls.static import static

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
    path('carga_masiva/normalizar/<int:id>', normalizar_archivo, name='normalizar_archivo'),
    path('carga_masiva/detalles_registro/<int:id>', detalles_registro, name='detalles_registro')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)