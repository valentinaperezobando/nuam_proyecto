# sirve para configurar el panel de amdin de django (http://127.0.0.1:8000/admin/)
from django.contrib import admin
from .models import UserProfile, RegistroBruto

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    
@admin.register(RegistroBruto)
class RegistroBrutoAdmin(admin.ModelAdmin): 
    list_display = ('payloadJson', 'archivo')