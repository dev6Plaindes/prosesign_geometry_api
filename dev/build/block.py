import cadquery as cq
from shapely.geometry import Polygon
from dev.assemblys.capas import FactoryCapas

# =====================================================================
# FUNCIÓN PARA CREAR BLOQUES 3D BASADOS EN UN POLÍGONO DE SHAPELY
# =====================================================================

def new_block(
    polygon: Polygon, 
    alto_z: float, 
    assembly: cq.Assembly, 
    nombre: str = "Bloque", 
    color_hex: str = "#3498DB",
    factory_capas: FactoryCapas = None,
    nivel: int = 1
):
    """
    Crea un bloque extruido en 3D usando la huella exacta de un Polygon de Shapely,
    lo cual respeta de forma nativa cualquier rotación, desfase o inclinación.
    
    Parámetros:
        - polygon: Objeto Polygon de Shapely que define la base del bloque.
        - alto_z: float, la altura de extrusión (dimensión Z).
        - assembly: Objeto cq.Assembly donde se añadirá el bloque.
        - nombre: str, identificador para el árbol del visor.
        - color_hex: str, color en formato hexadecimal.
        - factory_capas: FactoryCapas, para agregar a capas.
        - nivel: int, nivel al que pertenece.
    """
    # 1. Obtener las coordenadas del contorno exterior del polígono
    # Shapely repite el primer punto al final para cerrar el bucle, lo cual es ideal para .polyline()
    vertices_2d = list(polygon.exterior.coords)
    
    # 2. Dibujar la huella inclinada y extruirla en Z de forma nativa
    bloque_3d = (
        cq.Workplane("XY")
        .polyline(vertices_2d)
        .close()
        .extrude(alto_z)
    )
    
    # 3. Añadir el objeto extruido al Assembly
    assembly.add(
        bloque_3d,
        name=nombre,
        color=cq.Color(color_hex)
    )

    # 4. Añadir a capas
    if factory_capas:
        factory_capas.add_in_capa_auto(bloque_3d, nivel=nivel, name=nombre)