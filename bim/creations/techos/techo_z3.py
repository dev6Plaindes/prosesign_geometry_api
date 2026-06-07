import math
import cadquery as cq

# 1. ENTORNO DE PRUEBA LOCAL (Simula tus importaciones bim)
CONFIG_PROYECTO = {
    'alto_nivel': 2.80,  
    'e_muro': 0.15,
    'ancho_escalera': 1.00
}

# 2. LA FUNCIÓN CON LA GEOMETRÍA ASIMÉTRICA Z3 RELLENA (BASE PLANA)
def create_techo_z3(
    ensamblaje,
    ancho_hab: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    posicion_puerta: str = "bottom",
    nivel: int = 1,
    orientacion: str = "horizontal",
    espesor_techo: float = 0.25,
    alto_cumbrera: float = 1.35,
    largo_subida: float = 4.50,
    largo_bajada: float = 4.50,
    largo_plano: float = 1.80,
    alero_izq: float = 1.00
):
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']

    desfase_z = nivel * altura_piso 
    ancho_total_techo_y = ancho_hab + (e_muro * 2)
    
    if posicion_puerta.lower() == "bottom":
        y_base = desplazamiento_y
    elif posicion_puerta.lower() == "top":
        y_base = desplazamiento_y + e_muro
    else:
        y_base = desplazamiento_y

    # Coordenadas X calculadas
    x0 = -alero_izq
    x1 = 0.0
    x2 = largo_subida
    x3 = largo_subida + largo_bajada
    x4 = x3 + largo_plano

    # CORRECCIÓN: Usamos abs(x0) para que la pendiente sume altura hacia la izquierda en lugar de restar
    z_alero_exterior = (abs(x0) / x2) * alto_cumbrera + espesor_techo  

    # --- PERFIL HORARIO CONTINUO LIMPIO ---
    puntos_perfil = [
        (x0, 0),                              # 1. Inicio en esquina inferior izquierda
        (x0, z_alero_exterior),               # 2. Sube vertical hasta la punta del alero (Ahora da un Z positivo de +0.55)
        (x2, alto_cumbrera + espesor_techo),  # 3. Sube en diagonal a la cumbrera máxima
        (x3, espesor_techo),                  # 4. Baja en diagonal al quiebre plano
        (x4, espesor_techo),                  # 5. Avanza horizontal por el tramo plano
        (x4, 0),                              # 6. Baja vertical al piso en el extremo derecho
        (x0, 0)                               # 7. Cierra recto por todo el piso hasta el punto inicial
    ]

    techo = (
        cq.Workplane("XZ")
        .polyline(puntos_perfil)
        .close()
        .extrude(ancho_total_techo_y)
    )

    # 2. LOGICA DE ROTACIÓN SEGURA
    if orientacion.lower() == "vertical":
        techo = techo.rotate((0,0,0), (0,0,1), 90)
        
    # 3. TRASLACIÓN FINAL
    techo = techo.translate((desplazamiento_x, y_base + (ancho_total_techo_y / 2), desfase_z))

    ensamblaje.add(techo, name=f"Techo Especial Z3 {sufijo_nombre} - Nivel {nivel}")