import math
import cadquery as cq
from shapely.geometry import Polygon
from shapely import affinity

from bim.config_proyect import CONFIG_PROYECTO
from bim.capas import FactoryCapas

def create_balcony(
    ensamblaje,
    polygon: Polygon,
    sufijo_nombre: str,
    posicion_puerta: str = "bottom",
    nivel: int = 1,
    ancho_balcon: float = 1.8,
    factory_capas: FactoryCapas = None
):
    """
    Genera e incorpora la losa de un balcón junto con su parapeto perimetral de 1.2m
    de altura al ensamblaje a partir del nivel 2, basándose en un Polygon de Shapely.
    
    Analiza de forma automática el ángulo de inclinación espacial, dimensiones y 
    georreferenciación inversa siguiendo la lógica de control plano de 'create_structure'.
    """
    # Validación base: Los balcones solo se construyen a partir del nivel 2
    if nivel < 2:
        return

    # =========================================================================
    # 1. ANALIZAR GEOMETRÍA DEL POLYGON (INCLINACIÓN Y DIMENSIONES REALES)
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    # Calcular ángulo de inclinación nativo del terreno
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # Rotar temporalmente a 0° usando su propio centroide plano como pivote
    pivote_2d = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote_2d)
    
    # Extraer cotas reales del estado plano cartesiano alineado
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    largo_bloque_fijo = max_x - min_x
    ancho_hab = max_y - min_y
    
    # Desplazamientos locales equivalentes
    desplazamiento_x = min_x
    desplazamiento_y = min_y

    # =========================================================================
    # 2. CONFIGURACIÓN GENERAL DEL PROYECTO
    # =========================================================================
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']
    ancho_escalera = CONFIG_PROYECTO["ancho_escalera"]

    grosor_losa = 0.10
    alto_parapeto = 1.20
    desfase_z = (nivel - 1) * altura_piso

    # El balcón se extiende en los extremos para cubrir las zonas de escaleras fijas
    largo_total_balcon = largo_bloque_fijo + (ancho_escalera * 2)

    # =========================================================================
    # 3. DETERMINAR POSICIÓN LOCAL Y DEL BALCÓN (Según orientación de puerta)
    # =========================================================================
    if posicion_puerta.lower() == "bottom":
        y_local_min = desplazamiento_y - ancho_balcon
        y_local_max = desplazamiento_y
        y_parapeto_frontal = (desplazamiento_y - ancho_balcon) + (e_muro / 2)
        centro_y_lateral = desplazamiento_y - (ancho_balcon / 2) - (e_muro / 2)
    else:  # "top"
        y_local_min = desplazamiento_y + ancho_hab
        y_local_max = desplazamiento_y + ancho_hab + ancho_balcon
        y_parapeto_frontal = (desplazamiento_y + ancho_hab + ancho_balcon) - (e_muro / 2)
        centro_y_lateral = desplazamiento_y + ancho_hab + (ancho_balcon / 2) + (e_muro / 2)

    centro_x_balcon = (largo_total_balcon / 2) + desplazamiento_x
    centro_y_balcon = (y_local_min + y_local_max) / 2
    centro_z_balcon = (grosor_losa / 2) + desfase_z

    # =========================================================================
    # 4. MODELADO DE SÓLIDOS (En estado plano de trabajo)
    # =========================================================================
    # 4.1 Losa base
    balcon_solido = (
        cq.Workplane("XY")
        .box(largo_total_balcon, ancho_balcon, grosor_losa)
        .translate((centro_x_balcon, centro_y_balcon, centro_z_balcon))
    )

    # 4.2 Parapeto perimetral
    centro_z_parapeto = desfase_z + grosor_losa + (alto_parapeto / 2)

    # Parapeto Frontal
    parapeto_frontal = (
        cq.Workplane("XY")
        .box(largo_total_balcon, e_muro, alto_parapeto)
        .translate((centro_x_balcon, y_parapeto_frontal, centro_z_parapeto))
    )

    # Parapetos Laterales
    largo_parapeto_lat = ancho_balcon - e_muro
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

    # 4.3 Unificación monolítica plana
    balcon_completo = (
        balcon_solido
        .union(parapeto_frontal)
        .union(parapeto_lat_izq)
        .union(parapeto_lat_der)
    )

    # =========================================================================
    # 5. GEORREFERENCIACIÓN INVERSA (Rotación al ángulo real de la Tierra)
    # =========================================================================
    pivote_3d = (pivote_2d.x, pivote_2d.y, 0)
    eje_rotacion_z = (pivote_2d.x, pivote_2d.y, 1)

    balcon_completo = balcon_completo.rotate(pivote_3d, eje_rotacion_z, angulo_grados)

    # =========================================================================
    # 6. INYECCIÓN EN ENSAMBLAJE Y SISTEMA DE CAPAS
    # =========================================================================
    name_balcon = f"Balcon {sufijo_nombre} - Nivel {nivel}"
    
    # Blindaje de color: Formato decimal RGBA para evitar fallos de compatibilidad en Open CASCADE
    # Tono gris concreto claro (#BCBDBE aproximado)
    color_gris_concreto = cq.Color(0.74, 0.74, 0.74, 1.0)
    
    ensamblaje.add(balcon_completo, name=name_balcon, color=color_gris_concreto)
    
    if factory_capas:
        factory_capas.add_in_capa_auto(workplane=balcon_completo, nivel=nivel, name=name_balcon)