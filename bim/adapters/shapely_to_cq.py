import cadquery as cq
from shapely.geometry import Polygon

def shapely_a_cadquery(polygon_shapely: Polygon) -> cq.Workplane:
    """
    Convierte un Polygon de Shapely en un Workplane de CadQuery (plano 2D).
    """
    # 1. Extraemos las coordenadas del contorno exterior
    # coords contiene (x, y), pero Shapely duplica el último punto para cerrar el polígono.
    # Con [: -1] quitamos ese último punto repetido porque CadQuery lo cierra con .close()
    puntos_2d = list(polygon_shapely.exterior.coords)[:-1]
    
    # 2. Creamos el contorno en CadQuery
    poligono_cq = (
        cq.Workplane("XY")
        .polyline(puntos_2d)
        .close() # Cierra el polígono uniendo el último punto con el primero
    )
    
    return poligono_cq

from shapely.geometry import Polygon
import math

def obtener_referencia_cuadrante(best_rect: Polygon, angle_deg: float):
    """
    Devuelve el punto del rectángulo rotado que corresponde
    al origen local (0,0) del cuadrante.
    """

    coords = list(best_rect.exterior.coords)[:-1]

    angle_rad = math.radians(angle_deg)

    # Eje X local del cuadrante
    dir_x = (
        math.cos(angle_rad),
        math.sin(angle_rad)
    )

    # Eje Y local del cuadrante
    dir_y = (
        -math.sin(angle_rad),
        math.cos(angle_rad)
    )

    mejor_punto = None
    mejor_score = None

    for x, y in coords:

        # Proyección sobre ejes locales
        px = x * dir_x[0] + y * dir_x[1]
        py = x * dir_y[0] + y * dir_y[1]

        score = px + py

        if mejor_score is None or score < mejor_score:
            mejor_score = score
            mejor_punto = (x, y)

    return mejor_punto