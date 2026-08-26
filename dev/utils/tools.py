from typing import List, Union, Optional
from shapely.geometry import Polygon, box
from shapely import affinity
import math

from typing import List, Union
from shapely.geometry import Polygon, LineString
from shapely.ops import split
import math


def div_logic(
    medidas: List[Union[int, float, str]],
    polygon: Polygon,
    eje_div: str = "x"
) -> List[Polygon]:

    if polygon is None or polygon.is_empty:
        return []

    # ============================================================
    # 1. OBTENER ORIENTACIÓN DEL POLYGON
    # ============================================================

    coords = list(polygon.exterior.coords)

    p0 = coords[0]
    p1 = coords[1]

    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]

    angulo = math.atan2(dy, dx)

    # Vector unitario X local
    ux = math.cos(angulo)
    uy = math.sin(angulo)

    # Vector unitario Y local
    vx = -uy
    vy = ux

    # ============================================================
    # 2. CENTRO DEL POLYGON
    # ============================================================

    centro = polygon.centroid

    # ============================================================
    # 3. PROYECTAR LOS VÉRTICES SOBRE LOS EJES LOCALES
    # ============================================================

    valores_x = []
    valores_y = []

    for x, y in coords[:-1]:

        dxp = x - centro.x
        dyp = y - centro.y

        local_x = dxp * ux + dyp * uy
        local_y = dxp * vx + dyp * vy

        valores_x.append(local_x)
        valores_y.append(local_y)

    min_x = min(valores_x)
    max_x = max(valores_x)

    min_y = min(valores_y)
    max_y = max(valores_y)

    largo = max_x - min_x
    ancho = max_y - min_y

    # ============================================================
    # 4. DETERMINAR EJE DE DIVISIÓN
    # ============================================================

    es_x = eje_div.lower() == "x"

    medida_total = largo if es_x else ancho

    # ============================================================
    # 5. RESOLVER MEDIDAS
    # ============================================================

    suma_fijos = sum(
        m for m in medidas
        if isinstance(m, (int, float))
    )

    cantidad_auto = medidas.count("auto")

    if suma_fijos > medida_total:
        print(
            f"⚠️ Las medidas ({suma_fijos}) "
            f"superan la longitud disponible ({medida_total:.2f})"
        )
        return []

    valor_auto = (
        (medida_total - suma_fijos) / cantidad_auto
        if cantidad_auto > 0
        else 0
    )

    medidas_resueltas = [
        valor_auto if m == "auto" else float(m)
        for m in medidas
    ]

    # ============================================================
    # 6. POSICIÓN INICIAL
    # ============================================================

    coordenada_actual = -medida_total / 2

    # ============================================================
    # 7. CREAR CORTES
    # ============================================================

    resultado = [polygon]

    for paso in medidas_resueltas:

        coordenada_actual += paso

        # No crear corte después del último tramo
        if coordenada_actual >= medida_total / 2:
            break

        # ========================================================
        # POSICIÓN DEL CORTE EN COORDENADAS GLOBALES
        # ========================================================

        if es_x:

            # Punto sobre el eje X local
            px = centro.x + coordenada_actual * ux
            py = centro.y + coordenada_actual * uy

            # Dirección de la línea = Y local
            lx = vx
            ly = vy

        else:

            # Punto sobre el eje Y local
            px = centro.x + coordenada_actual * vx
            py = centro.y + coordenada_actual * vy

            # Dirección de la línea = X local
            lx = ux
            ly = uy

        # ========================================================
        # CREAR UNA LÍNEA MUY LARGA QUE ATRAVIESE EL POLYGON
        # ========================================================

        longitud_linea = max(largo, ancho) * 10 + 100

        p_inicio = (
            px - lx * longitud_linea,
            py - ly * longitud_linea
        )

        p_fin = (
            px + lx * longitud_linea,
            py + ly * longitud_linea
        )

        linea_corte = LineString([
            p_inicio,
            p_fin
        ])

        # ========================================================
        # SHAPELY HACE EL SPLIT
        # ========================================================

        nuevo_resultado = []

        for pieza in resultado:

            partes = split(
                pieza,
                linea_corte
            )

            nuevo_resultado.extend(
                geom
                for geom in partes.geoms
                if not geom.is_empty
            )

        resultado = nuevo_resultado

    return resultado

def div_logic_with_spacing(
    medidas: List[Union[int, float, str]],
    polygon: Polygon,
    eje_div: str = "x",
    gap: float = 0.3,
    padding: float = 0.3,
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
        print(
            "⚠️ Advertencia: El padding es demasiado grande para las dimensiones del polígono."
        )
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
        print(
            "⚠️ Advertencia: Las medidas fijas + los gaps superan la longitud útil disponible."
        )
        return []

    cantidad_auto = medidas.count("auto")
    valor_auto = (
        (espacio_disponible_para_medidas - suma_fijos) / cantidad_auto
        if cantidad_auto > 0
        else 0
    )
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
            sub_box = box(
                coordenada_actual, min_y_util, coordenada_siguiente, max_y_util
            )
        else:
            # Ocupa el largo útil (ajustado por el padding en X)
            sub_box = box(
                min_x_util, coordenada_actual, max_x_util, coordenada_siguiente
            )

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
    polygon: Polygon, largo: float, ancho: float
) -> Optional[Polygon]:
    """
    Crea un sub-polígono con un largo y ancho específicos, centrado
    dentro del polígono contenedor (soporta orientaciones arbitrarias).
    """
    if not polygon or polygon.is_empty:
        return None

    # =========================================================================
    # 1. OBTENER RECTÁNGULO CONTENEDOR MÍNIMO Y SU ÁNGULO REAL
    # =========================================================================
    # minimum_rotated_rectangle calcula el Bounding Box Orientado (OBB) exacto
    mrr = polygon.minimum_rotated_rectangle
    mrr_coords = list(mrr.exterior.coords)

    # Obtenemos el vector del lado más largo o principal del OBB
    p0, p1 = mrr_coords[0], mrr_coords[1]
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)

    # =========================================================================
    # 2. ALINEAR TEMPORALMENTE EL POLÍGONO CON SU CENTROIDE
    # =========================================================================
    centroide = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=centroide)

    # Medimos el marco real alineado
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_contenedor = max_x - min_x
    ancho_contenedor = max_y - min_y

    # Si las dimensiones solicitadas quedan invertidas respecto al eje alineado,
    # verificamos ambas combinaciones (Largo x Ancho) o (Ancho x Largo)
    fit_directo = (largo <= largo_contenedor) and (ancho <= ancho_contenedor)
    fit_invertido = (ancho <= largo_contenedor) and (largo <= ancho_contenedor)

    if not (fit_directo or fit_invertido):
        print("⚠️ Advertencia: Las dimensiones solicitadas superan el tamaño del polígono contenedor.")
        return None

    # Ajustar orientación si encaja mejor de forma invertida
    if not fit_directo and fit_invertido:
        largo, ancho = ancho, largo

    # =========================================================================
    # 3. CREAR CAJA CENTRADA EN EL CENTROIDE
    # =========================================================================
    cx, cy = centroide.x, centroide.y
    sub_box_alineado = box(
        cx - (largo / 2.0),
        cy - (ancho / 2.0),
        cx + (largo / 2.0),
        cy + (ancho / 2.0)
    )

    # =========================================================================
    # 4. ROTAR DE VUELTA Y VALIDAR CONTENCIÓN FÍSICA
    # =========================================================================
    sub_polygon_final = affinity.rotate(sub_box_alineado, angulo_grados, origin=centroide)

    # Validación topológica final: garantiza que no sobresalga en polígonos irregulares
    if not polygon.buffer(1e-6).contains(sub_polygon_final):
        print("⚠️ Advertencia: El sub-polígono centrado sobresale de los límites reales del contenedor.")
        return None

    return sub_polygon_final

