import cadquery as cq

from bim.config_proyect import CONFIG_PROYECTO

# Función que genera el techo asimétrico para zona climática z3 (sierra/selva).
# Cumbrera centrada, aleros simétricos de 1m, perfil con subida + bajada + plano.
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
    alero_izq: float = 1.00,
    largo_bloque_fijo: float = None
):
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']

    # [DOCUMENTACIÓN] Se reemplazaron las fracciones fijas 0.40/0.40/0.20 por una fórmula
    # que centra la cumbrera exactamente en el punto medio entre los dos aleros de 1m.
    # largo_subida = largo_bloque_fijo / 2  →  cumbrera en el centro del bloque
    # resto = (largo_bloque_fijo / 2) + alero_izq  →  mitad derecha + alero
    # largo_bajada = resto * 2/3, largo_plano = resto * 1/3  →  reparto proporcional
    # El techo resultante tiene aleros simétricos de 1m a cada lado del bloque.
    if largo_bloque_fijo is not None:
        alero_izq = 1.0
        largo_subida = largo_bloque_fijo / 2
        resto = (largo_bloque_fijo / 2) + alero_izq
        largo_bajada = resto * (2/3)
        largo_plano = resto * (1/3)

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

    # [DOCUMENTACIÓN] Se corrigió la alineación del techo Z3 traduciendo primero en Y por
    # (desplazamiento_y - e_muro + ancho_total_techo_y) para contrarrestar la extrusión en sentido negativo
    # y luego rotando alrededor del pivote (desplazamiento_x, desplazamiento_y, 0) si es orientación vertical.
    
    # 1. TRASLACIÓN HORIZONTAL INICIAL (para alinear con el bloque horizontal)
    techo = techo.translate((
        desplazamiento_x,
        desplazamiento_y - e_muro + ancho_total_techo_y,
        desfase_z
    ))

    # 2. LOGICA DE ROTACIÓN VERTICAL (rotación sobre el pivote de la edificación)
    if orientacion.lower() == "vertical":
        pivote = (desplazamiento_x, desplazamiento_y, 0)
        techo = techo.rotate(pivote, (desplazamiento_x, desplazamiento_y, 1), 90)

    ensamblaje.add(techo, name=f"Techo Especial Z3 {sufijo_nombre} - Nivel {nivel}", color=cq.Color("#4A4A4A"))