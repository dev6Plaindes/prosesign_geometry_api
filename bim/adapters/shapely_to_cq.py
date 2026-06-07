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