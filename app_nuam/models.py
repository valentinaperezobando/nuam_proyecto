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
    mercado_choices = [
        ('ACCIONES', 'acciones'), ('CFI', 'CFI'), ('FONDOS_MUTUOS', 'Fondos_Mutuos')
    ]
    origen_choices = [
        ('CORREDORA', 'Corredora'), ('SISTEMA', 'Sistema')
    ]
    nombre = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    tipo_mercado = models.CharField(max_length=20, choices=mercado_choices)
    origen_informacion = models. CharField(max_length=20, choices=origen_choices)
    periodo_comercial = models.PositiveBigIntegerField()
    mappingJson = models.JSONField()
    factoresJson = models.JSONField(default=dict)
    descripcion = models.JSONField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def probar_plantilla(self, archivo):
        registros_bruto = RegistroBruto.objects.filter(archivo=archivo)
        resultados_preview = []
        
        for registro in registros_bruto:
            data = registro.payloadJson
            mapping = self.mappingJson
            factores = self.factoresJson
            
            for fila in data:
                normalizada = {}
                for clave_destino, clave_origen in mapping.items():
                    valor = fila.get(clave_origen)
                    #transforma segun factores Json
                    reglas = factores.get(clave_destino, {})
                    if 'factor' in reglas and isinstance(valor, (int, float)):
                        valor *= reglas['factor']
                    if 'formato' in reglas:
                        from datetime import datetime
                        try:
                            valor = datetime.strptime(valor, reglas["formato"]).strftime("%Y-%m-%d")
                        except Exception:
                            pass
                    normalizada[clave_destino] = valor
                resultados_preview.append(normalizada)
        return resultados_preview
    
class RegistroNormalizado(models.Model):
    plantilla = models.ForeignKey("Plantilla", on_delete=models.CASCADE)
    archivo = models.ForeignKey("Archivo", on_delete=models.CASCADE, null=True, blank=True)
    ejercicio = models.PositiveIntegerField(default=2025)
    instrumento = models.CharField(max_length=100)
    fecha_pago_dividendo = models.DateField()
    descripcion_dividendo = models.TextField()
    secuencia_evento = models.CharField(max_length=20)
    acogido_isfut = models.CharField(max_length=10, null=True, blank=True)
    origen = models.CharField(max_length=20)  # "CORREDORA" o "SISTEMA"
    factor_actualizacion = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    factores = models.JSONField(null=True, blank=True)  # { "factor8": x, "factor9": y, ... }

    def to_dict(self):
        return {
            "ejercicio": self.ejercicio,
            "instrumento": self.instrumento,
            "fecha_pago_dividendo": self.fecha_pago_dividendo.strftime("%d-%m-%Y"),
            "descripcion_dividendo": self.descripcion_dividendo,
            "secuencia_evento": self.secuencia_evento,
            "acogido_isfut": self.acogido_isfut,
            "origen": self.origen,
            "factor_actualizacion": str(self.factor_actualizacion),
            "factores": self.factores,
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


# VERSION A CORREGIR
class Calificacion(models.Model):
    objetoTipo = models.CharField(max_length=100)
    objetoId = models.IntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    label = models.CharField(max_length=100)
    motivos = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    mensaje = models.TextField()
    nivel = models.CharField(max_length=50)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)  