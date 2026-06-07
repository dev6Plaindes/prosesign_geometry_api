import cadquery as cq

from bim.config_proyect import CONFIG_PROYECTO

def generate_techo(
    ensamblaje,
    largos_habitaciones: list,
    ancho_hab: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    largo_bloque_fijo: float,
    nivel=1,
    orientacion: str = "horizontal"
):
    """
    Genera la losa de techo para un bloque estructural y la añade al ensamblaje.
    Soporta orientación adaptativa en X (horizontal) e Y (vertical) mediante rotación nativa.
    """
    
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    alto = CONFIG_PROYECTO['alto_nivel']
    e_techo = CONFIG_PROYECTO['e_techo']
    e_muro = CONFIG_PROYECTO['e_muro']

    # El desfase base del piso actual
    desfase_z_piso = (nivel - 1) * altura_piso

    # La losa se posiciona encima de los muros de este nivel
    posicion_z_losa = desfase_z_piso + alto + (e_techo / 2)

    # 🔥 CORRECCIÓN DE MEDIDAS: Usamos el largo fijo y agregamos el grosor perimetral de muros
    largo_total_techo = largo_bloque_fijo
    ancho_total_techo = ancho_hab

    # Creación del sólido del techo (Generado inicialmente en el eje X)
    techo_solido = (
        cq.Workplane("XY")
        .box(largo_total_techo, ancho_total_techo, e_techo)
        .translate((
            largo_total_techo / 2 + desplazamiento_x,
            ancho_total_techo / 2 + desplazamiento_y,
            posicion_z_losa
        ))
    )

    # --- 🔥 ROTACIÓN DE EJE ADAPTATIVA ---
    # Si es vertical, rotamos el techo 90 grados usando el mismo punto de origen como pivote
    if orientacion.lower() == "vertical":
        pivote = (desplazamiento_x, desplazamiento_y, 0)
        techo_solido = techo_solido.rotate(pivote, (desplazamiento_x, desplazamiento_y, 1), 90)

    # Agregar al ensamblaje con un nombre único descriptor
    ensamblaje.add(techo_solido, name=f"Techo {sufijo_nombre} - Nivel {nivel}")