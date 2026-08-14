from shapely.geometry import Polygon
from math import dist # Necesario para calcular distancias euclidianas

def imprimir_dimensiones_poligono(poligono: Polygon, name : str="Poligono"):
    """
    Imprime el ancho y largo reales de un polígono de Shapely,
    calculando su rectángulo delimitador mínimo rotado para
    manejar polígonos inclinados.
    """
    
    # 1. Obtener el rectángulo delimitador mínimo rotado.
    # Esto devuelve un nuevo objeto Polygon que es un rectángulo.
    rectangulo_minimo = poligono.minimum_rotated_rectangle
    
    # 2. Extraer las coordenadas de los vértices del rectángulo.
    # .exterior.coords devuelve una lista de tuplas (x, y).
    # Un rectángulo tiene 5 coordenadas (la primera y la última son iguales).
    coords = list(rectangulo_minimo.exterior.coords)
    
    # 3. Calcular la longitud de dos lados adyacentes.
    # Usamos math.dist para la distancia euclidiana entre puntos.
    # Lado 1: Distancia entre el primer punto y el segundo.
    lado_a = dist(coords[0], coords[1])
    # Lado 2: Distancia entre el segundo punto y el tercero.
    lado_b = dist(coords[1], coords[2])
    
    # 4. Asignar convencionalmente el menor como ancho y el mayor como largo.
    # Esto asegura consistencia sin importar la orientación inicial.
    ancho = min(lado_a, lado_b)
    largo = max(lado_a, lado_b)
    
    # 5. Imprimir resultados.
    print("============================")
    print(f"Dimensiones Reales de {name} (Independiente de la inclinación):")
    print(f"Ancho real: {ancho:.3f} m")
    print(f"Largo real: {largo:.3f} m")
    print("============================")
    