import cadquery as cq
from shapely import Polygon

from bim.calculate import calcular_rango_centrado
from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.balcony import create_balcony
from bim.creations.base_construction import ComponenteConstruccion
from bim.creations.base_structure import create_structure
from bim.creations.pasadizo import create_corridor_slab
from bim.creations.techo import generate_techo
from bim.utils.logic import acumulate_coords, div_logic, largos_for_piso, translate_norm
from bim.utils.step_to_json import ensamblaje_to_array, polygon_a_mesh_array
from bim.utils.transform_referencia import transformar_escena_con_referencia
from bim.capas import FactoryCapas

def build_2do_cuad(data_dict_ambientes = [], cuadrante : Polygon = None, factory_capas : FactoryCapas = None, return_assembly: bool = False):
    ensamblaje = cq.Assembly(name="Proyecto")
    ancho_pasadiso = CONFIG_PROYECTO["ancho_pasadiso"]
    ancho_inferior = CONFIG_PROYECTO["ancho_hab"]
    
    # Formatear de nuevo las referencias
    coords = list(cuadrante.exterior.coords)

    # Puntos contiguos para calcular los lados
    p0 = coords[0]
    p1 = coords[1]
    p2 = coords[2]

    # Calcular la distancia real de los lados (Base y Altura)
    lado_1 = ((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)**0.5
    lado_2 = ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)**0.5

    # Asignar preliminarmente cuál es ancho y cuál largo
    ancho_cuadrante = lado_1
    largo_cuadrante = lado_2
    print("==================")
    print("2DO CUADRANTE")
    print(ancho_cuadrante, largo_cuadrante)
    print("==================")

    # 3. Aplicar tu lógica de orientación (Garantizar que Largo > Ancho)
    if largo_cuadrante < ancho_cuadrante:
        ancho_cuadrante, largo_cuadrante = largo_cuadrante, ancho_cuadrante
    
    piso_solido = (
        cq.Workplane("XY")
        .box(largo_cuadrante, ancho_cuadrante, CONFIG_PROYECTO["espesor_piso"])
        .translate(translate_norm(largo_cuadrante, ancho_cuadrante, -CONFIG_PROYECTO["espesor_piso"] / 2))
    )
    
    factory_capas.add_in_capa_auto(
            workplane = piso_solido,
            nivel = 1,
            name="Cuadrante 2"
        )
    
    # Agregamos el piso al ensamblaje
    ensamblaje.add(piso_solido, name="Losa Base Cuadrante 2")
    areas_inicial = div_logic([ancho_inferior, ancho_pasadiso, "auto"], largo_cuadrante)
    area_inicial, pas_inicial, pos_centro = acumulate_coords(areas_inicial, 0)
    area_inicial = [0,ancho_cuadrante]
    pab_medio = [
        row
        for row in data_dict_ambientes
        if row["Pabellon"] == "Medio"
    ]
    # Patio inicial
    patio_inicial = [
        row
        for row in pab_medio
        if "Patio Inicial" in row["Ambientes"]
    ]
    patio_losa_dep = [
        row
        for row in pab_medio
        if "Losa Deportiva" in row["Ambientes"]
    ]

    

    # 3. Bloque Inicial (En la franja central 'ancho_sobrante', pegado a la IZQUIERDA en X)
    desplazamiento_x_ini = ancho_inferior

    # 2. INICIAL (Superior, Centrado en X)
    data_inicial = [
        row
        for row in data_dict_ambientes
        if row["Pabellon"] == "Inferior"
    ]
    largos_inicial = largos_for_piso(data_inicial, largo_cuadrante)
    desplazamiento_y_sup = pos_centro[0]
    pos_centro_inicial = calcular_rango_centrado(area_inicial, sum(largos_inicial[0]))[0]

    if patio_inicial:
        patio_inicial = patio_inicial[0]
        patio_losa_dep = patio_losa_dep[0] if patio_losa_dep else None
        pos_centro_patio_inicial = calcular_rango_centrado(area_inicial, patio_inicial["Largo"])
        pos_centro_losa_dep = calcular_rango_centrado(pos_centro, patio_losa_dep["Largo"])

        pos_patio = [pos_centro[0] + 0.4 , pos_centro[0] + 0.4 + float(patio_inicial["Ancho"])]
        create_corridor_slab(
            ensamblaje=ensamblaje,
            pos_x=pos_patio,
            pos_y=pos_centro_patio_inicial,
            sufijo_nombre="Patio Inicial",
            nivel=1,
            factory_capas=factory_capas
        )
    max_nivel_inicial = len(largos_inicial)
    for index, largo_inicial in enumerate(largos_inicial):
        pos_puerta= "bottom"
        sum_largos_inicial = sum(largo_inicial)
        nivel = index + 1
        create_structure(
            ensamblaje,
            largo_inicial,
            ancho_inferior,
            desplazamiento_x_ini,
            pos_centro_inicial,
            "Inicial",
            posicion_puerta=pos_puerta,
            nivel=nivel,
            largo_bloque_fijo=sum_largos_inicial,
            orientacion="vertical",
            max_nivel=max_nivel_inicial,
            factory_capas=factory_capas
            )
        generate_techo(
                ensamblaje,
                largos_habitaciones=largo_inicial,
                ancho_hab=ancho_inferior,
                desplazamiento_x=desplazamiento_x_ini,
                desplazamiento_y=pos_centro_inicial,
                sufijo_nombre="Inicial Techo",
                nivel=nivel,
                largo_bloque_fijo=sum_largos_inicial,
                orientacion="vertical"
            )
        # [DOCUMENTACIÓN] Se actualizaron los parámetros de create_balcony para el Inicial del Cuadrante 2.
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

    create_corridor_slab(
        ensamblaje=ensamblaje,
        pos_x=pas_inicial,
        pos_y=area_inicial,
        sufijo_nombre="Inicial",
        nivel=1,
        factory_capas=factory_capas
    )
    sum_amb = [
        row
        for row in pab_medio
        if "SUM" in row["Ambientes"]
    ]
    if sum_amb:
        sum_amb = sum_amb[0]
        largo_sum=sum_amb["Largo"]
        ancho_sum=sum_amb["Ancho"]
        
        pos_sum_centrado_y = calcular_rango_centrado(area_inicial, ancho_sum)[0]
        pos_sum_x =float(ancho_sum) + CONFIG_PROYECTO["ancho_hab"] + CONFIG_PROYECTO["ancho_pasadiso"] + largo_sum
        create_structure(
                ensamblaje,
                [float(sum_amb["Largo"])],
                float(sum_amb["Ancho"]),
                pos_sum_x,
                pos_sum_centrado_y,
                "SUM",
                posicion_puerta="top",
                nivel=1,
                largo_bloque_fijo=float(sum_amb["Largo"]),
                orientacion="vertical",
                factory_capas=factory_capas
                
            )

        generate_techo(
                ensamblaje,
                largos_habitaciones=[float(sum_amb["Largo"])],
                ancho_hab=float(sum_amb["Ancho"]),
                desplazamiento_x=pos_sum_x,
                desplazamiento_y=pos_sum_centrado_y,
                sufijo_nombre="SUM Techo",
                nivel=1,
                largo_bloque_fijo=float(sum_amb["Largo"]),
                orientacion="vertical"
            )
    
    datos = ensamblaje_to_array(ensamblaje)
    data_2do_cuadrante = polygon_a_mesh_array(cuadrante, "2do cuadrante")

    move_to_origin = transformar_escena_con_referencia(datos, data_2do_cuadrante)
    
    if return_assembly:
        return move_to_origin, ensamblaje
    return move_to_origin