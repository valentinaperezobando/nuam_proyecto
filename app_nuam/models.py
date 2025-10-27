# Create your models here.
from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    
class Rol(models.Model):
    nombre = models.CharField(max_length=100)

class Permiso(models.Model):
    clave = models.CharField(max_length=100)

class Reporte(models.Models):
    tipo = models.CharField(max_length=100)
    periodo_inicio = models.DateField()
    periodo_fin = models.DateField()
    urlDescarga = models.URLField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def generar_reporte(self, criterios):
        # Lógica para generar el reporte basado en ciertos criterios
        pass

class Bitacora(models.Model):
    entidad = models.CharField(max_length=100)
    accion = models.CharField(max_length=100)
    antes = models.JSONField(null=True, blank=True)
    despues = models.JSONField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class LoteCarga(models.Models):
    estados = (('en proceso', 'En Proceso'), ('procesado', 'Procesado'), ('error', 'Error'))
    origen = models.CharField(max_length=100)
    estado = models.CharField(max_length=50, choices=estados, default='en proceso')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def validar_resumen(self):
        # Lógica para validar el resumen del lote de carga
        pass

class Archivo(models.Models):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30)
    hash = models.CharField(max_length=200)
    estado = models.CharField(max_length=50)
    lote_carga = models.ForeignKey(LoteCarga, on_delete=models.CASCADE)

class RegistroBruto(models.Models):
    payloadJson = models.JSONField()
    erroresJson = models.JSONField(null=True, blank=True)
    valido = models.BooleanField(default=False)
    archivo = models.ForeignKey(Archivo, on_delete=models.CASCADE)

class Plantilla(models.Models):
    nombre = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    mappingJson = models.JSONField()

    def probar_plantilla(self, registro_bruto):
        # Lógica para probar la plantilla con un registro bruto
        pass
    
class RegistroNormalizado(models.Models):
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
    
class Regla(models.Models):
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
    
class ResultadoRegla(models.Models):
    estados = (('ok', 'OK'), ('warning', 'Warning'), ('error', 'Error'))
    detalle = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    registroNormalizado = models.ForeignKey(RegistroNormalizado, on_delete=models.CASCADE)
    regla = models.ForeignKey(Regla, on_delete=models.CASCADE)


# VERSION A CORREGIR
class Calificacion(models.Models):
    objetoTipo = models.CharField(max_length=100)
    objetoId = models.IntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    label = models.CharField(max_length=100)
    motivos = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Notificacion(models.Models):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)
    mensaje = models.TextField()
    nivel = models.CharField(max_length=50)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)