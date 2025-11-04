# sirve para configurar el panel de amdin de django (http://127.0.0.1:8000/admin/)
from django.contrib import admin
from .models import UserProfile, RegistroBruto, Calificacion, HistorialCalificacion
from django.contrib import messages

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')
    
@admin.register(RegistroBruto)
class RegistroBrutoAdmin(admin.ModelAdmin): 
    list_display = ('payloadJson', 'archivo')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'ejercicio', 'mercado', 'instrumento', 
        'fecha_pago', 'estado', 'origen', 'creado_por', 'fecha_creacion'
    )
    list_filter = ('estado', 'origen', 'mercado', 'ejercicio')
    search_fields = ('instrumento', 'descripcion', 'secuencia_evento')
    readonly_fields = (
        'fecha_creacion', 'fecha_modificacion', 
        'factores_calculados', 'errores_validacion'
    )
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'ejercicio', 'mercado', 'instrumento', 'descripcion',
                'fecha_pago', 'secuencia_evento', 'evento_capital'
            )
        }),
        ('Valores', {
            'fields': ('valor_historico', 'dividendo')
        }),
        ('Factores', {
            'fields': ('factores', 'factores_calculados'),
            'classes': ('collapse',)
        }),
        ('Estado y Metadatos', {
            'fields': (
                'estado', 'origen', 'creado_por',
                'registro_normalizado', 'lote_carga',
                'fecha_creacion', 'fecha_modificacion'
            )
        }),
        ('Validación y Observaciones', {
            'fields': ('observaciones', 'errores_validacion'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(HistorialCalificacion)
class HistorialCalificacionAdmin(admin.ModelAdmin):
    list_display = ('calificacion', 'usuario', 'accion', 'fecha')
    list_filter = ('accion', 'fecha')
    search_fields = ('calificacion__instrumento', 'usuario__username')
    readonly_fields = ('calificacion', 'usuario', 'accion', 'cambios', 'fecha')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    # auditoria de cambios en calificaciones
    def save_model(self, request, obj, form, change):
        if not change:
            obj.creado_por = request.user
            super().save_model(request, obj, form, change)
            HistorialCalificacion.objects.create(
                calificacion=obj, usuario=request.user, accion='creacion', cambios={'via': 'admin'}
            )
        else:
            anterior = Calificacion.objects.get(pk=obj.pk).to_dict()
            super().save_model(request, obj, form, change)
            nuevo = obj.to_dict()
            HistorialCalificacion.objects.create(
                calificacion=obj, usuario=request.user, accion='modificacion',
                cambios={'anterior': anterior, 'nuevo': nuevo, 'via': 'admin'}
            )
            messages.add_message(request, messages.INFO, 'Cambios registrados en historial.')

    def delete_model(self, request, obj):
        from .models import Bitacora
        Bitacora.objects.create(
            entidad='Calificacion', accion='eliminacion', antes=obj.to_dict(), despues=None, usuario=request.user
        )
        super().delete_model(request, obj)