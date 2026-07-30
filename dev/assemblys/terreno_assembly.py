import cadquery as cq
from shapely.geometry import Polygon

def terreno_assembly(
    vertices_dict, 
    assembly, 
    nombre="Terreno Real (Polígono)", 
    color_hex="#2ECC71"
):
    """
    Dibuja el terreno real en el Assembly y retorna su objeto Polygon de Shapely.
    Soporta formato de diccionario {'x': ..., 'y': ...} o formato de tuplas (x, y).
    """
    # 1. Convertir los vértices normalizados a tuplas simples (x, y)
    if isinstance(vertices_dict[0], dict):
        puntos = [(v["x"], v["y"]) for v in vertices_dict]
    else:
        puntos = [(v[0], v[1]) for v in vertices_dict]
        
    # 2. Crear la geometría 3D en el espacio del CAD (mantiene la inclinación exacta)
    terreno_3d = (
        cq.Workplane("XY")
        .polyline(puntos)
        .close()
        .extrude(0.2) # Grosor de 20cm para diferenciarlo
    )
    
    assembly.add(
        terreno_3d, 
        name=nombre, 
        color=cq.Color(color_hex)
    )
    
    # 3. Crear y retornar el objeto Shapely
    terreno_shapely = Polygon(puntos)
    return terreno_shapely, terreno_3d