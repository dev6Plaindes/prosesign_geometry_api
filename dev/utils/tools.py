from typing import List, Union, Optional
from shapely.geometry import Polygon, box
from shapely import affinity
import math

def div_logic(
    medidas: List[Union[int, float, str]], 
    polygon: Polygon, 
    eje_div: str = "x"
) -> List[Polygon]:
    """
    Divide un polígono (cuadrante inclinado) en sub-polígonos (tramos) siguiendo 
    una lista de medidas fijas y/o automáticas ("auto") a lo largo de un eje.
    
    Parámetros:
        - medidas: List, ejemplo [5, "auto", 5]
        - polygon: Objeto Polygon de Shapely del cuadrante (puede estar rotado).
        - eje_div: str, "x" para cortes a lo largo del largo (verticales) 
                       o "y" para cortes a lo largo del ancho (horizontales).
                       
    Retorna:
        - List[Polygon]: Una lista de objetos Polygon de Shapely correspondientes 
                         a cada división, perfectamente orientados.
    """
    # =========================================================================
    # 1. DETECTAR ÁNGULO DE INCLINACIÓN
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    # Calculamos el ángulo en radianes y luego a grados respecto al eje X horizontal
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    
    # Para evitar comportamientos extraños si los vértices vienen en sentido inverso, 
    # forzamos que esté en un rango controlable.
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # =========================================================================
    # 2. ALINEAR TEMPORALMENTE EL POLÍGONO A 0°
    # =========================================================================
    pivote = polygon.centroid
    # Rotamos en sentido contrario para alinearlo plano
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote)
    
    # Obtenemos los límites del polígono alineado
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_total = max_x - min_x
    ancho_total = max_y - min_y
    
    # Determinar qué dimensión vamos a dividir
    medida_total = largo_total if eje_div.lower() == "x" else ancho_total
    offset_inicial = min_x if eje_div.lower() == "x" else min_y

    # =========================================================================
    # 3. LÓGICA DE DIVISIÓN DE MEDIDAS (Tus cálculos originales)
    # =========================================================================
    suma_fijos = sum(m for m in medidas if isinstance(m, (int, float)))
    if suma_fijos > medida_total:
        print("⚠️ Advertencia: Las medidas fijas superan la longitud total disponible.")
        return []

    cantidad_auto = medidas.count("auto")
    valor_auto = (medida_total - suma_fijos) / cantidad_auto if cantidad_auto > 0 else 0
    medidas_resueltas = [valor_auto if m == "auto" else m for m in medidas]

    # =========================================================================
    # 4. CREAR SUB-POLÍGONOS EN EL ESTADO PLANO (ALINEADO)
    # =========================================================================
    sub_poligonos_alineados = []
    coordenada_actual = offset_inicial

    for paso in medidas_resueltas:
        coordenada_siguiente = coordenada_actual + paso
        
        if eje_div.lower() == "x":
            # Si dividimos en X, el tramo va de coord_actual a coord_siguiente en X,
            # y ocupa todo el ancho disponible en Y (de min_y a max_y).
            sub_box = box(coordenada_actual, min_y, coordenada_siguiente, max_y)
        else:
            # Si dividimos en Y, el tramo va de coord_actual a coord_siguiente en Y,
            # y ocupa todo el largo disponible en X (de min_x a max_x).
            sub_box = box(min_x, coordenada_actual, max_x, coordenada_siguiente)
            
        sub_poligonos_alineados.append(sub_box)
        coordenada_actual = coordenada_siguiente

    # =========================================================================
    # 5. ROTAR DE VUELTA LOS TRAMOS AL ÁNGULO ORIGINAL
    # =========================================================================
    sub_poligonos_finales = []
    for sub_poly in sub_poligonos_alineados:
        # Rotamos de vuelta al ángulo original usando el mismo pivote
        sub_poly_rotado = affinity.rotate(sub_poly, angulo_grados, origin=pivote)
        sub_poligonos_finales.append(sub_poly_rotado)

    return sub_poligonos_finales


def div_logic_with_spacing(
    medidas: List[Union[int, float, str]], 
    polygon: Polygon, 
    eje_div: str = "x",
    gap: float = 0.3,
    padding: float = 0.3
) -> List[Polygon]:
    """
    Divide un polígono inclinado en sub-polígonos aplicando un padding general
    a la zona de trabajo y un gap entre las divisiones creadas.
    
    Parámetros:
        - medidas: List, ejemplo [5, "auto", 5]
        - polygon: Objeto Polygon de Shapely del cuadrante.
        - eje_div: str, "x" para divisiones verticales, "y" para horizontales.
        - gap: float, espacio de separación entre tramos adyacentes.
        - padding: float, espacio de margen interno en los 4 bordes del polígono.
    """
    # =========================================================================
    # 1. DETECTAR ÁNGULO DE INCLINACIÓN
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # =========================================================================
    # 2. ALINEAR TEMPORALMENTE EL POLÍGONO A 0°
    # =========================================================================
    pivote = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote)
    
    # Límites originales en plano
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    
    # =========================================================================
    # 3. APLICAR PADDING (Reducir el área útil de trabajo)
    # =========================================================================
    # Si el padding supera las dimensiones físicas del polígono, cancelamos.
    if (2 * padding) >= (max_x - min_x) or (2 * padding) >= (max_y - min_y):
        print("⚠️ Advertencia: El padding es demasiado grande para las dimensiones del polígono.")
        return []
        
    min_x_util = min_x + padding
    max_x_util = max_x - padding
    min_y_util = min_y + padding
    max_y_util = max_y - padding
    
    largo_util = max_x_util - min_x_util
    ancho_util = max_y_util - min_y_util
    
    medida_total_util = largo_util if eje_div.lower() == "x" else ancho_util
    offset_inicial = min_x_util if eje_div.lower() == "x" else min_y_util

    # =========================================================================
    # 4. CONSIDERAR GAPS EN LA LÓGICA DE DIVISIONES
    # =========================================================================
    # Si tenemos N tramos, habrá N-1 gaps.
    num_tramos = len(medidas)
    gaps_totales = (num_tramos - 1) * gap if num_tramos > 1 else 0.0
    
    # El espacio disponible real para distribuir las medidas disminuye por los gaps
    espacio_disponible_para_medidas = medida_total_util - gaps_totales
    
    suma_fijos = sum(m for m in medidas if isinstance(m, (int, float)))
    if (suma_fijos + gaps_totales) > medida_total_util:
        print("⚠️ Advertencia: Las medidas fijas + los gaps superan la longitud útil disponible.")
        return []

    cantidad_auto = medidas.count("auto")
    valor_auto = (espacio_disponible_para_medidas - suma_fijos) / cantidad_auto if cantidad_auto > 0 else 0
    medidas_resueltas = [valor_auto if m == "auto" else m for m in medidas]

    # =========================================================================
    # 5. CREAR SUB-POLÍGONOS EN EL ESTADO PLANO (CON GAPS)
    # =========================================================================
    sub_poligonos_alineados = []
    coordenada_actual = offset_inicial

    for idx, paso in enumerate(medidas_resueltas):
        coordenada_siguiente = coordenada_actual + paso
        
        if eje_div.lower() == "x":
            # Ocupa el alto útil (ajustado por el padding en Y)
            sub_box = box(coordenada_actual, min_y_util, coordenada_siguiente, max_y_util)
        else:
            # Ocupa el largo útil (ajustado por el padding en X)
            sub_box = box(min_x_util, coordenada_actual, max_x_util, coordenada_siguiente)
            
        sub_poligonos_alineados.append(sub_box)
        
        # Al movernos al siguiente tramo, le sumamos el tamaño del gap
        coordenada_actual = coordenada_siguiente + gap

    # =========================================================================
    # 6. ROTAR DE VUELTA LOS TRAMOS AL ÁNGULO ORIGINAL
    # =========================================================================
    sub_poligonos_finales = []
    for sub_poly in sub_poligonos_alineados:
        sub_poly_rotado = affinity.rotate(sub_poly, angulo_grados, origin=pivote)
        sub_poligonos_finales.append(sub_poly_rotado)

    return sub_poligonos_finales




def obtener_sub_polygon_centrado(
    polygon: Polygon, 
    largo: float, 
    ancho: float
) -> Optional[Polygon]:
    """
    Crea un sub-polígono con un largo y ancho específicos, centrado tanto 
    horizontal como verticalmente dentro del polígono contenedor (incluso si está inclinado).
    
    Parámetros:
        - polygon: Objeto Polygon de Shapely contenedor (puede estar rotado).
        - largo: Longitud del nuevo polígono (en el eje X del polígono alineado).
        - ancho: Ancho del nuevo polígono (en el eje Y del polígono alineado).
        
    Retorna:
        - Polygon: El sub-polígono perfectamente centrado y orientado, o None si no cabe.
    """
    # =========================================================================
    # 1. DETECTAR ÁNGULO DE INCLINACIÓN
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # =========================================================================
    # 2. ALINEAR TEMPORALMENTE EL POLÍGONO A 0°
    # =========================================================================
    pivote = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote)
    
    # Obtenemos los límites y dimensiones del polígono contenedor alineado
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_contenedor = max_x - min_x
    ancho_contenedor = max_y - min_y
    
    # Validamos que el sub-polígono quepa en el contenedor
    if largo > largo_contenedor or ancho > ancho_contenedor:
        print("⚠️ Advertencia: Las dimensiones solicitadas superan el tamaño del polígono contenedor.")
        return None

    # =========================================================================
    # 3. CALCULAR CENTRO Y NUEVAS COORDENADAS PLANAS
    # =========================================================================
    # Encontramos el centro geométrico del contenedor alineado
    centro_x = (min_x + max_x) / 2
    centro_y = (min_y + max_y) / 2
    
    # Calculamos los límites de la nueva caja centrada
    sub_min_x = centro_x - (largo / 2)
    sub_max_x = centro_x + (largo / 2)
    sub_min_y = centro_y - (ancho / 2)
    sub_max_y = centro_y + (ancho / 2)
    
    # Creamos el box alineado
    sub_box_alineado = box(sub_min_x, sub_min_y, sub_max_x, sub_max_y)

    # =========================================================================
    # 4. ROTAR DE VUELTA AL ÁNGULO ORIGINAL
    # =========================================================================
    sub_polygon_final = affinity.rotate(sub_box_alineado, angulo_grados, origin=pivote)

    return sub_polygon_final