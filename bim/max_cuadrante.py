import json

import pandas as pd
from shapely import affinity
import numpy as np
from shapely.geometry import box, Polygon
from rasterio import features
from affine import Affine

# 🔷 1. Max rectangle en matriz binaria
def maximal_rectangle(matrix):
    if not matrix.any():
        return 0, (0, 0, 0, 0)

    max_area = 0
    max_rect = (0, 0, 0, 0)
    dp = [0] * len(matrix[0])

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            dp[j] = dp[j] + 1 if matrix[i][j] == 1 else 0

        stack = []
        for j in range(len(dp) + 1):
            while stack and (j == len(dp) or dp[j] < dp[stack[-1]]):
                height = dp[stack.pop()]
                width = j if not stack else j - stack[-1] - 1
                area = height * width

                if area > max_area:
                    max_area = area
                    top_left_j = stack[-1] + 1 if stack else 0
                    top_left_i = i - height + 1
                    max_rect = (top_left_i, top_left_j, height, width)

            stack.append(j)

    return max_area, max_rect

# 🔷 2. Obtener ángulos candidatos (OPTIMIZACIÓN 🔥)
def get_candidate_angles(polygon):
    angles = set()
    
    # 1. Normalizar la entrada: si es MultiPolygon sacamos sus partes, si es Polygon lo envolvemos en una lista
    if polygon.geom_type == 'MultiPolygon':
        polygons_to_process = list(polygon.geoms)
    elif polygon.geom_type == 'Polygon':
        polygons_to_process = [polygon]
    else:
        return []

    # 2. Iterar sobre cada polígono/fragmento del terreno
    for poly in polygons_to_process:
        if poly.is_empty:
            continue
            
        coords = list(poly.exterior.coords)

        # 3. Tu lógica original aplicada a los lados de cada fragmento
        for i in range(len(coords) - 1):
            dx = coords[i+1][0] - coords[i][0]
            dy = coords[i+1][1] - coords[i][1]
            angle = np.degrees(np.arctan2(dy, dx))
            angles.add(round(angle % 180, 2))

    return sorted(angles)

# 🔷 3. Evaluar un ángulo
def find_max_rect_for_angle(polygon, angle_deg, cell_size=0.4):
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    origin = ((minx + maxx) / 2, (miny + maxy) / 2)

    # Rotar polígono
    poly_rotated = affinity.rotate(polygon.buffer(-0.01), -angle_deg, origin=origin)

    rminx, rminy, rmaxx, rmaxy = poly_rotated.bounds
    width = int(np.ceil((rmaxx - rminx) / cell_size))
    height = int(np.ceil((rmaxy - rminy) / cell_size))

    if width <= 0 or height <= 0:
        return None, 0

    transform = Affine.translation(rminx, rminy) * Affine.scale(cell_size, cell_size)

    grid = features.rasterize(
        [poly_rotated],
        out_shape=(height, width),
        transform=transform,
        fill=0,
        default_value=1,
        dtype=np.uint8
    )

    area_px, (i_start, j_start, h_px, w_px) = maximal_rectangle(grid)

    if area_px == 0:
        return None, 0

    x0 = j_start * cell_size + rminx
    x1 = (j_start + w_px) * cell_size + rminx
    y0 = i_start * cell_size + rminy
    y1 = (i_start + h_px) * cell_size + rminy

    rect = box(x0, y0, x1, y1)

    # Rotar de vuelta
    rect_final = affinity.rotate(rect, angle_deg, origin=origin)

    area_m2 = area_px * (cell_size ** 2)

    return rect_final, area_m2

# 🔷 4. FUNCIÓN PRINCIPAL (MEJORADA 🚀)
def find_best_rectangle(polygon, cell_size_coarse=0.5, cell_size_fine=0.2):
    best_rect = None
    best_area = 0
    best_angle = 0

    # 🔥 ángulos inteligentes
    base_angles = get_candidate_angles(polygon)

    # 🔥 refinamiento fino
    angles = []
    for a in base_angles:
        angles.extend([a + d for d in np.linspace(-3, 3, 7)])

    # --- PRIMERA PASADA (rápida) ---
    for angle in angles:
        rect, area = find_max_rect_for_angle(polygon, angle, cell_size_coarse)

        if rect and area > best_area:
            best_rect = rect
            best_area = area
            best_angle = angle

    # --- SEGUNDA PASADA (precisa 🔥) ---
    fine_angles = [best_angle + d for d in np.linspace(-1, 1, 5)]

    for angle in fine_angles:
        rect, area = find_max_rect_for_angle(polygon, angle, cell_size_fine)

        if rect and area > best_area:
            best_rect = rect
            best_area = area
            best_angle = angle

    return best_rect, best_area, best_angle

def find_next_best_rectangle(polygon, previous_rect, cell_size_coarse=0.5, cell_size_fine=0.2):
    """
    Busca el siguiente mejor rectángulo máximo en el terreno, 
    excluyendo el área del cuadrante máximo ya encontrado.
    """
    # 1. Restar el rectángulo anterior al terreno original
    # (previous_rect debe ser un objeto Polygon de Shapely)
    remaining_terrain = polygon.difference(previous_rect)
    
    # Valida que quede terreno útil para buscar
    if remaining_terrain.is_empty:
        print("No queda terreno disponible.")
        return None, 0, 0

    best_rect = None
    best_area = 0
    best_angle = 0

    # 🔥 ángulos inteligentes basados en el terreno restante
    base_angles = get_candidate_angles(remaining_terrain)

    # 🔥 refinamiento fino de ángulos
    angles = []
    for a in base_angles:
        angles.extend([a + d for d in np.linspace(-3, 3, 7)])

    # --- PRIMERA PASADA (rápida) ---
    for angle in angles:
        # Buscamos en 'remaining_terrain' en lugar del polígono original
        rect, area = find_max_rect_for_angle(remaining_terrain, angle, cell_size_coarse)

        if rect and area > best_area:
            best_rect = rect
            best_area = area
            best_angle = angle

    # --- SEGUNDA PASADA (precisa 🔥) ---
    if best_rect:  # Solo si se encontró algo en la primera pasada
        fine_angles = [best_angle + d for d in np.linspace(-1, 1, 5)]

        for angle in fine_angles:
            rect, area = find_max_rect_for_angle(remaining_terrain, angle, cell_size_fine)

            if rect and area > best_area:
                best_rect = rect
                best_area = area
                best_angle = angle

    return best_rect, best_area, best_angle

def normalizar_polygon(vertices):
    """
    Convierte coordenadas grandes (UTM) a un sistema local cercano a (0,0)
    sin alterar la forma del polígono.
    """

    poly = Polygon(vertices)

    # 🔥 usar esquina inferior izquierda como referencia
    minx, miny, _, _ = poly.bounds

    # trasladar al origen
    poly_normalizado = affinity.translate(poly, xoff=-minx, yoff=-miny)

    return poly_normalizado



def polygon_get_data(rect):
    """
    Solo formatea el resultado ya calculado (rect, area, angle)
    al formato de get_data()
    """

    if rect is None:
        return pd.DataFrame()

    minx, miny, maxx, maxy = rect.bounds

    ancho = maxx - minx
    largo = maxy - miny

    return pd.DataFrame({
        "ancho": [ancho],
        "largo": [largo],
        # "area": [area],
        # "description": [f"max_rect_{angle:.2f}deg"],
        "geometria": [rect],
        "x": [minx],
        "y": [miny],
        "tipo": ["max_rect"],
        "piso": [1]
    })
    

def df_geom_to_dict(df):
    # 1. Copia para no afectar el original
    temp_df = df.copy()
    
    # 2. Convertir geometría a WKT de forma vectorizada (más rápido)
    if "geometria" in temp_df.columns:
        temp_df["geometria"] = temp_df["geometria"].apply(
            lambda x: x.wkt if hasattr(x, "wkt") else None
        )
    
    # 3. La "vieja confiable": Pasar por JSON para limpiar tipos de NumPy
    # Esto convierte int64 -> int, float64 -> float y NaN -> null automáticamente
    return json.loads(temp_df.to_json(orient="records"))
