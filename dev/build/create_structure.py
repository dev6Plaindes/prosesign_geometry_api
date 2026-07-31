import math
import cadquery as cq
from shapely.geometry import Polygon, box
from shapely import affinity

from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.doors import _generate_door_geometry
from bim.creations.escaleras import create_stairs, get_stair_dimensions
from bim.creations.techos.techo_z1 import create_techo_z_1
from bim.creations.techos.techo_z3 import create_techo_z3
from bim.creations.vigas import _generate_beams_geometry
from bim.creations.windows import _generate_windows_by_room
from bim.utils.algoritm_distibution import calcular_posiciones_columnas, encontrar_largo_equilibrado
from dev.assemblys.capas import FactoryCapas

def create_structure(
    ensamblaje,
    polygon: Polygon,
    largos_habitaciones: list,
    sufijo_nombre: str,
    posicion_puerta: str = "bottom",
    nivel=1,
    max_nivel=1,
    names_ambientes: list = None,
    factory_capas: FactoryCapas = None
):
    """
    Construye UN solo bloque modular de ambientes variables basándose en un Polygon de Shapely.
    Determina de forma automática el largo (lado mayor), el ancho, y la inclinación espacial.
    Integra columnas, vigas, muros, puertas, ventanas, escaleras y techos de manera georreferenciada.
    """
    # =========================================================================
    # 1. ANALIZAR GEOMETRÍA DEL POLYGON (INCLINACIÓN Y DIMENSIONES REALES)
    # =========================================================================
    coords = list(polygon.exterior.coords)
    p0, p1 = coords[0], coords[1]
    
    # Calcular ángulo de inclinación nativo
    angulo_rad = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    angulo_grados = math.degrees(angulo_rad)
    if angulo_grados > 90:
        angulo_grados -= 180
    elif angulo_grados < -90:
        angulo_grados += 180

    # Rotar temporalmente a 0° usando su propio centroide como pivote
    pivote_2d = polygon.centroid
    poly_alineado = affinity.rotate(polygon, -angulo_grados, origin=pivote_2d)
    
    # Obtener cotas del estado plano (Alineado con los ejes cartesianos del CAD)
    min_x, min_y, max_x, max_y = poly_alineado.bounds
    dim_x = max_x - min_x
    dim_y = max_y - min_y

    # Asegurarse de que el "largo" es la dimensión mayor, alineada con el eje X de trabajo
    if dim_y > dim_x:
        # La dimensión Y es más larga, rotamos 90 grados para que sea la X
        poly_alineado = affinity.rotate(poly_alineado, 90, origin=poly_alineado.centroid)
        angulo_grados -= 90 # Ajustamos el ángulo de rotación final para la georreferenciación inversa
        # Recalculamos las cotas
        min_x, min_y, max_x, max_y = poly_alineado.bounds
        largo_bloque_fijo = max_x - min_x
        ancho_hab = max_y - min_y
    else:
        largo_bloque_fijo = dim_x
        ancho_hab = dim_y
    
    # Desplazamientos locales equivalentes
    desplazamiento_x = min_x
    desplazamiento_y = min_y

    # =========================================================================
    # 2. CONFIGURACIÓN GENERAL DEL PROYECTO
    # =========================================================================
    altura_piso = CONFIG_PROYECTO['alto_nivel']
    alto = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']
    ancho_col = CONFIG_PROYECTO['ancho_col']
    desfase_z = (nivel - 1) * altura_piso

    largo_total_hab = largo_bloque_fijo
    ancho_total_hab = ancho_hab
    ancho_interior = ancho_hab - (e_muro * 2)

    # =========================================================================
    # 3. CONSTRUCCIÓN DE MUROS BASE (En coordenadas alineadas de trabajo)
    # =========================================================================
    muros_locales = (
        cq.Workplane("XY")
        .box(largo_total_hab, ancho_total_hab, alto)
        .translate((
            largo_total_hab / 2 + desplazamiento_x,
            ancho_total_hab / 2 + desplazamiento_y,
            (alto / 2) + desfase_z
        ))
    )

    # =========================================================================
    # 4. CÁLCULO DE COLUMNAS ALINEADAS
    # =========================================================================
    resultado = encontrar_largo_equilibrado(
        largo_total=largo_total_hab,
        min_largo=4.0,
        max_largo=5.5,
        grosor_columna=ancho_col
    )

    cantidad_columnas = resultado["numero_columnas"]
    espacios_m = resultado['largo_individual_exacto']

    pos_columnas = calcular_posiciones_columnas(
        cantidad_columnas,
        ancho_col,
        espacios_m
    )

    esquinas_globales = set()
    pos_y_inferior = desplazamiento_y + (ancho_col / 2)
    pos_y_superior = desplazamiento_y + ancho_total_hab - (ancho_col / 2)

    for col_inicio, col_fin in pos_columnas:
        centro_x_columna = ((col_inicio + col_fin) / 2) + desplazamiento_x
        esquinas_globales.update([
            (centro_x_columna, pos_y_inferior),
            (centro_x_columna, pos_y_superior)
        ])

    # =========================================================================
    # 5. DIVISIÓN Y REDIMENSIONAMIENTO INTERIOR DE AULAS
    # =========================================================================
    num_hab = len(largos_habitaciones)
    espacio_muros_interiores = (num_hab + 1) * e_muro
    espacio_neto_disponible = largo_total_hab - espacio_muros_interiores
    suma_largos_originales = sum(largos_habitaciones)

    largos_corregidos = [
        (l / suma_largos_originales) * espacio_neto_disponible
        for l in largos_habitaciones
    ]

    # =========================================================================
    # 6. GENERACIÓN DE GEOMETRÍAS INTERNAS (Aulas, Puertas, Ventanas)
    # =========================================================================
    borde_x = desplazamiento_x + e_muro
    puertas_lista_local = []
    ventanas_cortadores = []
    ventanas_paneles_local = []
    geometrias_ambientes_local = []

    for idx, l_hab in enumerate(largos_corregidos):
        centro_x = borde_x + (l_hab / 2)
        centro_y = desplazamiento_y + e_muro + (ancho_interior / 2)

        # A) Vaciado Interior (Cortador)
        cortador = (
            cq.Workplane("XY")
            .box(l_hab, ancho_interior, alto + 1)
            .translate((
                centro_x,
                centro_y,
                (alto / 2) + desfase_z
            ))
        )
        muros_locales = muros_locales.cut(cortador)
        
        # B) Asignación de Nombre y Geometría de Ambiente para Leyenda
        if names_ambientes and idx < len(names_ambientes):
            ambiente_base = names_ambientes[idx]
        else:
            ambiente_base = f"Ambiente_{idx + 1}"
        
        nombre_ambiente_formato = f"[{ambiente_base} {idx + 1}]"

        geometria_ambiente = (
            cq.Workplane("XY")
            .box(l_hab, ancho_interior, alto)
            .translate((
                centro_x,
                centro_y,
                (alto / 2) + desfase_z
            ))
        )
        geometrias_ambientes_local.append((geometria_ambiente, nombre_ambiente_formato))

        # C) Geometría de Puertas (Con alternancia de lado)
        lado_puerta = "right" if idx % 2 == 1 else "left"
        cortador_vano, bloque_puerta, rango_puerta_x = _generate_door_geometry(
            posicion_puerta=posicion_puerta,
            borde_x=borde_x,
            l_hab=l_hab,
            desplazamiento_y=desplazamiento_y,
            ancho_total_hab=ancho_total_hab,
            desfase_z=desfase_z,
            pos_columnas=pos_columnas,
            desplazamiento_x=desplazamiento_x,
            lado_puerta=lado_puerta
        )

        if cortador_vano and bloque_puerta:
            muros_locales = muros_locales.cut(cortador_vano)
            puertas_lista_local.append(bloque_puerta)

        # D) Ventanas Frontales y Traseras (Ventilación Cruzada)
        cortadores_w, paneles_w = _generate_windows_by_room(
            inicio_hab_x=borde_x,
            fin_hab_x=borde_x + l_hab,
            desplazamiento_y=desplazamiento_y,
            ancho_total_hab=ancho_total_hab,
            desfase_z=desfase_z,
            pos_columnas=pos_columnas,
            desplazamiento_x=desplazamiento_x,
            posicion_puerta=posicion_puerta,
            rango_puerta_x=rango_puerta_x
        )
        ventanas_cortadores.extend(cortadores_w)
        ventanas_paneles_local.extend(paneles_w)

        posicion_puerta_atras = "top" if posicion_puerta.lower() == "bottom" else "bottom"
        cortadores_w_atras, paneles_w_atras = _generate_windows_by_room(
            inicio_hab_x=borde_x,
            fin_hab_x=borde_x + l_hab,
            desplazamiento_y=desplazamiento_y,
            ancho_total_hab=ancho_total_hab,
            desfase_z=desfase_z,
            pos_columnas=pos_columnas,
            desplazamiento_x=desplazamiento_x,
            posicion_puerta=posicion_puerta_atras,
            rango_puerta_x=None
        )
        ventanas_cortadores.extend(cortadores_w_atras)
        ventanas_paneles_local.extend(paneles_w_atras)

        borde_x = borde_x + l_hab + e_muro

    # =========================================================================
    # 7. CORTES FINALES DE VENTANAS Y ENSAMBLAJE DE ESTRUCTURA SOPORTE
    # =========================================================================
    for cortador_ventana in ventanas_cortadores:
        muros_locales = muros_locales.cut(cortador_ventana)

    # Columnas
    altura_total = alto + CONFIG_PROYECTO["ancho_viga"]
    columnas_final = (
        cq.Workplane("XY")
        .pushPoints(list(esquinas_globales))
        .box(ancho_col, ancho_col, altura_total)
        .translate((0, 0, (altura_total / 2) + desfase_z))
    )

    muros_final = muros_locales.cut(columnas_final)

    # Vigas
    vigas_final = _generate_beams_geometry(
        pos_columnas=pos_columnas,
        desplazamiento_x=desplazamiento_x,
        desplazamiento_y=desplazamiento_y,
        ancho_total_hab=ancho_total_hab,
        ancho_col=ancho_col,
        alto_muro=alto,
        desfase_z=desfase_z
    )

    # =========================================================================
    # 8. ROTACIÓN DE VOLÚMENES COMPLETOS AL ÁNGULO REAL DEL TERRENO
    # =========================================================================
    pivote_3d = (pivote_2d.x, pivote_2d.y, 0)
    eje_rotacion_z = (pivote_2d.x, pivote_2d.y, 1)

    muros_final = muros_final.rotate(pivote_3d, eje_rotacion_z, angulo_grados)
    columnas_final = columnas_final.rotate(pivote_3d, eje_rotacion_z, angulo_grados)
    vigas_final = vigas_final.rotate(pivote_3d, eje_rotacion_z, angulo_grados)

    puertas_lista = [p.rotate(pivote_3d, eje_rotacion_z, angulo_grados) for p in puertas_lista_local]
    ventanas_paneles_lista = [w.rotate(pivote_3d, eje_rotacion_z, angulo_grados) for w in ventanas_paneles_local]

    # =========================================================================
    # 9. ESCALERAS (Rotadas y Desplazadas con Precisión)
    # =========================================================================
    if nivel > 1:
        nivel_escalera = nivel - 1
        
        # Obtener las dimensiones reales de la escalera para el posicionamiento
        stair_dims = get_stair_dimensions(huella=0.28, contrahuella_max=0.17)
        largo_escalera_x = stair_dims['largo_total_x']
        ancho_escalera_y = stair_dims['ancho_total_y']

        # Las calculamos de forma local alineada y dejamos que la rotación se calcule
        # Se ubica la escalera fuera del bloque, pegada al extremo izquierdo.
        # NOTA: Con orientacion="vertical", las dimensiones se invierten en el plano XY.
        # El ancho en el eje X corresponde a 'ancho_escalera_y'.
        desplazamiento_x_escalera = desplazamiento_x - ancho_escalera_y
        if posicion_puerta == "bottom":
            # Se ubica fuera del bloque, en el lado de las puertas ('bottom')
            # El largo en el eje Y corresponde a 'largo_escalera_x'.
            desplazamiento_y_escalera = desplazamiento_y - largo_escalera_x
        else:
            # Se ubica fuera del bloque, en el lado de las puertas ('top')
            desplazamiento_y_escalera = desplazamiento_y + ancho_hab

        # Se crea la escalera con su propia lógica de orientación y posición
        escalera = create_stairs(
            ensamblaje=ensamblaje,
            ancho_hab=ancho_hab,
            desplazamiento_x=desplazamiento_x_escalera,
            desplazamiento_y=desplazamiento_y_escalera,
            sufijo_nombre=sufijo_nombre,
            posicion_puerta=posicion_puerta,
            nivel=nivel_escalera,
            orientacion="vertical",
            huella=0.28,
            contrahuella_max=0.17,
            desplazamiento_x_bloque=desplazamiento_x,
            desplazamiento_y_bloque=desplazamiento_y
        )
        # Rotamos la escalera terminada sobre el mismo eje de normalización
        escalera = escalera.rotate(pivote_3d, eje_rotacion_z, angulo_grados)
        
        name_obj = f"Escalera {sufijo_nombre} - Nivel {nivel_escalera}"
        factory_capas.add_in_capa_auto(workplane=escalera, nivel=nivel - 1, name=name_obj)
        
        ensamblaje.add(escalera, name=name_obj, color=cq.Color("#BCBDBE"))

    # =========================================================================
    # 10. GENERACIÓN DE TECHOS
    # =========================================================================
    if max_nivel == nivel:
        if CONFIG_PROYECTO.get("zona_climatica") == "z1":
            techo = create_techo_z_1(
                ancho_techo=largo_bloque_fijo,
                desplazamiento_x=desplazamiento_x,
                desplazamiento_y=desplazamiento_y,
                sufijo_nombre=sufijo_nombre,
                posicion_puerta=posicion_puerta,
                largo_inclinado=ancho_hab,
                nivel=nivel,
                orientacion="horizontal"
            )
            techo = techo.rotate(pivote_3d, eje_rotacion_z, angulo_grados)
            ensamblaje.add(techo, name=f"Techo Especial Z1 {sufijo_nombre} - Nivel {nivel}", color=cq.Color("#4A4A4A"))
            
        elif CONFIG_PROYECTO.get("zona_climatica") == "z3":
            # Guardamos temporalmente el estado del ensamblaje antes de llamar a techo_z3
            # para interceptar los sólidos generados y aplicarles la rotación final
            techos_previos = set(ensamblaje.children)
            
            create_techo_z3(
                ensamblaje=ensamblaje,
                ancho_hab=ancho_hab,
                desplazamiento_x=desplazamiento_x,
                desplazamiento_y=desplazamiento_y,
                sufijo_nombre=sufijo_nombre,
                posicion_puerta=posicion_puerta,
                nivel=nivel,
                orientacion="horizontal",
                largo_bloque_fijo=largo_bloque_fijo
            )
            
            techos_nuevos = set(ensamblaje.children) - techos_previos
            for techo_obj in techos_nuevos:
                # Rotamos espacialmente cada componente del techo z3
                techo_obj.obj = techo_obj.obj.rotate(pivote_3d, eje_rotacion_z, angulo_grados)

    # =========================================================================
    # 11. REGISTRO Y ENSAMBLAJE FINAL DE LOS AMBIENTES E INDIVIDUALES
    # =========================================================================
    # Sombreados de los ambientes internos
    for geom_amb, nombre_amb in geometrias_ambientes_local:
        geom_amb_rotada = geom_amb.rotate(pivote_3d, eje_rotacion_z, angulo_grados)        
        nombre_final_ambiente = f"{nombre_amb} {sufijo_nombre} - Nivel {nivel}"
        ensamblaje.add(
            geom_amb_rotada, 
            name=nombre_final_ambiente,
            color=cq.Color(0.85, 0.9, 1.0, 0.5) # Azul claro semitransparente
        )
        if factory_capas:
            factory_capas.add_in_capa_auto(workplane=geom_amb_rotada, nivel=nivel, name=nombre_final_ambiente)

    # Muros
    ensamblaje.add(muros_final, name=f"Muros {sufijo_nombre} - Nivel {nivel}", color=cq.Color("#6E6E6E"))
    factory_capas.add_in_capa_auto(workplane=muros_final, nivel=nivel, name=f"Muros {sufijo_nombre} - Nivel {nivel}")

    # Columnas
    ensamblaje.add(columnas_final, name=f"Columnas {sufijo_nombre} - Nivel {nivel}", color=cq.Color("#4A4A4A"))
    factory_capas.add_columna_in_capa(workplane=columnas_final, nivel=nivel, name=f"Columnas {sufijo_nombre} - Nivel {nivel}")

    # Vigas
    ensamblaje.add(vigas_final, name=f"Vigas {sufijo_nombre} - Nivel {nivel}", color=cq.Color("#4A4A4A"))
    factory_capas.add_viga_in_capa(workplane=vigas_final, nivel=nivel, name=f"Vigas {sufijo_nombre} - Nivel {nivel}")

    # Carpintería (Puertas y Ventanas)
    for i, puerta_solido in enumerate(puertas_lista):
        ensamblaje.add(puerta_solido, name=f"Puerta {sufijo_nombre} - Nivel {nivel} - {i+1}", color=cq.Color("#1A0E08"))

    for j, ventana_solido in enumerate(ventanas_paneles_lista):
        ensamblaje.add(ventana_solido, name=f"Ventana {sufijo_nombre} - Nivel {nivel} - {j+1}", color=cq.Color(0.29, 0.29, 0.29, 0.5))