from shapely.geometry import mapping
import pandas as pd
import numpy as np
from shapely.geometry import shape
from shapely import affinity

def preparar_df_para_api(df: pd.DataFrame) -> list:
    df_serializado = df.copy()

    # 🔥 1. Reemplazar NaN por None (CLAVE)
    df_serializado = df_serializado.replace({np.nan: None})

    # 🔷 2. Serializar geometrías
    columnas_geom = [
        "geometria",
        "geometria_marco",
        "geometria_hoja",
        "geometria_arco"
    ]

    for col in columnas_geom:
        if col in df_serializado.columns:
            df_serializado[col] = df_serializado[col].apply(
                lambda g: mapping(g) if g is not None else None
            )

    # 🔁 3. Convertir a JSON-ready
    return df_serializado.to_dict(orient="records")


def reconstruir_geometria(geojson):
    if geojson is None:
        return None
    return shape(geojson)  # 👈 convierte GeoJSON → Shapely


def vertices_a_dataframe(vertices: list) -> pd.DataFrame:
    df = pd.DataFrame(vertices)

    # 🔁 Convertir geometría
    if "geometria" in df.columns:
        df["geometria"] = df["geometria"].apply(reconstruir_geometria)

    # (opcional) si tienes más geometrías
    columnas_geom = ["geometria_marco", "geometria_hoja", "geometria_arco"]

    for col in columnas_geom:
        if col in df.columns:
            df[col] = df[col].apply(reconstruir_geometria)

    return df



def restaurar_plano(df_plano, df_cuadrante_real, best_angle):

    df = df_plano.copy()

    g_rect = df_cuadrante_real.iloc[0]["geometria"]

    cx_rect = g_rect.centroid.x
    cy_rect = g_rect.centroid.y

    largo = df_cuadrante_real.iloc[0]["largo"]
    ancho = df_cuadrante_real.iloc[0]["ancho"]

    ang = np.radians(best_angle)

    cos = np.cos(ang)
    sin = np.sin(ang)

    # vectores de orientación
    vx = cos
    vy = sin

    px = -sin
    py = cos

    # corregir media dimensión
    xoff = cx_rect - vx*largo/2 - px*ancho/2
    yoff = cy_rect - vy*largo/2 - py*ancho/2

    a = cos
    b = -sin
    d = sin
    e = cos

    geoms = []

    for g in df["geometria"]:

        g2 = affinity.affine_transform(
            g,
            [a, b, d, e, xoff, yoff]
        )

        geoms.append(g2)

    df["geometria"] = geoms
    df["x"] = df["geometria"].apply(lambda g: g.centroid.x)
    df["y"] = df["geometria"].apply(lambda g: g.centroid.y)

    return df