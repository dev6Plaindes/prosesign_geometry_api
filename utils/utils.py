from fastapi.encoders import jsonable_encoder
import pandas as pd
import numpy as np

def preparar_df_para_api(df_global):
    """
    Convierte geometrías de Shapely y objetos complejos en 
    formatos serializables. Maneja tanto DataFrames como Listas.
    """
    # 1. Validar si recibimos una lista (ya procesada)
    if isinstance(df_global, list):
        # Si la lista ya tiene diccionarios, solo aseguramos compatibilidad JSON
        return jsonable_encoder(df_global)

    # 2. Si es DataFrame, validar que no esté vacío
    if df_global is None or (hasattr(df_global, 'empty') and df_global.empty):
        return []

    # 3. Procesamiento si es un DataFrame original
    df_api = df_global.copy()

    # Convertir Polígonos a Listas de Coordenadas (geometria_mundo)
    if "geometria_mundo" in df_api.columns:
        df_api["geometria_mundo"] = df_api["geometria_mundo"].apply(
            lambda p: list(p.exterior.coords) if hasattr(p, 'exterior') and not p.is_empty else p
        )

    # Convertir Geometría local
    if "geometria" in df_api.columns:
        df_api["geometria"] = df_api["geometria"].apply(
            lambda p: list(p.exterior.coords) if hasattr(p, 'exterior') else p
        )

    # Limpiar columnas no serializables
    columnas_a_quitar = ["instancia_zona", "instancia_terreno"]
    for col in columnas_a_quitar:
        if col in df_api.columns:
            df_api = df_api.drop(columns=[col])

    # IMPORTANTE: Reemplazar NaNs por None para evitar el error "nan is not JSON compliant"
    df_api = df_api.replace({np.nan: None})

    # 4. Convertir a lista de diccionarios
    datos_dict = df_api.to_dict(orient="records")
    
    return jsonable_encoder(datos_dict)