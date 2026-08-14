import cadquery as cq
from bim.adapters.shapely_to_cq import obtener_referencia_cuadrante, shapely_a_cadquery
from bim.calculate import calcular_desplazamiento_y, calcular_rango_centrado
from bim.capas import FactoryCapas
from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.balcony import create_balcony
from bim.creations.base_structure import create_structure
from bim.creations.pasadizo import create_corridor_slab
from bim.creations.techo import generate_techo
from bim.utils.logic import (
    acumulate_coords,
    div_logic,
    largos_for_piso_and_ambiente,
)
from bim.utils.step_to_json import (
    ensamblaje_to_array,
    polygon_a_mesh_array,
    terreno_a_mesh_array,
)
from bim.cuadrante_2do import build_2do_cuad

from bim.utils.transform_referencia import transformar_escena_con_referencia
from bim.max_cuadrante import (
    find_best_rectangle,
    normalizar_polygon,
    find_max_rect_for_angle,
)

def cuadrante_1(vertices_terreno, data_dict_ambientes, number_floors=None, vertices_rectangle=None, angle=None):

    terreno_poly = normalizar_polygon(vertices_terreno)
    RESUMEN_AREAS = []
    # [DOCUMENTACIÓN] Inicialización de variables para evitar NameError en flujos alternativos
    largos_inicial = []
    data_2do_cuadrante_builded = []
    # ==================================================================================
    # 1. MAXIMO CUADRANTE
    # [DOCUMENTACIÓN] Si se provee un rectángulo de cálculo guardado desde el frontend (vertices_rectangle y angle),
    # lo utilizamos directamente trasladándolo al origen usando el mismo offset de normalización del terreno.
    # Esto asegura consistencia 100%, evita fallos de generación y previene coordenadas gigantes (UTM) que arruinan la escala del render 3D.
    if vertices_rectangle and len(vertices_rectangle) >= 4:
        from shapely.geometry import Polygon
        from shapely import affinity
        
        # Calcular límites originales del terreno
        poly_orig = Polygon(vertices_terreno)
        minx, miny, _, _ = poly_orig.bounds
        
        best_rect = Polygon(vertices_rectangle)
        # Normalizar trasladando al origen local
        best_rect = affinity.translate(best_rect, xoff=-minx, yoff=-miny)
        best_angle = angle if angle is not None else 0.0
        best_area = best_rect.area
    else:
        best_rect, best_area, best_angle = find_best_rectangle(terreno_poly)
    
    cuadrante_1_cq = shapely_a_cadquery(best_rect)
    x_ref, y_ref = obtener_referencia_cuadrante(
        best_rect,
        best_angle
    )
    
    # resultado_array = terreno_a_mesh_array(vertices_terreno) # uncommented at bottom
    max_cuadrante_array = polygon_a_mesh_array(best_rect, "max_cuadrante")

    coords = list(best_rect.exterior.coords)
    x_min_absoluto, y_min_absoluto, x_max_absoluto, y_max_absoluto = best_rect.bounds
    # Puntos contiguos para calcular los lados
    p0 = coords[0]
    p1 = coords[1]
    p2 = coords[2]
    x_min_absoluto = coords[0][0]
    y_min_absoluto = coords[0][1]

    # Calcular la distancia real de los lados (Base y Altura)
    lado_1 = ((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2) ** 0.5
    lado_2 = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5

    ancho_terreno = lado_1
    largo_terreno = lado_2

    # Garantizar que Largo > Ancho
    # if largo_terreno > ancho_terreno:
    #     ancho_terreno, largo_terreno = largo_terreno, ancho_terreno
    #     print("aplicando angulo")
    #     best_angle += 90

    CONFIG_PROYECTO["largo_cuadrante"] = largo_terreno
    CONFIG_PROYECTO["ancho_cuadrante"] = ancho_terreno

    # ==================================================================================
    # 2. CONFIG PROYECTO Y VARIABLES PRINCIPALES

    largo_cuadrante = CONFIG_PROYECTO["largo_cuadrante"]
    ancho_cuadrante = CONFIG_PROYECTO["ancho_cuadrante"]
    ancho_pasadiso = CONFIG_PROYECTO["ancho_pasadiso"]
    ancho_hab_base = CONFIG_PROYECTO["ancho_hab"]
    alto = CONFIG_PROYECTO["alto_nivel"]
    e_muro = CONFIG_PROYECTO["e_muro"]
    ancho_col = CONFIG_PROYECTO["ancho_col"]

    # [DOCUMENTACIÓN] Validación inteligente de espacio mínimo para evitar desempaquetado de listas vacías y caídas de RQ worker.
    min_ancho_req = 2 * ancho_hab_base + 2 * ancho_pasadiso
    if ancho_cuadrante < min_ancho_req:
        raise ValueError(
            f"El terreno disponible es muy angosto: el cuadrante óptimo tiene {ancho_cuadrante:.2f}m de ancho, "
            f"pero la tipología escolar requiere un mínimo de {min_ancho_req:.2f}m."
        )

    min_largo_req = 2 * ancho_hab_base + 2 * ancho_pasadiso
    if largo_cuadrante < min_largo_req:
        raise ValueError(
            f"El terreno disponible es muy corto: el cuadrante óptimo tiene {largo_cuadrante:.2f}m de largo, "
            f"pero la tipología escolar requiere un mínimo de {min_largo_req:.2f}m."
        )

    # ==================================================================================
    # 3. MEDIDAS DE LOS AMBIENTES

    # ==================================================================================
    # 4. DIVISIONES PRINCIPALES Y POSICIONES DE LOS PABELLONES
    # Estas medidas se calculan a partir de las dimensiones del cuadrante y las configuraciones

    # divisiones horizontales
    areas_fase_1 = div_logic(
        [ancho_hab_base, ancho_pasadiso, "auto", ancho_pasadiso, ancho_hab_base],
        ancho_cuadrante,
    )
    ancho_inferior, _, ancho_sobrante, _, ancho_superior = areas_fase_1
    _, pas_prim, pos_centro, pas_sec, _ = acumulate_coords(areas_fase_1, 0)
    centro_disponible_ancho = round(abs(pos_centro[0] - pos_centro[1]), 3)

    # divisiones verticales
    areas_fase_2 = div_logic(
        [ancho_hab_base, ancho_pasadiso, "auto", ancho_pasadiso, ancho_hab_base],
        largo_cuadrante,
    )
    ancho_admin, _, ancho_sobrante_2, _, ancho_inicial = areas_fase_2
    _, pas_admin, pos_centro_2, pas_inicial, _ = acumulate_coords(areas_fase_2, 0)
    centro_disponible_largo = round(abs(pos_centro_2[0] - pos_centro_2[1]), 3)

    data_2do_cuadrante_builded_verif = False
    espacio_requerido_largo = 15 + 7.5
    if centro_disponible_largo < espacio_requerido_largo:
        data_2do_cuadrante_builded_verif = True

    # MEDIO
    pab_medio = [row for row in data_dict_ambientes if row["Pabellon"] == "Medio"]

    # SUM
    sum_amb = [row for row in pab_medio if "SUM" in row["Ambientes"]]

    if data_2do_cuadrante_builded_verif:
        # [DOCUMENTACIÓN] Se corrigió el cálculo de divisiones de fase 2 (Tarea 2 del Plan v3-Final):
        # 1. Se usa ancho_cuadrante en lugar de largo_cuadrante.
        # 2. Se mantiene el ancho del bloque Admin (ancho_hab_base, ancho_pasadiso) activo y se
        #    reduce a 0.1m el bloque Inicial (que se genera en el segundo cuadrante).
        areas_fase_2 = div_logic(
            [ancho_hab_base, ancho_pasadiso, "auto", 0.1, 0.1], ancho_cuadrante
        )
        ancho_admin, _, ancho_sobrante_2, _, ancho_inicial = areas_fase_2
        _, pas_admin, pos_centro_2, pas_inicial, _ = acumulate_coords(areas_fase_2, 0)

    largo_sum = 0

    # ==================================================================================
    # INICIALIZACION CAPAS
    ensamblaje_niveles = cq.Assembly(name="Emsamblaje por capas")
    factory_capas = FactoryCapas(
        ensamblaje=ensamblaje_niveles,
        degree_referencia=best_angle,
        x_referencia=x_ref,
        y_referencia=y_ref
    )

    # ==================================================================================
    # 5. DIVISIONES SECUNDARIAS Y POSICIONES DE LOS AMBIENTES

    # 5.1 PRIMARIA
    data_primaria = [
        row for row in data_dict_ambientes if row["Pabellon"] == "Izquierda"
    ]
    
    
    largos_primaria = largos_for_piso_and_ambiente(data_primaria, largo_cuadrante, name_pabellon="primaria") # DATA
        
    sum_largos_primaria = sum(item["largo"] for item in largos_primaria[0])
    desplazamiento_y_inf = calcular_desplazamiento_y(
        ancho_inferior, e_muro, ancho_cuadrante, borde="inferior"
    )
    pos_centro_primaria = calcular_rango_centrado(
        [0, largo_cuadrante], sum_largos_primaria
    )
    pos_centro_primaria = pos_centro_primaria[0]

    max_nivel_primaria = len(largos_primaria)

    # 5.2 SECUNDARIA
    data_secundaria = [
        row for row in data_dict_ambientes if row["Pabellon"] == "Derecha"
    ]
    largos_secundaria = largos_for_piso_and_ambiente(data_secundaria, largo_cuadrante, name_pabellon="secundaria") # DATA
    sum_largos_sec = sum(item["largo"] for item in largos_secundaria[0])

    desplazamiento_y_sup = calcular_desplazamiento_y(
        ancho_superior, e_muro, ancho_cuadrante, borde="superior"
    )
    pos_centro_secundaria = calcular_rango_centrado(
        [0, largo_cuadrante], sum_largos_sec
    )
    pos_centro_secundaria = pos_centro_secundaria[0]

    max_nivel_sec = len(largos_secundaria)

    # 5.3 INICIAL
    desplazamiento_x_ini = ancho_inferior + e_muro

    # Patio inicial
    patio_inicial = [row for row in pab_medio if "Patio Inicial" in row["Ambientes"]]
    patio_losa_dep = [row for row in pab_medio if "Losa Deportiva" in row["Ambientes"]]

    patio_inicial = patio_inicial[0] if patio_inicial else None
    patio_losa_dep = patio_losa_dep[0] if patio_losa_dep else None
    pos_patio = None

    if patio_inicial:
        pos_centro_patio_inicial = calcular_rango_centrado(
            pos_centro, patio_inicial["Largo"]
        )
        pos_patio = [
            pos_centro_2[0] + 0.4,
            pos_centro_2[0] + 0.4 + float(patio_inicial["Ancho"]),
        ]

    # [DOCUMENTACIÓN] Se independizó el cálculo de la losa deportiva (patio_losa_dep) de patio_inicial,
    # permitiendo que se posicione correctamente en el inicio del espacio disponible (pos_centro_2[0])
    # si el patio de inicial no está definido, evitando errores de UnboundLocalError.
    if patio_losa_dep:
        pos_centro_losa_dep = calcular_rango_centrado(
            pos_centro, patio_losa_dep["Largo"]
        )
        start_y = pos_patio[1] if pos_patio else pos_centro_2[0]
        pos_losa_dep = [
            start_y + 0.4,
            start_y + 0.4 + float(patio_losa_dep["Ancho"]),
        ]

    if not data_2do_cuadrante_builded_verif:
        # 2. INICIAL (Superior, Centrado en X)
        data_inicial = [
            row for row in data_dict_ambientes if row["Pabellon"] == "Inferior"
        ]
        largos_inicial = largos_for_piso_and_ambiente(data_inicial, ancho_sobrante, "inicial") # DATA
        sum_largos_inicial = sum(item["largo"] for item in largos_inicial[0])
        desplazamiento_y_sup = pos_centro[0]
        pos_centro_inicial = calcular_rango_centrado(pos_centro, sum_largos_inicial)[0]

        max_nivel_inicial = len(largos_inicial)

    # 5.5 ADMINISTRACION
    data_admin = [row for row in data_dict_ambientes if row["Pabellon"] == "Superior"]
    data_ept_cocina = [
        row
        for row in pab_medio
        if "Cocina" in row["Ambientes"] and "EPT" in row["Ambientes"]
    ]
    data_admin.extend(data_ept_cocina)
    largos_admin = largos_for_piso_and_ambiente(data_admin, ancho_sobrante, name_pabellon="administracion")
    sum_largo_admin = sum(item["largo"] for item in largos_admin[0])
    pos_centro_admin = calcular_rango_centrado(pos_centro, sum_largo_admin)
    max_nivel_admin = len(largos_admin)

    # ==================================================================================
    # INICIALIZACION ENSAMBLAJE
    ensamblaje = cq.Assembly(name="Proyecto")

    # Terreno
    terreno_cq = shapely_a_cadquery(terreno_poly)
    factory_capas.add_in_terreno(workplane=terreno_cq, nivel=1, name="Terreno")

    factory_capas.add_cuadrante(workplane=cuadrante_1_cq, name="Cuadrante")
    
    # CUADRANTE
    piso_solido = (
        cq.Workplane("XY")
        .box(largo_cuadrante, ancho_cuadrante, CONFIG_PROYECTO["espesor_piso"])
        .translate((
            largo_cuadrante/2,
            ancho_cuadrante/2,
            -0.1
        ))
    )

    # Agregamos el piso al ensamblaje
    ensamblaje.add(piso_solido, name="Cuadrante")
    factory_capas.add_in_capa_auto(workplane=piso_solido, nivel=1, name="Cuadrante test")

    # ========================================

    for index, nivel_data in enumerate(largos_primaria):
        nivel = index + 1
        largos_prim_numeros = [item["largo"] for item in nivel_data]
        nombres_ambientes = [item["ambiente"] for item in nivel_data]
        posicion_puerta = "top"
        create_structure(
            ensamblaje,
            largos_prim_numeros,
            ancho_inferior,
            pos_centro_primaria,
            desplazamiento_y_inf,
            "Inferior",
            posicion_puerta=posicion_puerta,
            nivel=index + 1,
            largo_bloque_fijo=sum_largos_primaria,
            max_nivel=max_nivel_primaria,
            names_ambientes=nombres_ambientes,
            factory_capas=factory_capas,
        )
        generate_techo(
            ensamblaje,
            largos_habitaciones=largos_prim_numeros,
            ancho_hab=ancho_inferior,
            desplazamiento_x=pos_centro_primaria,
            desplazamiento_y=desplazamiento_y_inf,
            largo_bloque_fijo=sum_largos_primaria,
            sufijo_nombre="Inferior Techo",
            nivel=nivel,
        )
        # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para usar
        # el origen de coordenadas y el ancho real del pabellón de Primaria de forma alineada.
        create_balcony(
            ensamblaje=ensamblaje,
            ancho_hab=ancho_inferior,
            desplazamiento_x=pos_centro_primaria,
            desplazamiento_y=desplazamiento_y_inf,
            sufijo_nombre="Modulo_A",
            largo_bloque_fijo=sum_largos_primaria,
            posicion_puerta=posicion_puerta,
            nivel=nivel,
            factory_capas=factory_capas
        )

    # [DOCUMENTACIÓN - TAREA 5]: Generación del Pasadizo para el Pabellón Primaria
    # Anteriormente esto estaba comentado, lo que ocasionaba que no se renderizaran 
    # los pasadizos y balcones principales en la vista 3D.
    create_corridor_slab(
        ensamblaje=ensamblaje,
        pos_x=[0.0, largo_cuadrante],
        pos_y=pas_prim,
        sufijo_nombre="Principal",
        nivel=1,
        factory_capas=factory_capas
    )

    for index, data_nivel in enumerate(largos_secundaria):
        nivel = index + 1
        largos_sec = [item["largo"] for item in data_nivel]
        names_sec = [item["ambiente"] for item in data_nivel]

        create_structure(
            ensamblaje,
            largos_sec,
            ancho_inferior,
            pos_centro_secundaria,
            pas_sec[1],
            "Secundaria",
            posicion_puerta="bottom",
            nivel=index + 1,
            largo_bloque_fijo=sum(largos_sec),
            max_nivel=max_nivel_sec,
            names_ambientes=names_sec,
            factory_capas=factory_capas,
        )
        generate_techo(
            ensamblaje,
            largos_habitaciones=largos_sec,
            ancho_hab=ancho_inferior,
            desplazamiento_x=pos_centro_secundaria,
            desplazamiento_y=pas_sec[1],
            largo_bloque_fijo=sum(largos_sec),
            sufijo_nombre="Secundaria Techo",
            nivel=nivel,
        )
        # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para usar
        # el origen de coordenadas y el ancho real del pabellón de Secundaria de forma alineada.
        create_balcony(
            ensamblaje=ensamblaje,
            ancho_hab=ancho_inferior,
            desplazamiento_x=pos_centro_secundaria,
            desplazamiento_y=pas_sec[1],
            sufijo_nombre="Sec",
            largo_bloque_fijo=sum_largos_sec,
            posicion_puerta="bottom",
            nivel=nivel,
            factory_capas=factory_capas
        )

    # Pasadizo Secundaria
    create_corridor_slab(
        ensamblaje=ensamblaje,
        pos_x=[0.0, largo_cuadrante],
        pos_y=pas_sec,
        sufijo_nombre="Secundaria",
        nivel=1,
        factory_capas=factory_capas
    )

    if sum_amb and not data_2do_cuadrante_builded_verif:
        sum_amb = sum_amb[0]
        pos_y = pos_centro_2[1] - 0.5
        pos_x = pos_centro[0] + 7.5
        largo_sum = sum_amb["Largo"]
        create_structure(
            ensamblaje,
            [float(sum_amb["Largo"])],
            float(sum_amb["Ancho"]),
            pos_y,
            pos_x,
            "SUM",
            posicion_puerta="bottom",
            nivel=1,
            largo_bloque_fijo=float(sum_amb["Ancho"]),
            orientacion="vertical",
            factory_capas=factory_capas,
        )

        generate_techo(
            ensamblaje,
            largos_habitaciones=[float(sum_amb["Largo"])],
            ancho_hab=float(sum_amb["Ancho"]),
            desplazamiento_x=pos_y,
            desplazamiento_y=pos_x,
            sufijo_nombre="SUM Techo",
            nivel=1,
            largo_bloque_fijo=float(sum_amb["Ancho"]),
            orientacion="vertical",
        )
        # [DOCUMENTACIÓN - TAREA 6]: Generación del Balcón para el ambiente SUM
        # Faltaba instanciar la función create_balcony, causando que este ambiente
        # complementario apareciera incompleto sin su respectiva estructura de balcón.
        # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para el SUM.
        create_balcony(
            ensamblaje=ensamblaje,
            ancho_hab=float(sum_amb["Ancho"]),
            desplazamiento_x=pos_y,
            desplazamiento_y=pos_x,
            sufijo_nombre="SUM Balcon",
            largo_bloque_fijo=float(sum_amb["Ancho"]),
            posicion_puerta="bottom",
            nivel=1,
            orientacion="vertical",
            factory_capas=factory_capas
        )

    if patio_inicial:
        if not data_2do_cuadrante_builded_verif:
            create_corridor_slab(
                ensamblaje=ensamblaje,
                pos_x=pos_patio,
                pos_y=pos_centro_patio_inicial,
                sufijo_nombre="Patio Inicial",
                nivel=1,
                factory_capas=factory_capas
            )

    # [DOCUMENTACIÓN] Se condicionó la creación de la losa deportiva a que esté definida en patio_losa_dep
    # para evitar errores UnboundLocalError si el usuario no la incluye en el aforo/ambientes del formulario.
    if patio_losa_dep:
        create_corridor_slab(
            ensamblaje=ensamblaje,
            pos_x=pos_losa_dep,
            pos_y=pos_centro_losa_dep,
            sufijo_nombre="Patio Primaria Secundaria",
            nivel=1,
            factory_capas=factory_capas
        )

    if not data_2do_cuadrante_builded_verif:
        for index, data_nivel in enumerate(largos_inicial):
            pos_puerta = "bottom"
            nivel = index + 1
            largos_m_inicial = [item["largo"] for item in data_nivel]
            names_inicial = [item["ambiente"] for item in data_nivel]
            create_structure(
                ensamblaje,
                largos_m_inicial,
                ancho_inferior,
                desplazamiento_x_ini,
                pos_centro_inicial,
                "Inicial",
                posicion_puerta=pos_puerta,
                nivel=nivel,
                largo_bloque_fijo=sum_largos_inicial,
                orientacion="vertical",
                max_nivel=max_nivel_inicial,
                names_ambientes=names_inicial,
                factory_capas=factory_capas,
            )
            generate_techo(
                ensamblaje,
                largos_habitaciones=largos_m_inicial,
                ancho_hab=ancho_inferior,
                desplazamiento_x=desplazamiento_x_ini,
                desplazamiento_y=pos_centro_inicial,
                sufijo_nombre="Inicial Techo",
                nivel=nivel,
                largo_bloque_fijo=sum_largos_inicial,
                orientacion="vertical",
            )
            # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para el Inicial.
            create_balcony(
                ensamblaje=ensamblaje,
                ancho_hab=ancho_inferior,
                desplazamiento_x=desplazamiento_x_ini,
                desplazamiento_y=pos_centro_inicial,
                sufijo_nombre="Inicial Balcon",
                largo_bloque_fijo=sum_largos_inicial,
                posicion_puerta=pos_puerta,
                nivel=nivel,
                orientacion="vertical",
                factory_capas=factory_capas
            )

        # [DOCUMENTACIÓN] Se asigna pas_admin como la coordenada X de Inicial para revertir el cruce de pasadizos.
        create_corridor_slab(
            ensamblaje=ensamblaje,
            pos_x=pas_admin,
            pos_y=pos_centro,
            sufijo_nombre="Inicial",
            nivel=1,
            factory_capas=factory_capas
        )

    for index, data_nivel in enumerate(largos_admin):
        largos_admin_m = [item["largo"] for item in data_nivel]
        names_admin = [item["ambiente"] for item in data_nivel]
        nivel = index + 1
        pos_x_admin = CONFIG_PROYECTO["largo_cuadrante"]
        pos_y_admin = pos_centro_admin[0]
        ancho_hab = CONFIG_PROYECTO["ancho_hab"]

        create_structure(
            ensamblaje,
            largos_admin_m,
            ancho_hab,
            pos_x_admin,
            pos_y_admin,
            "Admin",
            posicion_puerta="top",
            nivel=nivel,
            largo_bloque_fijo=sum_largo_admin,
            orientacion="vertical",
            max_nivel=max_nivel_admin,
            names_ambientes=names_admin,
            factory_capas=factory_capas,
        )
        generate_techo(
            ensamblaje,
            largos_habitaciones=largos_admin_m,
            ancho_hab=ancho_hab,
            desplazamiento_x=pos_x_admin,
            desplazamiento_y=pos_y_admin,
            sufijo_nombre="Admin Techo",
            nivel=nivel,
            largo_bloque_fijo=sum_largo_admin,
            orientacion="vertical",
        )
        # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para Admin
        # usando el pivote y coordenadas unificadas de pos_x_admin.
        create_balcony(
            ensamblaje=ensamblaje,
            ancho_hab=ancho_hab,
            desplazamiento_x=pos_x_admin,
            desplazamiento_y=pos_y_admin,
            sufijo_nombre="Admin Balcon",
            largo_bloque_fijo=sum_largo_admin,
            posicion_puerta="top",
            nivel=nivel,
            orientacion="vertical",
            factory_capas=factory_capas
        )

    # [DOCUMENTACIÓN] Se asigna pas_inicial como la coordenada X de Admin para revertir el cruce de pasadizos.
    create_corridor_slab(
        ensamblaje=ensamblaje,
        pos_x=pas_inicial,
        pos_y=pos_centro,
        sufijo_nombre="Admin",
        nivel=1,
        factory_capas=factory_capas
    )
    
    # IF 2DO CUADRANTE
    
    if centro_disponible_largo < espacio_requerido_largo:
        print("Usar otro cuadrante")
        # [DOCUMENTACIÓN] Se reemplazó find_next_best_rectangle por find_max_rect_for_angle a fin de
        # forzar el uso de best_angle, garantizando que el bloque central quede perfectamente paralelo
        # a los bloques perimetrales del primer cuadrante.
        remaining_terrain = terreno_poly.difference(best_rect)
        rect2_coords, area2 = find_max_rect_for_angle(remaining_terrain, best_angle, cell_size=0.2)
        angulo2 = best_angle
        x_min_absoluto_2, y_min_absoluto_2, _, _ = rect2_coords.bounds
        factory_capas.x_referencia = x_min_absoluto_2
        factory_capas.y_referencia = y_min_absoluto_2
        factory_capas.degree_referencia = angulo2
        data_2do_cuadrante_builded = build_2do_cuad(
            data_dict_ambientes, rect2_coords, factory_capas=factory_capas
        )

    datos = ensamblaje_to_array(ensamblaje)
    
    RESUMEN_AREAS.append({"inicial": largos_inicial})
    RESUMEN_AREAS.append({"primaria" : largos_primaria})
    RESUMEN_AREAS.append({"secundaria" : largos_secundaria})
    RESUMEN_AREAS.append({"admin" : largos_admin})
    
    cuadrante_max_and_terreno = []
    resultado_array = terreno_a_mesh_array(vertices_terreno)
    cuadrante_max_and_terreno.extend(resultado_array)
    cuadrante_max_and_terreno.extend(max_cuadrante_array)

    # move to origin
    move_to_origin = transformar_escena_con_referencia(datos, resultado_array)

    cuadrante_max_and_terreno.extend(move_to_origin)

    # INSERTAR 2DO CUADRANTE
    if data_2do_cuadrante_builded_verif:
        cuadrante_max_and_terreno.extend(data_2do_cuadrante_builded)

    # return vertices builded
    return cuadrante_max_and_terreno, ensamblaje, factory_capas, RESUMEN_AREAS
