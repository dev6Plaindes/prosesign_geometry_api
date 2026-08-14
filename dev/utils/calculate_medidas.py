from itertools import groupby
from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, box
from shapely import affinity, unary_union
import math

from bim.utils.algoritm_distibution import auto_distribution_ambientes_y

def _get_main_axis_angle(polygon: Polygon) -> float:
    """
    Calcula el ángulo del eje principal (lado más largo) del rectángulo
    delimitador mínimo de un polígono para obtener su orientación real.
    """
    # 1. Obtener el rectángulo delimitador mínimo rotado.
    mrr = polygon.minimum_rotated_rectangle

    # 2. Extraer las coordenadas de los vértices.
    coords = list(mrr.exterior.coords)

    # 3. Calcular la longitud de dos lados adyacentes para encontrar el más largo.
    lado_1_len = math.dist(coords[0], coords[1])
    lado_2_len = math.dist(coords[1], coords[2])

    # 4. Determinar los puntos del lado más largo para calcular el ángulo.
    if lado_1_len >= lado_2_len:
        p1, p2 = coords[0], coords[1]
    else:
        p1, p2 = coords[1], coords[2]

    # 5. Calcular el ángulo en grados.
    # CORRECCIÓN: Se usa p2[0] - p1[0] para el delta X (dx). El código original tenía un error tipográfico (p1[0] - p1[0]).
    angle_rad = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    return math.degrees(angle_rad)


def largos_for_piso_and_ambiente(
    data: List[Dict[str, Any]],
    polygon: Polygon,
    name_pabellon: str,
    min_floors: int = 1
) -> List[List[Dict[str, Any]]]:
    """
    Calcula la distribución de ambientes a lo largo del lado más grande de un Polygon,
    centrando el conjunto de ambientes tanto horizontal como verticalmente dentro del
    polígono contenedor. Genera la huella física (Polygon de Shapely) para cada
    ambiente individual ya en su posición final y orientada correctamente.
    """
    # 1. ANÁLISIS DE GEOMETRÍA Y ORIENTACIÓN DEL POLÍGONO PADRE
    # Se usa el rectángulo delimitador mínimo para obtener el ángulo del eje principal real.
    angulo_grados = _get_main_axis_angle(polygon)

    # El pivote para la rotación es el centroide del polígono original.
    pivote = polygon.centroid

    # Se alinea el polígono a 0 grados para trabajar en un sistema de coordenadas cartesiano.
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote)

    # Se obtienen las dimensiones reales del área de trabajo alineada.
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_total = max_x - min_x
    ancho_total = max_y - min_y

    # 2. DISTRIBUCIÓN LÓGICA DE AMBIENTES (ALGORITMO DE EMPAQUETADO)
    # Se distribuyen los ambientes a lo largo de la dimensión más larga disponible.
    pabellon_p = auto_distribution_ambientes_y(data, largo_total, min_floors=min_floors)

    if isinstance(pabellon_p, str):
        raise ValueError(
            f"No se pudo distribuir los ambientes en el pabellón '{name_pabellon}' "
            f"con el largo disponible ({largo_total:.2f}m). Detalles: {pabellon_p}"
        )

    # 3. GENERACIÓN Y POSICIONAMIENTO DE GEOMETRÍAS POR PISO
    resultado_completo = []

    # Se agrupan los ambientes por el piso asignado por el algoritmo.
    for clave, grupo in groupby(pabellon_p, key=lambda x: x['Piso']):
        grupo_lista = list(grupo)
        piso_data = []

        # Se calcula el largo total que ocuparán los ambientes de este piso.
        largos_ambientes_piso = [item['Largo_Individual'] for item in grupo_lista]
        largo_total_piso = sum(largos_ambientes_piso)

        # CÁLCULO DE CENTRADO HORIZONTAL: Se calcula el margen para centrar el bloque de ambientes.
        offset_x_centrado = (largo_total - largo_total_piso) / 2

        # El cursor para dibujar arranca en el borde izquierdo del área alineada más el margen de centrado.
        coordenada_actual_x = min_x + offset_x_centrado

        for item in grupo_lista:
            largo_ambiente = item['Largo_Individual']
            ancho_ambiente = item['Ancho_Individual']

            # CÁLCULO DE CENTRADO VERTICAL: Se calcula el margen para centrar cada ambiente en el ancho.
            offset_y_centrado = (ancho_total - ancho_ambiente) / 2

            # Coordenadas del ambiente individual dentro del espacio alineado.
            y_inicio_ambiente = min_y + offset_y_centrado
            x_fin_ambiente = coordenada_actual_x + largo_ambiente
            y_fin_ambiente = y_inicio_ambiente + ancho_ambiente

            # Se crea la caja (Polygon) del ambiente en el espacio de trabajo alineado.
            caja_ambiente_alineada = box(coordenada_actual_x, y_inicio_ambiente, x_fin_ambiente, y_fin_ambiente)

            # Se rota la caja del ambiente de vuelta a la orientación original del terreno.
            caja_ambiente_rotada = affinity.rotate(caja_ambiente_alineada, angulo_grados, origin=pivote)

            piso_data.append({
                "ambiente": item['Ambiente'],
                "largo": round(largo_ambiente, 2),
                "ancho": round(ancho_ambiente, 2),
                "pabellon": name_pabellon,
                "piso": item['Piso'],
                "polygon": caja_ambiente_rotada  # Se guarda el polígono final, ya posicionado.
            })

            # Se avanza el cursor para el siguiente ambiente.
            coordenada_actual_x = x_fin_ambiente

        resultado_completo.append(piso_data)

    return resultado_completo

def obtener_polygon_real_del_piso(
    piso_data: List[Dict[str, Any]],
    polygon_parent: Polygon
) -> Optional[Polygon]:
    """
    Une los polígonos de los recintos de un piso en un único polígono sólido (huella).
    NOTA: Se asume que los polígonos de entrada (de 'piso_data') ya están
    correctamente posicionados y centrados por la función `largos_for_piso_and_ambiente`.
    El argumento `polygon_parent` se mantiene por compatibilidad pero ya no se usa para centrar.
    """
    if not piso_data:
        return None

    poligonos_ambientes = [item["polygon"] for item in piso_data if "polygon" in item and item["polygon"] is not None]

    if not poligonos_ambientes:
        return None

    # Se unen todas las geometrías de los ambientes del piso.
    resultado_union = unary_union(poligonos_ambientes)

    # .envelope crea el rectángulo delimitador de la unión, que es lo que se necesita para la estructura.
    # Si la unión ya es un rectángulo (lo será si los ambientes son contiguos),
    # esto es equivalente a la propia unión.
    polygon_real_piso = resultado_union.envelope if resultado_union.geom_type == 'MultiPolygon' else resultado_union

    # La lógica de centrado anterior ahora reside en `largos_for_piso_and_ambiente`
    # para asegurar que tanto la huella del piso como los polígonos individuales
    # estén correctamente posicionados desde su creación. El centrado aquí ya no es necesario.

    return polygon_real_piso

def limpiar_distribucion_para_resumen(distribucion):
    """
    Serializa los objetos Polygon a cadenas WKT para exportación JSON/BD.
    """
    if not distribucion:
        return []

    distribucion_limpia = []
    for piso in distribucion:
        piso_limpio = []
        for item in piso:
            item_limpio = item.copy()
            if "polygon" in item_limpio:
                polygon_obj = item_limpio["polygon"]
                item_limpio["polygon"] = polygon_obj.wkt if polygon_obj is not None else None
            piso_limpio.append(item_limpio)
        distribucion_limpia.append(piso_limpio)

    return distribucion_limpia