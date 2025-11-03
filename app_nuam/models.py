# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    roles =(('usuario', 'Usuario'), ('admin', 'Admin'), ('analista', 'Analista'), ('contador', 'Contador'), ('auditor', 'Auditor'))
    user = models.OneToOneField(User, related_name = 'usuario', on_delete=models.CASCADE)
    rol = models.CharField(max_length=255, choices=roles, default = 'usuario')
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} {(self.rol)}'
    
class Rol(models.Model):
    nombre = models.CharField(max_length=100)

class Permiso(models.Model):
    clave = models.CharField(max_length=100)

class Reporte(models.Model):
    tipo = models.CharField(max_length=100)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    urlDescarga = models.URLField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def generar_reporte(self, criterios):
        # Lógica para generar el reporte basado en ciertos criterios
        pass

class Bitacora(models.Model):
    entidad = models.CharField(max_length=100)
    accion = models.CharField(max_length=100)
    antes = models.JSONField(null=True, blank=True)
    despues = models.JSONField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

class LoteCarga(models.Model):
    estados = (('en proceso', 'En Proceso'), ('procesado', 'Procesado'), ('error', 'Error'))
    origen = models.CharField(max_length=100)
    estado = models.CharField(max_length=50, choices=estados, default='en proceso')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def validar_resumen(self):
        # Lógica para validar el resumen del lote de carga
        pass

class Archivo(models.Model):
    archivo = models.FileField(upload_to='uploads/', null=False, default=False)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30)
    hash = models.CharField(max_length=200, unique=True)
    estado = models.CharField(max_length=50)
    lote_carga = models.ForeignKey(LoteCarga, on_delete=models.CASCADE)

class RegistroBruto(models.Model):
    payloadJson = models.JSONField()
    erroresJson = models.JSONField(null=True, blank=True)
    valido = models.BooleanField(default=False)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)

class Plantilla(models.Model):
    nombre = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    mappingJson = models.JSONField()

    def probar_plantilla(self, registro_bruto):
        # Lógica para probar la plantilla con un registro bruto
        pass
    
class RegistroNormalizado(models.Model):
    fechaDoc = models.DateField(auto_now_add=True)
    rutEmisor = models.CharField(max_length=12)
    rutReceptor = models.CharField(max_length=12)
    neto = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    tipoDocumento = models.CharField(max_length=50)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)

    def doc_to_json(self):
        return {
            "fechaDoc": self.fechaDoc,
            "rutEmisor": self.rutEmisor,
            "rutReceptor": self.rutReceptor,
            "neto": str(self.neto),
            "iva": str(self.iva),
            "total": str(self.total),
            "tipoDocumento": self.tipoDocumento,
        }
    
class Regla(models.Model):
    tipos = (('validacion', 'Validación'), ('negocio', 'Negocio'))
    tipos_severidad = (('info', 'Info'), ('warning', 'Warning'), ('error', 'Error'))
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=tipos)
    expresion = models.CharField(max_length=500)
    severidad = models.CharField(max_length=50, choices=tipos_severidad)
    activo = models.BooleanField(default=True)

    def aplicar(self, registro_normalizado): 
        # Lógica para ejecutar la regla sobre un registro normalizado
        pass  
    
class ResultadoRegla(models.Model):
    estados = (('ok', 'OK'), ('warning', 'Warning'), ('error', 'Error'))
    detalle = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    registroNormalizado = models.ForeignKey(RegistroNormalizado, on_delete=models.CASCADE)
    regla = models.ForeignKey(Regla, on_delete=models.CASCADE)


class Calificacion(models.Model):
    ESTADOS = (
        ('borrador', 'Borrador'),
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    )
    
    ORIGENES = (
        ('manual', 'Manual'),
        ('sistema', 'Sistema'),
        ('carga_masiva', 'Carga Masiva'),
    )
    
    # Información básica
    ejercicio = models.IntegerField(verbose_name="Año/Ejercicio")
    mercado = models.CharField(max_length=50, verbose_name="Mercado", default="AC")
    instrumento = models.CharField(max_length=100, verbose_name="Instrumento")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    # Fechas y eventos
    fecha_pago = models.DateField(verbose_name="Fecha de Pago", default=None)
    secuencia_evento = models.CharField(max_length=50, verbose_name="Secuencia de Evento")
    evento_capital = models.CharField(max_length=100, blank=True, verbose_name="Evento de Capital")
    
    # Valores principales
    valor_historico = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor Histórico"
    )
    dividendo = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name="Dividendo"
    )
    
    # Factores tributarios (Factor 8 al 37) - Almacenados en JSON
    factores = models.JSONField(
        default=dict,
        verbose_name="Factores Tributarios",
        help_text="Diccionario con factores del 8 al 37"
    )
    
    # Factores calculados (si aplica)
    factores_calculados = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Factores Calculados",
        help_text="Resultado de cálculos automáticos"
    )
    
    # Metadatos
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    origen = models.CharField(max_length=20, choices=ORIGENES, default='manual')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Relaciones
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='calificaciones_creadas',
        default=None
    )
    registro_normalizado = models.ForeignKey(
        'RegistroNormalizado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Registro Normalizado Origen"
    )
    lote_carga = models.ForeignKey(
        'LoteCarga',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Lote de Carga Origen"
    )
    
    # Observaciones y validaciones
    observaciones = models.TextField(blank=True, verbose_name="Observaciones")
    errores_validacion = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Errores de Validación"
    )
    
    class Meta:
        verbose_name = "Calificación Tributaria"
        verbose_name_plural = "Calificaciones Tributarias"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['ejercicio', 'mercado']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha_pago']),
        ]
    
    def __str__(self):
        return f"{self.ejercicio} - {self.instrumento} - {self.descripcion[:30]}"
    
    def calcular_factores_automaticos(self):
        """
        Calcula factores automáticamente basándose en la fórmula:
        Factor_N_calculado = Factor_N / SUMA(Factor_8 a Factor_19)
        """
        try:
            # Factores del 8 al 19 para el denominador
            factores_base = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
            
            # Calcular suma del denominador
            suma_base = sum(
                float(self.factores.get(f'factor_{i}', 0)) 
                for i in factores_base
            )
            
            if suma_base == 0:
                self.errores_validacion.append({
                    'tipo': 'calculo',
                    'mensaje': 'La suma de factores base es 0, no se pueden calcular proporciones'
                })
                return
            
            # Calcular cada factor
            factores_calc = {}
            for i in range(8, 38):  # Factor 8 al 37
                factor_key = f'factor_{i}'
                valor_factor = float(self.factores.get(factor_key, 0))
                factores_calc[factor_key] = round(valor_factor / suma_base, 8)
            
            self.factores_calculados = factores_calc
            
        except Exception as e:
            self.errores_validacion.append({
                'tipo': 'error_calculo',
                'mensaje': str(e)
            })
    
    def validar_coherencia(self):
        errores = []
        
        # Validar que ejercicio sea razonable
        from datetime import datetime
        if self.ejercicio < 2000 or self.ejercicio > datetime.now().year + 1:
            errores.append({
                'campo': 'ejercicio',
                'mensaje': f'Ejercicio {self.ejercicio} fuera de rango válido'
            })
        
        # Validar valores no negativos
        if self.valor_historico < 0:
            errores.append({
                'campo': 'valor_historico',
                'mensaje': 'El valor histórico no puede ser negativo'
            })
        
        if self.dividendo < 0:
            errores.append({
                'campo': 'dividendo',
                'mensaje': 'El dividendo no puede ser negativo'
            })
        
        # Validar factores
        for i in range(8, 38):
            factor_key = f'factor_{i}'
            if factor_key in self.factores:
                try:
                    valor = float(self.factores[factor_key])
                    if valor < 0:
                        errores.append({
                            'campo': factor_key,
                            'mensaje': f'{factor_key} no puede ser negativo'
                        })
                except (ValueError, TypeError):
                    errores.append({
                        'campo': factor_key,
                        'mensaje': f'{factor_key} no tiene un valor numérico válido'
                    })
        
        self.errores_validacion = errores
        return len(errores) == 0
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones y cálculos"""
        # Validar coherencia
        self.validar_coherencia()
        
        # Si no hay errores críticos, calcular factores
        if not any(e.get('tipo') == 'error' for e in self.errores_validacion):
            self.calcular_factores_automaticos()
        
        # Si hay errores, marcar estado como error
        if self.errores_validacion and self.estado == 'completado':
            self.estado = 'error'
        
        super().save(*args, **kwargs)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON/API"""
        return {
            'id': self.id,
            'ejercicio': self.ejercicio,
            'mercado': self.mercado,
            'instrumento': self.instrumento,
            'descripcion': self.descripcion,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'secuencia_evento': self.secuencia_evento,
            'valor_historico': str(self.valor_historico),
            'dividendo': str(self.dividendo),
            'factores': self.factores,
            'factores_calculados': self.factores_calculados,
            'estado': self.estado,
            'origen': self.origen,
        }

class HistorialCalificacion(models.Model):
    calificacion = models.ForeignKey(
        Calificacion,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=50)  # 'creacion', 'modificacion', 'calculo'
    cambios = models.JSONField(default=dict)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Calificación"
        verbose_name_plural = "Historiales de Calificaciones"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.calificacion} - {self.accion} - {self.fecha}"

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    mensaje = models.TextField()
    nivel = models.CharField(max_length=50)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)  