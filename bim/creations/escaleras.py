import math
import cadquery as cq

from bim.config_proyect import CONFIG_PROYECTO

def create_stairs(
    ensamblaje,
    ancho_hab: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    posicion_puerta: str = "bottom",
    nivel: int = 1,
    orientacion: str = "horizontal",
    huella: float = 0.28,
    contrahuella_max: float = 0.18,
    espesor_peldaño: float = 0.15,
    desplazamiento_x_bloque: float = None,
    desplazamiento_y_bloque: float = None
):
    """
    Genera una escalera en U de dos tramos macizos con descanso invertido.
    El descanso se ubica en el origen (desplazamiento_x) y los tramos se desarrollan hacia +X.
    Se desplaza/baja el largo total en Y para su correcto acoplamiento inferior.
    """
    
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']
    ancho_escalera = CONFIG_PROYECTO["ancho_escalera"]

    # 1. Cálculos de peldaños y alturas
    num_pasos_totales = math.ceil(altura_piso / contrahuella_max)
    contrahuella_real = altura_piso / num_pasos_totales
    desfase_z = (nivel - 1) * altura_piso

    pasos_tramo1 = math.ceil(num_pasos_totales / 2)
    pasos_tramo2 = num_pasos_totales - pasos_tramo1

    largo_descanso = ancho_escalera 
    ancho_total_escalera = (ancho_escalera * 2) + 0.05 

    largo_desarrollo_tramo1 = pasos_tramo1 * huella
    largo_desarrollo_tramo2 = pasos_tramo2 * huella

    # 2. Posicionamiento en Y ajustado para bajar la estructura por completo
    ancho_total_hab = ancho_hab
    # [DOCUMENTACIÓN] Se corrigió el posicionamiento base de la escalera para posicion_puerta == "bottom".
    # Ahora se desplaza restando ancho_total_escalera para proyectarse en la zona del balcón exterior y no invadir aulas.
    if posicion_puerta.lower() == "bottom":
        y_base = desplazamiento_y - ancho_total_escalera
    elif posicion_puerta.lower() == "top":
        y_base = desplazamiento_y
    else:
        y_base = desplazamiento_y - ancho_total_escalera

    # --- DESCANSO INTERMEDIO (Extremo izquierdo) ---
    alto_descanso = pasos_tramo1 * contrahuella_real
    
    centro_z_descanso = desfase_z + alto_descanso - (espesor_peldaño / 2)
    centro_x_descanso = desplazamiento_x + (largo_descanso / 2)
    centro_y_descanso = y_base + (ancho_total_escalera / 2)

    descanso = (
        cq.Workplane("XY")
        .box(largo_descanso, ancho_total_escalera, espesor_peldaño)
        .translate((centro_x_descanso, centro_y_descanso, centro_z_descanso))
    )

    # --- TRAMO 1: Sube hacia la DERECHA (+X) ---
    puntos_t1 = [(0, 0)]
    x_act, z_act = 0, 0
    
    for i in range(pasos_tramo1):
        z_act += contrahuella_real
        puntos_t1.append((x_act, z_act))
        x_act += huella
        puntos_t1.append((x_act, z_act))
        
    puntos_t1.append((x_act, z_act - espesor_peldaño))
    puntos_t1.append((0, 0 - espesor_peldaño))
    
    centro_y_t1 = y_base + (ancho_escalera / 2)
    x_inicio_t1 = desplazamiento_x - largo_desarrollo_tramo1
    
    tramo1 = (
        cq.Workplane("XZ")
        .polyline(puntos_t1)
        .close()
        .extrude(ancho_escalera)
        .translate((x_inicio_t1, centro_y_t1 + (ancho_escalera / 2), desfase_z))
    )

    # --- TRAMO 2: Sube hacia la IZQUIERDA (-X) ---
    puntos_t2 = [(0, 0)]
    x_act, z_act = 0, 0
    
    for j in range(pasos_tramo2):
        z_act += contrahuella_real
        puntos_t2.append((x_act, z_act))
        x_act -= huella
        puntos_t2.append((x_act, z_act))
        
    puntos_t2.append((x_act, z_act - espesor_peldaño))
    puntos_t2.append((0, 0 - espesor_peldaño))
    
    centro_y_t2 = y_base + ancho_total_escalera - (ancho_escalera / 2)
    x_inicio_t2 = desplazamiento_x
    z_inicio_t2 = desfase_z + alto_descanso
    
    tramo2 = (
        cq.Workplane("XZ")
        .polyline(puntos_t2)
        .close()
        .extrude(ancho_escalera)
        .translate((x_inicio_t2, centro_y_t2 + (ancho_escalera / 2), z_inicio_t2))
    )

    # --- UNIFICACIÓN MONOLÍTICA ---
    escalera_completa = tramo1.union(descanso).union(tramo2)
    # [DOCUMENTACIÓN] Se unificó la lógica de rotación vertical de la escalera.
    # Ahora la escalera se rota 90° alrededor del origen global del bloque (desplazamiento_x_bloque, desplazamiento_y_bloque)
    # para que gire en perfecta sincronía con los muros y balcones del edificio, asegurando que quede paralela y
    # conectada correctamente al balcón.
    if orientacion.lower() == "vertical":
        px = desplazamiento_x_bloque if desplazamiento_x_bloque is not None else desplazamiento_x
        py = desplazamiento_y_bloque if desplazamiento_y_bloque is not None else desplazamiento_y
        pivote = (px, py, 0)
        escalera_completa = escalera_completa.rotate(pivote, (px, py, 1), 90)
    # 5. Registrar en el ensamblaje general
    return escalera_completa

# [DOCUMENTACIÓN] Se implementó get_stair_dimensions para permitir el cálculo de dimensiones
# en las aserciones de pruebas de coordenadas de las escaleras.
def get_stair_dimensions(huella=0.28, contrahuella_max=0.18):
    """
    Calcula las dimensiones totales y número de pasos de la escalera según la configuración del proyecto.
    """
    import math
    from bim.config_proyect import CONFIG_PROYECTO
    
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    ancho_escalera = CONFIG_PROYECTO["ancho_escalera"]
    
    num_pasos_totales = math.ceil(altura_piso / contrahuella_max)
    pasos_tramo1 = math.ceil(num_pasos_totales / 2)
    pasos_tramo2 = num_pasos_totales - pasos_tramo1
    
    largo_descanso = ancho_escalera
    ancho_total_escalera = (ancho_escalera * 2) + 0.05
    
    largo_desarrollo_tramo1 = pasos_tramo1 * huella
    largo_desarrollo_tramo2 = pasos_tramo2 * huella
    
    largo_total_x = largo_descanso + max(largo_desarrollo_tramo1, largo_desarrollo_tramo2)
    
    return {
        "largo_total_x": largo_total_x,
        "ancho_total_y": ancho_total_escalera,
        "num_pasos_totales": num_pasos_totales
    }
    
import math
from shapely.affinity import rotate
from shapely.geometry import MultiPolygon, Polygon, box


def obtener_angulo_inclinacion(polygon: Polygon) -> float:
    """Calcula el ángulo de inclinación (en grados) del rectángulo orientado

    mínimo del polígono.
    """
    mrr = polygon.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)[:-1]

    # Calcular dimensiones de lados adyacentes
    v0, v1, v2 = coords[0], coords[1], coords[2]
    d1 = math.hypot(v1[0] - v0[0], v1[1] - v0[1])
    d2 = math.hypot(v2[0] - v1[0], v2[1] - v1[1])

    # Tomar el lado principal como referencia del eje X local
    if d1 >= d2:
        dx, dy = v1[0] - v0[0], v1[1] - v0[1]
    else:
        dx, dy = v2[0] - v1[0], v2[1] - v1[1]

    return math.degrees(math.atan2(dy, dx))


def crear_poligono_escalera(
    principal_polygon: Polygon,
    container_polygon: Polygon,
    ancho: float = 2.45,
    largo: float = 3.72,
    lado: str = "derecha",  # Opciones válidas: "derecha" o "izquierda"
    posicion_vertical: str = "top",  # Opciones válidas: "top" o "bottom"
) -> Polygon:
    """Crea un polígono para la escalera pegado a la parte superior/inferior y al

    costado (derecho o izquierdo) de un contenedor inclinado.

    Parameters:
    -----------
    principal_polygon : Polygon
        Polígono principal del pabellón.
    container_polygon : Polygon
        Polígono del contenedor (puede estar inclinado/rotado).
    ancho : float
        Dimensión de la escalera en la dirección perpendicular al borde (3.72).
    largo : float
        Dimensión de la escalera a lo largo del borde (2.45).
    lado : str
        'derecha' o 'izquierda' respecto a la orientación local del contenedor.
    posicion_vertical : str
        'top' para alinear al borde superior o 'bottom' para alinear al borde inferior.
    """
    if lado not in ("derecha", "izquierda"):
        raise ValueError("El parámetro 'lado' debe ser 'derecha' o 'izquierda'")

    if posicion_vertical not in ("top", "bottom"):
        raise ValueError(
            "El parámetro 'posicion_vertical' debe ser 'top' o 'bottom'"
        )

    # 1. Obtener el centroide del contenedor
    cx, cy = container_polygon.centroid.x, container_polygon.centroid.y

    # 2. Obtener el ángulo de inclinación del contenedor
    angulo = obtener_angulo_inclinacion(container_polygon)

    # 3. Des-rotar temporalmente el contenedor a 0 grados
    container_alineado = rotate(container_polygon, -angulo, origin=(cx, cy))
    minx, miny, maxx, maxy = container_alineado.bounds

    # 4. Alinear verticalmente según la posición seleccionada
    if posicion_vertical == "top":
        esc_maxy = maxy
        esc_miny = maxy - largo
    else:  # "bottom"
        esc_miny = miny
        esc_maxy = miny + largo

    # 5. Posicionar la escalera al costado correspondiente (derecha o izquierda)
    if lado == "derecha":
        esc_minx = maxx
        esc_maxx = maxx + ancho
    else:  # "izquierda"
        esc_maxx = minx
        esc_minx = minx - ancho

    escalera_alineada = box(esc_minx, esc_miny, esc_maxx, esc_maxy)

    # 6. Re-rotar la escalera al ángulo original del contenedor
    escalera_rotada = rotate(escalera_alineada, angulo, origin=(cx, cy))

    # 7. Validar intersección segura con el pabellón principal
    if not principal_polygon.contains(escalera_rotada):
        interseccion = escalera_rotada.intersection(principal_polygon)

        if interseccion.is_empty:
            return escalera_rotada

        if isinstance(interseccion, MultiPolygon):
            return max(interseccion.geoms, key=lambda g: g.area)
        elif isinstance(interseccion, Polygon):
            return interseccion

    return escalera_rotada