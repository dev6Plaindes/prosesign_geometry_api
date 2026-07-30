import cadquery as cq
from shapely.geometry import Polygon

def build_cuadrante(vertices, assembly, nombre="Terreno", color_hex="#2ECC71"):
    """
    Toma vértices UTM, los normaliza restando el desfase mínimo (haciendo que
    el terreno parta de 0,0) y añade la placa del terreno al Assembly.
    
    Retorna el offset (desfase) (min_x, min_y) para que sepas dónde quedó el 
    origen real en coordenadas UTM por si necesitas posicionar más cosas.
    """
    # 1. Encontrar los mínimos para que el terreno empiece exactamente en (0,0)
    # Esto es mejor que usar el primer vértice, ya que mantiene todo el terreno en positivo (X >= 0, Y >= 0)
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    min_x = min(xs)
    min_y = min(ys)
    
    # 2. Convertir coordenadas UTM masivas a coordenadas locales (metros)
    vertices_locales = [(x - min_x, y - min_y) for x, y in vertices]
    
    # 3. Crear la geometría del terreno (una base de 10 cm de grosor)
    terreno_3d = (
        cq.Workplane("XY")
        .polyline(vertices_locales)
        .close()
        .extrude(0.1)
    )
    
    # 4. Añadir el objeto al Assembly con su color correspondiente
    assembly.add(
        terreno_3d, 
        name=nombre, 
        color=cq.Color(color_hex)
    )
    
    # Devolvemos los offsets por si necesitas referenciar la ubicación real más adelante
    return min_x, min_y



def build_cuadrante_shapely(vertices, assembly, nombre="Terreno Principal", color_hex="#27AE60"):
    """
    Dibuja la geometría 3D en el Assembly y retorna el objeto Polygon de Shapely 
    con todas sus propiedades espaciales intactas.
    """
    # 1. Generar la geometría 3D en CadQuery usando los vértices normalizados
    cuadrante_3d = (
        cq.Workplane("XY")
        .polyline(vertices)
        .close()
        .extrude(0.1)
    )
    
    assembly.add(
        cuadrante_3d, 
        name=nombre, 
        color=cq.Color(color_hex)
    )

    # 2. Crear y retornar el elemento Shapely original
    cuadrante_shapely = Polygon(vertices)
    return cuadrante_shapely