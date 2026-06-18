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
    """
    
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']

    # Validación base: Los balcones solo se construyen a partir del nivel 2
    if nivel < 2:
        return

    grosor_losa = 0.10
    alto_parapeto = 1.20
    desfase_z = (nivel - 1) * altura_piso

    largo_total_balcon = largo_bloque_fijo + (CONFIG_PROYECTO["ancho_escalera"] * 2)
    ancho_total_hab = ancho_hab

    # 1. Determinar la posición en Y según el lado de la puerta (Plano horizontal base)
    if posicion_puerta.lower() == "bottom":
        centro_y_balcon = desplazamiento_y - (ancho_balcon / 2)
        # El frente largo del parapeto estará abajo en Y
        y_parapeto_frontal = desplazamiento_y - ancho_balcon + (e_muro / 2)
    elif posicion_puerta.lower() == "top":
        centro_y_balcon = desplazamiento_y + ancho_total_hab + (ancho_balcon / 2)
        # El frente largo del parapeto estará arriba en Y
        y_parapeto_frontal = desplazamiento_y + ancho_total_hab + ancho_balcon - (e_muro / 2)
    else:
        centro_y_balcon = desplazamiento_y - (ancho_balcon / 2)
        y_parapeto_frontal = desplazamiento_y - ancho_balcon + (e_muro / 2)

    centro_x_balcon = (largo_total_balcon / 2) + desplazamiento_x
    centro_z_balcon = (grosor_losa / 2) + desfase_z

    # 2. Crear la losa base del balcón
    balcon_solido = (
        cq.Workplane("XY")
        .box(largo_total_balcon, ancho_balcon, grosor_losa)
        .translate((centro_x_balcon, centro_y_balcon, centro_z_balcon))
    )

    # 3. Modelar el Parapeto perimetral (Ubicación Z: justo encima de la losa)
    centro_z_parapeto = desfase_z + grosor_losa + (alto_parapeto / 2)

    # 3.1 Parapeto Frontal (Muro largo)
    parapeto_frontal = (
        cq.Workplane("XY")
        .box(largo_total_balcon, e_muro, alto_parapeto)
        .translate((centro_x_balcon, y_parapeto_frontal, centro_z_parapeto))
    )

    # 3.2 Parapetos Laterales (Muros cortos de los extremos izquierdo y derecho)
    # Su largo en Y es igual al ancho del balcón menos el espesor del frontal para no solaparse
    largo_parapeto_lat = ancho_balcon - e_muro

    # El centro Y de las tapas laterales se desfasa un poco para alinearse con el frontal
    if posicion_puerta.lower() == "bottom":
        centro_y_lateral = centro_y_balcon - (e_muro / 2)
    else:
        centro_y_lateral = centro_y_balcon + (e_muro / 2)

    x_lateral_izq = desplazamiento_x + (e_muro / 2)
    x_lateral_der = desplazamiento_x + largo_total_balcon - (e_muro / 2)

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

    # 4. Unificar la losa con todos sus parapetos en un solo objeto monolítico
    balcon_completo = (
        balcon_solido
        .union(parapeto_frontal)
        .union(parapeto_lat_izq)
        .union(parapeto_lat_der)
    )

    # 5. Aplicar la rotación de 90 grados al conjunto completo si la orientación es Vertical
    if orientacion.lower() == "vertical":
        pivote = (desplazamiento_x, desplazamiento_y, 0)
        balcon_completo = balcon_completo.rotate(pivote, (desplazamiento_x, desplazamiento_y, 1), 90)

    # 6. Registrar en el ensamblaje general
    name_balcon = f"Balcon {sufijo_nombre} - Nivel {nivel}"
    ensamblaje.add(balcon_completo, name=name_balcon)
    
    factory_capas.add_in_capa_auto(balcon_completo, nivel=nivel, name=name_balcon)
    