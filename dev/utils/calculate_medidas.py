from itertools import groupby
from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, box
from shapely import affinity, unary_union
import math

from bim.utils.algoritm_distibution import auto_distribution_ambientes_y

def largos_for_piso_and_ambiente(
    data: List[Dict[str, Any]], 
    polygon: Polygon, 
    name_pabellon: str, 
    min_floors: int = 1
) -> List[List[Dict[str, Any]]]:
    """
    Calcula la distribución de ambientes a lo largo del lado más grande de un Polygon.
    Genera la huella física (Polygon de Shapely) para cada ambiente individual y la inyecta
    directamente en su diccionario de metadatos bajo la clave 'polygon'.
    
    Retorna:
        - List[List[Dict[str, Any]]]: Lista de pisos, donde cada piso contiene la lista de 
                                      sus ambientes con sus metadatos y su respectivo polígono.
    """
    # =========================================================================
    # 1. CALCULAR ÁNGULO Y ALINEAR EL POLÍGONO PARA MEDIR EL LARGO REAL
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    # Calcular ángulo de inclinación
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # Alinear temporalmente a 0 grados usando su propio centroide como pivote
    pivote = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote)
    
    # Extraer las dimensiones reales alineadas
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_total = max_x - min_x
    ancho_total = max_y - min_y
    
    # El "largo" para tu función de distribución será el lado más grande
    largo_para_distribuir = max(largo_total, ancho_total)

    # =========================================================================
    # 2. EJECUTAR DISTRIBUCIÓN AUTOMÁTICA
    # =========================================================================
    pabellon_p = auto_distribution_ambientes_y(data, largo_para_distribuir, min_floors=min_floors)

    if isinstance(pabellon_p, str):
        raise ValueError(
            f"No se pudo distribuir los ambientes en el pabellón '{name_pabellon}' "
            f"con el largo disponible ({largo_para_distribuir:.2f}m). Detalles: {pabellon_p}"
        )

    # =========================================================================
    # 3. CONSTRUCCIÓN UNIFICADA DE METADATOS Y GEOMETRÍAS
    # =========================================================================
    resultado_completo = []

    # Agrupar por piso usando groupby
    for clave, grupo in groupby(pabellon_p, key=lambda x: x['Piso']):
        grupo_lista = list(grupo)
        piso_data = []
        
        # Empezamos el barrido acumulativo en el extremo izquierdo alineado (min_x)
        coordenada_actual = min_x

        for item in grupo_lista:
            largo_ambiente = item['Largo_Individual']
            coordenada_siguiente = coordenada_actual + largo_ambiente
            
            # 1. Crear la caja del ambiente en el estado plano alineado
            caja_ambiente_alineada = box(coordenada_actual, min_y, coordenada_siguiente, max_y)
            
            # 2. Rotar la caja de vuelta a la orientación inclinada original
            caja_ambiente_rotada = affinity.rotate(caja_ambiente_alineada, angulo_grados, origin=pivote)
            
            # 3. Agrupar toda la data y el polígono en un solo diccionario unificado
            piso_data.append({
                "ambiente": item['Ambiente'], 
                "largo": round(largo_ambiente, 2),
                "pabellon": name_pabellon,
                "piso": item['Piso'],
                "polygon": caja_ambiente_rotada  # <─── ¡Aquí está tu Polygon inyectado!
            })
            
            coordenada_actual = coordenada_siguiente
            
        resultado_completo.append(piso_data)

    return resultado_completo

def obtener_polygon_real_del_piso(
    piso_data: List[Dict[str, Any]], 
    polygon_parent: Polygon
) -> Optional[Polygon]:
    """
    Lee la lista de ambientes de un piso específico, genera un único Polygon 
    unificado que representa el largo real total ocupado por ese piso y lo centra
    horizontal y verticalmente dentro del polígono padre.
    
    Parámetros:
        - piso_data: Lista de diccionarios de un piso (ej. distribucion_primaria[0])
                     donde cada elemento contiene la clave 'polygon'.
        - polygon_parent: El Polygon de Shapely original (contenedor).
                     
    Retorna:
        - Polygon: El polígono unificado y perfectamente centrado dentro del padre.
                   Retorna None si la lista está vacía.
    """
    if not piso_data:
        return None
        
    # 1. Extraemos todos los polígonos individuales de los ambientes del piso
    poligonos_ambientes = [item["polygon"] for item in piso_data if "polygon" in item]
    
    if not poligonos_ambientes:
        return None
        
    # 2. Fusionamos todos los tramos en un solo bloque sólido
    resultado_union = unary_union(poligonos_ambientes)
    
    # BLINDAJE: Si se generó un MultiPolygon, tomamos su envelope para garantizar un Polygon
    if resultado_union.geom_type == 'MultiPolygon':
        polygon_real_piso = resultado_union.envelope 
    else:
        polygon_real_piso = resultado_union
        
    # 3. Calcular los centroides (puntos centrales) de ambos polígonos
    centro_padre = polygon_parent.centroid
    centro_piso = polygon_real_piso.centroid
    
    # 4. Calcular la distancia de movimiento necesaria en cada eje (X e Y)
    dx = centro_padre.x - centro_piso.x
    dy = centro_padre.y - centro_piso.y
    
    # 5. Trasladar el polígono blindado hacia el centro del padre
    polygon_centrado = affinity.translate(polygon_real_piso, xoff=dx, yoff=dy)
        
    # 6. Retornar el objeto que SÍ fue trasladado
    return polygon_centrado

def limpiar_distribucion_para_resumen(distribucion):
    if not distribucion:
        return []
    
    distribucion_limpia = []
    for piso in distribucion:
        piso_limpio = []
        for item in piso:
            # Copiamos el diccionario para no alterar la geometría en memoria
            item_limpio = item.copy()
            
            if "polygon" in item_limpio:
                polygon_obj = item_limpio["polygon"]
                if polygon_obj is not None:
                    # .wkt convierte el Polygon de Shapely a un string estándar
                    item_limpio["polygon"] = polygon_obj.wkt
                else:
                    item_limpio["polygon"] = None
                
            piso_limpio.append(item_limpio)
        distribucion_limpia.append(piso_limpio)
        
    return distribucion_limpia

