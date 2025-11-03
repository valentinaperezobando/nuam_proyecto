import pandas as pd, json
from app_nuam.models import Archivo, RegistroBruto
from PyPDF2 import PdfReader
import os
import numpy as np
import datetime

# Helper para convertir todo a tipos serializables JSON
def limpiar_json(obj):
    if isinstance(obj, (datetime.datetime, datetime.date, pd.Timestamp)):
        return obj.strftime("%d-%m-%Y")
    elif isinstance(obj, dict):
        return {k: limpiar_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [limpiar_json(i) for i in obj]
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj
