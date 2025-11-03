import os
import django, sys

# Configura el entorno Django
# Ruta absoluta al directorio donde está manage.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuam_proyecto.settings')
django.setup()
from app_nuam.models import Plantilla

Plantilla.objects.create(
    nombre="Plantilla genérica dividendos",
    version="1.0",
    tipo_mercado="ACCIONES",
    origen_informacion="CORREDORA",
    periodo_comercial=202501,
    mappingJson={
        "ejercicio": "EJERCICIO",
        "instrumento": "INSTRUMENTO",
        "fecha_pago_dividendo": "FECHA_DIV",
        "descripcion_dividendo": "DESC_DIV",
        "secuencia_evento": "SEQ_EVT",
        "acogido_isfut": "ISFUT",
        "origen": "ORIGEN_DATOS",
        "factor_actualizacion": "FACT_ACT"
    },
    factoresJson={
        "factor8": "FACT_08",
        "factor9": "FACT_09",
        "factor10": "FACT_10",
        # etc. hasta el 37
    },
    descripcion={"detalle": "Plantilla genérica para dividendos"}
)
