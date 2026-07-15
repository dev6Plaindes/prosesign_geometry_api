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