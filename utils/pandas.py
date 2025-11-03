import pandas as pd, json
from app_nuam.models import Archivo, RegistroBruto
from PyPDF2 import PdfReader
import os
import numpy as np

def procesar_archivo(archivo: Archivo):
    ruta = archivo.archivo.path
    extension = os.path.splitext(ruta)[1].lower()
    
    try:
        if extension in ['.xls', '.xlsx']:
            engine = 'openpyxl' if extension == '.xlsx' else 'xlrd'
            paginas_todas = pd.read_excel(ruta, sheet_name=None, engine=engine)

            datos = []
        
            for sheet_name, df in paginas_todas.items():
                df = df.replace({np.nan: None, np.inf: None, -np.inf: None})
                for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']):
                    df[col] = df[col].dt.strftime('%d-%m-%Y')
                datos.extend(df.to_dict(orient='records'))
            
            payload = {'tipo': 'excel', 'datos': datos}

        elif extension == '.csv':
            df = pd.read_csv(ruta)
            df = df.where(pd.notna(df), None)
            payload = {'tipo': 'csv', 'datos': df.to_dict(orient= 'records')}
            
        elif extension == '.pdf':
            reader = PdfReader(ruta)
            texto_total = ""
            for page in reader.pages:
                texto_total += page.extract_text() or ""
            payload= {'tipo': 'pdf', 'contenido_pdf': texto_total.strip()}
            
        else:
            raise ValueError(f"Tipo de archivo no soportado: {extension}")
        
        RegistroBruto.objects.create(
            payloadJson = payload,
            erroresJson = None,
            valido=True,
            archivo=archivo
        )
        
        archivo.estado = 'PROCESADO'
        archivo.save()
        
    except Exception as e:
        archivo.estado = 'error'
        archivo.save()
        print(f"Error procesando {archivo.nombre}: {e}")
        raise e