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
    nombre="Plantilla generica dividendos",
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
        "factor11": "FACT_11",
        "factor12": "FACT_12",
        "factor13": "FACT_13",
        "factor14": "FACT_14",
        "factor15": "FACT_15",
        "factor16": "FACT_16",
        "factor17": "FACT_17",
        "factor18": "FACT_18",
        "factor19": "FACT_19",
        "factor20": "FACT_20",
        "factor21": "FACT_21",
        "factor22": "FACT_22",
        "factor23": "FACT_23",
        "factor24": "FACT_24",
        "factor25": "FACT_25",
        "factor26": "FACT_26",
        "factor27": "FACT_27",
        "factor28": "FACT_28",
        "factor29": "FACT_29",
        "factor30": "FACT_30",
        "factor31": "FACT_31",
        "factor32": "FACT_32",
        "factor33": "FACT_33",
        "factor34": "FACT_34",
        "factor35": "FACT_35",
        "factor36": "FACT_36",
        "factor37": "FACT_37"
    },
    descripcion={"detalle": "Plantilla genérica para dividendos"}
)
