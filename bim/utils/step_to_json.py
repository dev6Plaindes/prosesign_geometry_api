from shapely import unary_union
import trimesh


def step_a_json(step_path):
    scene = trimesh.load(step_path)
    data = {}

    FACTOR_ESCALA = 10000

    for name, geom in scene.geometry.items():
        vertices_escalados = geom.vertices * FACTOR_ESCALA

        vertices_enteros = [
            [int(round(coord)) for coord in vertex]
            for vertex in vertices_escalados
        ]

        data[name] = {
            "vertices": vertices_enteros,
            "faces": geom.faces.tolist(),
        }

    return data

import json
from shapely.geometry import Polygon
import shapely.affinity


def terreno_a_mesh_json(vertices_2d):
    """Convierte una lista de coordenadas UTM a formato mesh 3D

    utilizando Shapely para trasladar el terreno al origen (0,0)
    en el cuadrante positivo.
    """
    if len(vertices_2d) < 3:
        raise ValueError(
            "Un terreno necesita al menos 3 vértices para formar un polígono."
        )

    # 1. Crear el polígono original con Shapely
    poligono_original = Polygon(vertices_2d)

    # 2. Obtener los límites mínimos absolutos (minx, miny)
    minx, miny, _, _ = poligono_original.bounds

    # 3. Trasladar el polígono para que empiece exactamente en (0,0)
    # Restamos minx y miny para moverlo al cuadrante positivo
    poligono_trasladado = shapely.affinity.translate(
        poligono_original, xoff=-minx, yoff=-miny
    )

    # 4. Extraer las nuevas coordenadas (redondeando a 3 decimales para metros)
    # Nota: exterior.coords incluye el punto inicial al final para cerrar el polígono,
    # por lo que usamos [: -1] para no duplicar el primer vértice en el formato mesh.
    vertices_limpios = [
        [round(x, 3), round(y, 3), 0.0]
        for x, y in poligono_trasladado.exterior.coords[:-1]
    ]

    # 5. Generar las caras (triangulación en abanico)
    caras = []
    num_vertices = len(vertices_limpios)
    for i in range(1, num_vertices - 1):
        caras.append([0, i, i + 1])

    # 6. Estructura final del JSON
    data = {"vertices": vertices_limpios, "faces": caras}

    return {"terreno": data}

from shapely.geometry import Polygon
from shapely import affinity

def terreno_a_mesh_array(vertices_2d):
    """
    Convierte un polígono 2D a la estructura de malla plana compatible 
    con datos_to_shapely y render_2d_shapely, usando una única cara poligonal.
    """
    if len(vertices_2d) < 3:
        raise ValueError("Se necesitan al menos 3 vértices")

    # 1. Crear el Polígono en Shapely
    poly = Polygon(vertices_2d)

    # 2. Trasladar a (0,0) tal como lo tenías
    minx, miny, _, _ = poly.bounds
    poly = affinity.translate(poly, xoff=-minx, yoff=-miny)

    # 3. Extraer Vértices en el plano Z=0 (Redondeados a 3 decimales)
    coords_2d = list(poly.exterior.coords)[:-1]
    vertices = [[round(x, 3), round(y, 3), 0.0] for x, y in coords_2d]

    # 4. Agrupar TODOS los vértices en una única cara poligonal
    # Esto evita la triangulación Fan y elimina cualquier línea diagonal interna
    faces = [vertices]

    # 5. Retorna la estructura de lista de diccionarios idéntica a la de CadQuery
    return [{
        "name": "Terreno",
        "vertices": vertices,
        "faces": faces
    }]

import json

import shapely.wkt
from shapely.geometry import Polygon

def polygon_a_mesh_array(vertices_2d, nombre="polygon"):
    # -----------------------------------
    # 1. UNIFICAR ENTRADA A OBJETO SHAPELY
    # -----------------------------------
    if isinstance(vertices_2d, str):
        poly_original = shapely.wkt.loads(vertices_2d)
    
    elif isinstance(vertices_2d, list):
        poly_original = Polygon(vertices_2d)
        
    elif hasattr(vertices_2d, "exterior"):
        poly_original = vertices_2d
        
    else:
        raise TypeError("Formato de entrada no soportado. Usa Lista, Shapely Polygon o String WKT.")

    # -----------------------------------
    # 2. EXTRAER PUNTOS Y VALIDAR
    # -----------------------------------
    puntos_originales = list(poly_original.exterior.coords)[:-1]
    
    if len(puntos_originales) < 3:
        raise ValueError("El polígono necesita al menos 3 puntos")

    # -----------------------------------
    # 3. CREAR VÉRTICES 3D EN SU POSICIÓN ORIGINAL
    # -----------------------------------
    vertices_3d = []
    for x, y in puntos_originales:
        vertices_3d.append([
            round(x, 3),  
            round(y, 3),
            0.0           
        ])

    # -----------------------------------
    # 4. GENERAR FACES (Evitar la diagonal en cuadrantes)
    # -----------------------------------
    faces = []
    
    # Si es un rectángulo o cuadrado (4 esquinas), guardamos una sola cara de 4 puntos
    if len(vertices_3d) == 4:
        faces.append([
            vertices_3d[0],
            vertices_3d[1],
            vertices_3d[2],
            vertices_3d[3]
        ])
    else:
        # Si tiene más lados (terrenos complejos), mantenemos el Fan para que no se rompa
        for i in range(1, len(vertices_3d) - 1):
            cara_coordenadas = [
                vertices_3d[0],
                vertices_3d[i],
                vertices_3d[i + 1]
            ]
            faces.append(cara_coordenadas)

    return [
        {
            "name" : nombre,
            "vertices": vertices_3d,
            "faces": faces
        }
    ]
    
    
def ensamblaje_to_array(ensamblaje):
    """
    Convierte un Assembly de CadQuery en un array JSON-safe
    incluyendo el nombre de cada pieza, sus vértices y caras:
    [{name: "pieza1", vertices: [...], faces: [...]}, ...]
    """
    resultado = []

    # Iteramos sobre los objetos del ensamblaje (.objects es un diccionario interno de CadQuery)
    for nombre, sub_assembly in ensamblaje.objects.items():
        # sub_assembly.obj contiene el objeto real asignado a esa pieza del ensamblaje
        workplane_or_shape = sub_assembly.obj
        
        if not workplane_or_shape:
            continue

        # SOLUCIÓN AL ATTRIBUTE ERROR:
        # Si es un 'Workplane', extraemos su geometría real con .val()
        # Si ya es un 'Shape' o 'Solid' directo, lo dejamos como está
        if hasattr(workplane_or_shape, "val"):
            shape = workplane_or_shape.val()
        else:
            shape = workplane_or_shape

        # Verificación de seguridad: si .val() devolvió None o algo sin sólidos, saltamos
        if not shape or not hasattr(shape, "Solids"):
            continue

        # Extraemos los sólidos de este componente en específico
        for solid in shape.Solids():
            
            # ---------------------------
            # VÉRTICES
            # ---------------------------
            vertices = [
                (round(v.X, 4), round(v.Y, 4), round(v.Z, 4))
                for v in solid.Vertices()
            ]

            # ---------------------------
            # CARAS (como polígonos)
            # ---------------------------
            faces = []
            for face in solid.Faces():
                try:
                    wire = face.outerWire()
                    poly = [
                        (round(p.X, 4), round(p.Y, 4), round(p.Z, 4))
                        for p in wire.Vertices()
                    ]
                    faces.append(poly)
                except:
                    # Si alguna cara no tiene un outerWire válido o falla, la ignoramos
                    pass

            # ---------------------------
            # OBJETO FINAL CON SU NOMBRE
            # ---------------------------
            resultado.append({
                "name": nombre,  # <--- Nombre del componente extraído del Assembly
                "vertices": vertices,
                "faces": faces
            })

    return resultado


from shapely.geometry import Polygon, MultiPolygon

from shapely.geometry import Polygon, LineString, GeometryCollection

def datos_to_shapely(datos):
    """
    Convierte los datos 3D de CadQuery en objetos 2D de Shapely.
    Soporta tanto caras planas (Polígonos) como caras verticales colapsadas (Líneas),
    garantizando que no se pierda ningún elemento en el renderizado.
    """
    escena_shapely = {}

    for pieza in datos:
        nombre = pieza["name"]
        geometrias_2d = []

        for cara_3d in pieza["faces"]:
            # Proyectamos a 2D tomando solo X e Y
            puntos_2d = [(round(pt[0], 4), round(pt[1], 4)) for pt in cara_3d]
            
            # Eliminamos duplicados consecutivos
            puntos_limpios = []
            for p in puntos_2d:
                if not puntos_limpios or p != puntos_limpios[-1]:
                    puntos_limpios.append(p)
            
            if not puntos_limpios:
                continue

            # CASO 1: Es una cara con área en 2D (tapas superiores/inferiores, inclinadas, etc.)
            # Clonamos el inicio al final para asegurar el cierre del polígono
            puntos_poligono = list(puntos_limpios)
            if puntos_poligono[0] != puntos_poligono[-1]:
                puntos_poligono.append(puntos_poligono[0])

            if len(puntos_poligono) >= 4:
                try:
                    poly = Polygon(puntos_poligono)
                    if poly.is_valid and poly.area > 0:
                        geometrias_2d.append(poly)
                        continue  # Si ya es un polígono válido, pasamos a la siguiente cara
                except:
                    pass

            # CASO 2: La cara es vertical y colapsó en una línea (área = 0)
            # Si tiene al menos 2 puntos únicos, sigue siendo una arista visible crucial de la pieza
            if len(puntos_limpios) >= 2:
                try:
                    linea = LineString(puntos_limpios)
                    if linea.is_valid:
                        geometrias_2d.append(linea)
                except:
                    pass

        if geometrias_2d:
            # Usamos GeometryCollection para poder mezclar tanto Polígonos como Líneas
            # sin que Shapely reclame por problemas de topología o dimensiones mixtas
            escena_shapely[nombre] = GeometryCollection(geometrias_2d)

    return escena_shapely

