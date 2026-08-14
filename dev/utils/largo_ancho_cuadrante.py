from math import dist
from shapely.geometry import Polygon

def obtener_dimensiones_cuadrante(cuadrante_normalizado):
    """
    Toma los vértices del cuadrante (lista de tuplas/listas o un Polygon de Shapely)
    y calcula su largo y ancho reales utilizando el rectángulo delimitador mínimo rotado,
    independientemente de si el cuadrante está inclinado o rotado.
    """
    # 1. Convertir a Polygon de Shapely si es una lista de vértices
    if not isinstance(cuadrante_normalizado, Polygon):
        poligono = Polygon(cuadrante_normalizado)
    else:
        poligono = cuadrante_normalizado
    
    # 2. Obtener el rectángulo delimitador mínimo rotado
    rect_minimo = poligono.minimum_rotated_rectangle
    
    # 3. Extraer las coordenadas de los vértices del rectángulo resultante
    coords = list(rect_minimo.exterior.coords)
    
    # 4. Calcular la distancia euclidiana de dos lados adyacentes
    lado_1 = dist(coords[0], coords[1])
    lado_2 = dist(coords[1], coords[2])
    
    # 5. Asignar el lado mayor como largo y el menor como ancho (o viceversa según tu criterio)
    largo = max(lado_1, lado_2)
    ancho = min(lado_1, lado_2)
    
    return largo, ancho