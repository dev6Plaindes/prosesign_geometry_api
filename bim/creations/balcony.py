import cadquery as cq

from bim.config_proyect import CONFIG_PROYECTO
from bim.capas import FactoryCapas
def create_balcony(
    ensamblaje,
    ancho_hab: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    largo_bloque_fijo: float,
    posicion_puerta: str = "bottom",
    nivel: int = 1,
    orientacion: str = "horizontal",
    ancho_balcon: float = 1.8,
    factory_capas : FactoryCapas = None
):
    """
    Genera e incorpora la losa de un balcón junto con su parapeto perimetral de 1.2m
    de altura al ensamblaje a partir del nivel 2.
    
    [DOCUMENTACIÓN] Se rediseñó el algoritmo para posicionar y modelar el balcón en 
    coordenadas locales alineadas con el bloque (origen en 0,0), aplicando traslación 
    y rotación globales de manera unificada. Esto previene desalineaciones en cuadrantes rotados o de orientación vertical.
    """
    
    # Validación base: Los balcones solo se construyen a partir del nivel 2
    if nivel < 2:
        return

    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']
    ancho_escalera = CONFIG_PROYECTO["ancho_escalera"]

    grosor_losa = 0.10
    alto_parapeto = 1.20
    desfase_z = (nivel - 1) * altura_piso

    # 1. Definir dimensiones y offsets locales (el edificio inicia en local (0,0))
    largo_total_balcon = largo_bloque_fijo + (ancho_escalera * 2)

    # 2. Determinar la posición en Y local según el lado de la puerta
    if posicion_puerta.lower() == "bottom":
        y_local_min = -ancho_balcon
        y_local_max = 0.0
        y_parapeto_frontal = -ancho_balcon + (e_muro / 2)
        centro_y_lateral = -ancho_balcon / 2 - (e_muro / 2)
    else:  # "top"
        y_local_min = ancho_hab
        y_local_max = ancho_hab + ancho_balcon
        y_parapeto_frontal = ancho_hab + ancho_balcon - (e_muro / 2)
        centro_y_lateral = ancho_hab + (ancho_balcon / 2) + (e_muro / 2)

    centro_x_balcon = largo_total_balcon / 2
    centro_y_balcon = (y_local_min + y_local_max) / 2
    centro_z_balcon = (grosor_losa / 2) + desfase_z

    # 3. Crear la losa base local
    balcon_solido = (
        cq.Workplane("XY")
        .box(largo_total_balcon, ancho_balcon, grosor_losa)
        .translate((centro_x_balcon, centro_y_balcon, centro_z_balcon))
    )

    # 4. Modelar el Parapeto perimetral local
    centro_z_parapeto = desfase_z + grosor_losa + (alto_parapeto / 2)

    # 4.1 Parapeto Frontal local
    parapeto_frontal = (
        cq.Workplane("XY")
        .box(largo_total_balcon, e_muro, alto_parapeto)
        .translate((centro_x_balcon, y_parapeto_frontal, centro_z_parapeto))
    )

    # 4.2 Parapetos Laterales locales
    largo_parapeto_lat = ancho_balcon - e_muro
    x_lateral_izq = (e_muro / 2)
    x_lateral_der = largo_total_balcon - (e_muro / 2)

    parapeto_lat_izq = (
        cq.Workplane("XY")
        .box(e_muro, largo_parapeto_lat, alto_parapeto)
        .translate((x_lateral_izq, centro_y_lateral, centro_z_parapeto))
    )

    parapeto_lat_der = (
        cq.Workplane("XY")
        .box(e_muro, largo_parapeto_lat, alto_parapeto)
        .translate((x_lateral_der, centro_y_lateral, centro_z_parapeto))
    )

    # 5. Unificar en un objeto local
    balcon_completo = (
        balcon_solido
        .union(parapeto_frontal)
        .union(parapeto_lat_izq)
        .union(parapeto_lat_der)
    )

    # 6. Aplicar la transformación global (Traslación + Rotación si es Vertical)
    # - Trasladar al origen global del bloque
    balcon_completo = balcon_completo.translate((desplazamiento_x, desplazamiento_y, 0))

    # - Rotar 90 grados alrededor del pivote del bloque si la orientación es Vertical
    if orientacion.lower() == "vertical":
        pivote = (desplazamiento_x, desplazamiento_y, 0)
        balcon_completo = balcon_completo.rotate(pivote, (desplazamiento_x, desplazamiento_y, 1), 90)

    # 7. Registrar en el ensamblaje general
    name_balcon = f"Balcon {sufijo_nombre} - Nivel {nivel}"
    ensamblaje.add(balcon_completo, name=name_balcon)
    
    factory_capas.add_in_capa_auto(balcon_completo, nivel=nivel, name=name_balcon)
    