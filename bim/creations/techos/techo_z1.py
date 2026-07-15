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

    # Se ajusta el desfase_z para que calce exacto sobre los muros sin espacio sobrante
    desfase_z = nivel * altura_piso
    
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
    print(f"[DEBUG techo_z1] sufijo={sufijo_nombre} posicion_puerta={posicion_puerta} orientacion={orientacion}")
    print(f"[DEBUG techo_z1]   ancho_total_techo_x={ancho_total_techo_x}  largo_inclinado={largo_inclinado}")
    print(f"[DEBUG techo_z1]   puntos_perfil={puntos_perfil}")
    print(f"[DEBUG techo_z1]   y_base={y_base}  desplazamiento_y={desplazamiento_y}")
    print(f"[DEBUG techo_z1]   rotacion_180={'SI' if posicion_puerta.lower() == 'bottom' else 'NO'}")

    # 1. CREACIÓN EN EL ORIGEN (Usando YZ para invertir largo por ancho)
    techo = (
        cq.Workplane("YZ")
        .polyline(puntos_perfil)
        .close()
        # Se extruye en el eje X de forma simétrica (-ancho/2 a +ancho/2)
        .extrude(ancho_total_techo_x) 
    )
    
    # 2. ROTACIÓN EN EL ORIGEN (Si es requerido cambiar el sentido por orientación)
    
    # 2.1 ROTACIÓN LOCAL (180 grados si es 'bottom')
    # Esto garantiza que el voladizo plano de 1.80m siempre apunte hacia el pasadizo.
    if posicion_puerta.lower() == "bottom":
        centro_x = ancho_total_techo_x / 2
        centro_y = largo_inclinado / 2
        techo = techo.rotate((centro_x, centro_y, 0), (centro_x, centro_y, 1), 180)

    # 2.2 ROTACIÓN VERTICAL
    if orientacion.lower() == "vertical":
        techo = techo.rotate((0, 0, 0), (0, 0, 1), 90)

    # 3. TRASLACIÓN FINAL
    # Como la extrusión en YZ centra el objeto en X, sumamos la mitad de su ancho 
    # para que empiece exactamente en 'desplazamiento_x' y se alinee correctamente.
    
    techo = techo.translate((
        desplazamiento_x, 
        desplazamiento_y, 
        desfase_z
    ))

    return techo