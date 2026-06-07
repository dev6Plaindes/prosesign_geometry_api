import math
import cadquery as cq

from bim.config_proyect import CONFIG_PROYECTO

def create_techo_z_1(
    ancho_techo: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    posicion_puerta: str = "bottom",
    nivel: int = 1,
    orientacion: str = "horizontal",
    largo_inclinado: float = 8.00,
    largo_plano: float = 1.80,
    espesor_techo: float = 0.25,
    desnivel_base: float = 0.40
):
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']

    desfase_z = nivel * (altura_piso + 0.1) 
    
    # Ahora el 'ancho_techo' se convierte en la dimensión que se extruye en el eje X
    ancho_total_techo_x = ancho_techo
    
    if posicion_puerta.lower() == "bottom":
        y_base = desplazamiento_y
    elif posicion_puerta.lower() == "top":
        y_base = desplazamiento_y + e_muro
    else:
        y_base = desplazamiento_y

    # Perfil 2D ahora en el plano YZ (El largo corre sobre el eje Y)
    puntos_perfil = [
        (0, 0),                                               
        (0, desnivel_base + espesor_techo),                                                   
        (largo_inclinado, espesor_techo),                                                     
        (largo_inclinado + largo_plano, espesor_techo),                                       
        (largo_inclinado + largo_plano, 0),                                                   
        (largo_inclinado, 0),                                                                 
        (0, 0)                                                                             
    ]

    # 1. CREACIÓN EN EL ORIGEN (Usando YZ para invertir largo por ancho)
    techo = (
        cq.Workplane("YZ")
        .polyline(puntos_perfil)
        .close()
        # Se extruye en el eje X de forma simétrica (-ancho/2 a +ancho/2)
        .extrude(ancho_total_techo_x) 
    )
    
    # 2. ROTACIÓN EN EL ORIGEN (Si es requerido cambiar el sentido por orientación)
    if orientacion.lower() == "vertical":
        techo = techo.rotate((0, 0, 0), (0, 0, 1), 90)
        # Rotamos usando el origen estricto como pivote para no desfasar coordenadas
    #     if posicion_puerta=="bottom":
    #         techo = techo.rotate((0, 0, 0), (0, 0, 1), 180)
    # else:
    #     if posicion_puerta=="bottom":
    #         techo = techo.rotate((0, 0, 0), (0, 0, 1), 180)

    # 3. TRASLACIÓN FINAL
    # Como la extrusión en YZ centra el objeto en X, sumamos la mitad de su ancho 
    # para que empiece exactamente en 'desplazamiento_x' y se alinee correctamente.
    
    techo = techo.translate((
        desplazamiento_x, 
        desplazamiento_y, 
        desfase_z
    ))

    return techo