import cadquery as cq
import os
import io
import logging

from bim.pabellones_to_csv import exportar_pabellones_a_csv
from bim.utils.dividir_sum import ajustar_dividir_sum
from bim.utils.posicion_puerta import determinar_posicion_puerta
from bim.v2.procesar_pabellones import _procesar_layout_multiples_pabellones
from bim.utils import view_ancho_largo_polygon
from bim.utils.view_ancho_largo_polygon import imprimir_dimensiones_poligono
from dev.assemblys.capas import FactoryCapas
from dev.assemblys.cuadrante import build_cuadrante_shapely
from dev.assemblys.terreno_assembly import terreno_assembly

from dev.build.create_balcony import create_balcony
from dev.build.create_structure import create_structure
from dev.build.block import new_block
from dev.config import CONFIG_PROYECTO
from dev.data.transform import agrupar_ambientes_por_pabellon
from dev.normalize import normalizar_datos_terreno
from dev.types import DataAmbientes
from dev.utils.calculate_medidas import (
    largos_for_piso_and_ambiente,
    limpiar_distribucion_para_resumen,
    obtener_polygon_real_del_piso,
)
from dev.utils.largo_ancho_cuadrante import obtener_dimensiones_cuadrante
from bim.upload_aws_file import subir_archivo_a_s3, obtener_archivo_en_binario
from bim.creations.escaleras import crear_poligono_escalera
from dev.utils.tools import (
    div_logic,
    div_logic_with_spacing,
    obtener_sub_polygon_centrado,
)


# Generacion del cuadrante 1 en el plano Version 2
# Con shapely para exactitud y poligonos en todos los angulos posibles
def cuadrante_1_v2(vertices_terreno, vertices_cuadrante, ambientes, id_project: int):
    mi_modelo = cq.Assembly(name="Proyecto Automatizado")

    ensamblaje_niveles = cq.Assembly(name="Emsamblaje por capas")

    # Refactorizar
    factory_capas = FactoryCapas(
        ensamblaje=ensamblaje_niveles,
    )

    # 2. Obtenemos tus vértices UTM de prueba en bruto (UTM masivos)
    cuadrante_maximo = vertices_cuadrante
    terreno_real = vertices_terreno

    # 3. Normalizar los datos al origen común (0, 0) de forma centralizada
    # 'origen_utm' contiene el punto (min_x, min_y) real de la parcela en la Tierra
    cuadrante_norm, terreno_norm, origen_utm = normalizar_datos_terreno(
        cuadrante_maximo, terreno_real
    )

    print(f"Punto Cero Georreferenciado (UTM): {origen_utm}")

    # 4. Procesamos y agregamos el cuadrante de referencia al assembly
    # Nota: Pasamos la data normalizada. El offset devuelto localmente será (0, 0)
    cuadrante_shapely = build_cuadrante_shapely(
        vertices=cuadrante_norm,
        assembly=mi_modelo,
        nombre="Límite del Cuadrante",
        color_hex="#CDCDCD",  # Rojo para notar el límite
    )

    # factory_capas.add_terreno(cuadrante_shapely, name="Cuadrante")

    # 5. Agregamos el Terreno Real usando la data ya normalizada
    _, terreno_wokrplane = terreno_assembly(
        vertices_dict=terreno_norm,
        assembly=mi_modelo,
        nombre="Terreno Real (Polígono)",
        color_hex="#2ECC71",  # Verde para el terreno real
    )

    factory_capas.add_terreno(terreno_wokrplane, name="Terreno_Base")

    largo_cuadrante, ancho_cuadrante = obtener_dimensiones_cuadrante(cuadrante_norm)
    print(
        f"📐 Dimensiones del Cuadrante: Largo (X) = {largo_cuadrante:.3f} m | Ancho (Y) = {ancho_cuadrante:.3f} m"
    )
    CONFIG_PROYECTO["ancho_cuadrante"] = ancho_cuadrante
    CONFIG_PROYECTO["largo_cuadrante"] = largo_cuadrante

    # =========================================================================
    # 1. IDENTIFICACIÓN PREVIA DE PABELLONES ACTIVOS
    # =========================================================================
    pabellones = agrupar_ambientes_por_pabellon(ambientes)
    exportar_pabellones_a_csv(pabellones)

    data_pab_medio: list[DataAmbientes] = pabellones.get("medio", [])
    data_primaria: list[DataAmbientes] = pabellones.get("primaria", [])
    data_secundaria: list[DataAmbientes] = pabellones.get("secundaria", [])
    data_inicial: list[DataAmbientes] = pabellones.get("inicial", [])
    data_admin: list[DataAmbientes] = pabellones.get("admin", [])

    pabellones_activos = {}
    if data_primaria:
        pabellones_activos["primaria"] = data_primaria
    if data_secundaria:
        pabellones_activos["secundaria"] = data_secundaria
    if data_inicial:
        pabellones_activos["inicial"] = data_inicial
    if data_admin:
        pabellones_activos["admin"] = data_admin

    num_pabellones = len(pabellones_activos)
    print(
        f"Pabellones activos detectados ({num_pabellones}): {list(pabellones_activos.keys())}"
    )

    # =========================================================================
    # 2. ADAPTACIÓN DINÁMICA DE LA ORIENTACIÓN
    # =========================================================================
    if largo_cuadrante >= ancho_cuadrante:
        eje_principal = "x"
        eje_secundario = "y"
    else:
        eje_principal = "y"
        eje_secundario = "x"

    ancho_pasadiso = CONFIG_PROYECTO["ancho_pasadiso"]
    ancho_aula = CONFIG_PROYECTO["ancho_aula"]

    slots = {}
    space_centro_2 = None

    # =========================================================================
    # 3. DIVISIÓN DINÁMICA SEGÚN NÚMERO DE PABELLONES (CON PASADIZOS)
    # =========================================================================
    if num_pabellones <= 2:
        print(
            "📐 Aplicando división dinámica para 2 pabellones (Aulas + Pasadizos laterales + Centro)."
        )

        # 5 tramos a lo largo del eje principal: [Aula, Pasadizo, Centro, Pasadizo, Aula]
        medidas_2_pabellones = [
            ancho_aula,
            ancho_pasadiso,
            "auto",
            ancho_pasadiso,
            ancho_aula,
        ]

        tramos_3 = div_logic(
            medidas_2_pabellones, cuadrante_shapely, eje_div=eje_principal
        )

        slot_lat_1, pasadizo_lat_1, space_centro_2, pasadizo_lat_2, slot_lat_2 = (
            tramos_3
        )

        slots = {
            "lateral_1": {"polygon": slot_lat_1, "pasadizo": pasadizo_lat_1},
            "lateral_2": {"polygon": slot_lat_2, "pasadizo": pasadizo_lat_2},
            "extremo_1": {"polygon": None, "pasadizo": None},
            "extremo_2": {"polygon": None, "pasadizo": None},
        }
        imprimir_dimensiones_poligono(space_centro_2, "AREA MEDIO")

    else:
        # Llamada a la función refactorizada para > 2 pabellones
        slots, space_centro_2 = _procesar_layout_multiples_pabellones(
            cuadrante_shapely=cuadrante_shapely,
            eje_principal=eje_principal,
            eje_secundario=eje_secundario,
            ancho_aula=ancho_aula,
            ancho_pasadiso=ancho_pasadiso,
            mi_modelo=mi_modelo,
            factory_capas=factory_capas,
        )
        
        imprimir_dimensiones_poligono(space_centro_2, "AREA MEDIO")
        

    # =========================================================================
    # 4. ASIGNACIÓN FINAL DE PABELLONES A SLOTS
    # =========================================================================
    asignacion_final = {}
    nombres_activos = list(pabellones_activos.keys())

    if num_pabellones <= 2:
        # Asignar únicamente a los slots laterales que abarcan todo el largo/alto
        if num_pabellones >= 1:
            asignacion_final[nombres_activos[0]] = {
                "data": pabellones_activos[nombres_activos[0]],
                "slot": slots["lateral_1"],
            }
        if num_pabellones == 2:
            asignacion_final[nombres_activos[1]] = {
                "data": pabellones_activos[nombres_activos[1]],
                "slot": slots["lateral_2"],
            }
    else:
        # Distribución estándar de 4 pabellones
        if "primaria" in pabellones_activos:
            asignacion_final["primaria"] = {
                "data": data_primaria,
                "slot": slots["lateral_1"],
            }
        if "secundaria" in pabellones_activos:
            asignacion_final["secundaria"] = {
                "data": data_secundaria,
                "slot": slots["lateral_2"],
            }
        if "inicial" in pabellones_activos:
            asignacion_final["inicial"] = {
                "data": data_inicial,
                "slot": slots["extremo_2"],
            }
        if "admin" in pabellones_activos:
            asignacion_final["admin"] = {"data": data_admin, "slot": slots["extremo_1"]}

    print("CENTRO AMBIENTES", data_pab_medio)

    # Lógica para determinar la orientación de la puerta hacia el centro
    centro_absoluto = space_centro_2.centroid
    
    # =========================================================================
    # CONSTRUCCIÓN DE PABELLONES BASADA EN ASIGNACIÓN DINÁMICA
    # =========================================================================
    distribuciones_finales = {
        "primaria": [],
        "secundaria": [],
        "inicial": [],
        "admin": [],
    }

    for nombre_pabellon, info in asignacion_final.items():
        logging.info(f"Construyendo pabellón '{nombre_pabellon}'...")

        data_pabellon = info["data"]
        slot_polygon = info["slot"]["polygon"]
        pasadizo_polygon = info["slot"]["pasadizo"]

        if not slot_polygon:
            logging.warning(
                f"Omitiendo construcción del pabellón '{nombre_pabellon}' porque no tiene un slot geométrico válido."
            )
            continue

        pos_puerta = determinar_posicion_puerta(
            slot_polygon, centro_absoluto, nombre_pabellon, eje_secundario
        )

        distribucion = largos_for_piso_and_ambiente(
            data=data_pabellon,
            polygon=slot_polygon,
            name_pabellon=nombre_pabellon.capitalize(),
        )

        distribuciones_finales[nombre_pabellon] = distribucion

        if not distribucion:
            logging.warning(
                f"No se pudo generar la distribución para el pabellón '{nombre_pabellon}'. Omitiendo construcción."
            )
            continue
        
        print("DISTRUBUICION", distribucion[0])
        container_polygon = obtener_polygon_real_del_piso(distribucion[0], slot_polygon)
        max_nivel = len(distribucion)

        lado_escalera = "izquierda" if nombre_pabellon == "primaria" else "derecha"
        posicion_vertical_escalera = "top" if nombre_pabellon == "admin" else "bottom"

        poly_escalera = crear_poligono_escalera(
            principal_polygon=slot_polygon,
            container_polygon=container_polygon,
            lado=lado_escalera,
            posicion_vertical=posicion_vertical_escalera,
        )

        # new_block(
        #     polygon=poly_escalera,
        #     alto_z=0.3,
        #     assembly=mi_modelo,
        #     nombre=f"Escalera test {nombre_pabellon.capitalize()} - Nivel 1",
        #     color_hex="#D8D8D8",
        #     factory_capas=factory_capas,
        # )

        if pasadizo_polygon:
            new_block(
                polygon=pasadizo_polygon,
                alto_z=0.3,
                assembly=mi_modelo,
                nombre=f"Pasadizo {nombre_pabellon.capitalize()} - Nivel 1",
                color_hex="#D8D8D8",
                factory_capas=factory_capas,
            )

        # REvisando medidas
        print("PISOS DISTRIBUICION", distribucion)

        for index, piso_data in enumerate(distribucion):
            nivel_actual = index + 1
            nombres_ambientes_piso = [item["ambiente"] for item in piso_data]
            largos_habitaciones_piso = [item["largo"] for item in piso_data]
            anchos_habitaciones_piso = [item["ancho"] for item in piso_data]
            imprimir_dimensiones_poligono(
                container_polygon, f"PISO MEDIDA {nivel_actual}"
            )

            create_structure(
                ensamblaje=mi_modelo,
                polygon_pabellon=slot_polygon,
                polygon=container_polygon,
                poly_escalera=poly_escalera,
                largos_habitaciones=largos_habitaciones_piso,
                anchos_habitaciones=anchos_habitaciones_piso,
                sufijo_nombre=nombre_pabellon.capitalize(),
                posicion_puerta=pos_puerta,
                nivel=nivel_actual,
                max_nivel=max_nivel,
                names_ambientes=nombres_ambientes_piso,
                factory_capas=factory_capas,
            )

            create_balcony(
                ensamblaje=mi_modelo,
                polygon=container_polygon,
                polygon_pabellon=slot_polygon,
                sufijo_nombre=nombre_pabellon.capitalize(),
                posicion_puerta=pos_puerta,
                nivel=nivel_actual,
                ancho_balcon=1.8,
                factory_capas=factory_capas,
            )

    # =========================================================================
    # CENTRO: Ubicación Progresiva / Fallback por Prioridad
    # =========================================================================

    # 1. Búsqueda de ambientes
    patio_inicial_list = [
        row
        for row in data_pab_medio
        if "PATIOINICIAL" in row.get("Ambientes", "").upper().replace(" ", "")
    ]
    patio_losa_dep_list = [
        row
        for row in data_pab_medio
        if "LOSADEPORTIVA" in row.get("Ambientes", "").upper().replace(" ", "")
    ]
    sum_salon_usos_mult_list = [
        row
        for row in data_pab_medio
        if "SUM" in row.get("Ambientes", "").upper().replace(" ", "")
    ]

    patio_inicial_values = patio_inicial_list[0] if patio_inicial_list else None
    patio_losa_dep_values = patio_losa_dep_list[0] if patio_losa_dep_list else None
    sum_salon_usos_mult_val = (
        sum_salon_usos_mult_list[0] if sum_salon_usos_mult_list else None
    )

    # Polígonos resultantes finales
    patio_inicial = None
    losa_deportiva = None
    sum_ambiente = None

    # Espacio disponible en el contenedor central
    space_patio, centro_3, space_sum = None, None, None

    if space_centro_2:
        # Preparamos dimensiones
        ancho_patio = (
            patio_inicial_values.get("Ancho", 0) if patio_inicial_values else 0
        )
        largo_patio = (
            patio_inicial_values.get("Largo", 0) if patio_inicial_values else 0
        )

        ancho_losa = patio_losa_dep_values["Ancho"] if patio_losa_dep_values else "auto"
        largo_losa = (
            patio_losa_dep_values.get("Largo", 0) if patio_losa_dep_values else 0
        )

        ancho_sum = (
            sum_salon_usos_mult_val["Ancho"] if sum_salon_usos_mult_val else "auto"
        )
        largo_sum = (
            sum_salon_usos_mult_val.get("Largo", 0) if sum_salon_usos_mult_val else 0
        )

        # INTENTO 1: División conjunta de los 3 tramos
        medidas_centro = [
            ancho_patio if patio_inicial_values else "auto",
            ancho_losa,
            ancho_sum,
        ]
        tramos_centro = div_logic_with_spacing(
            medidas_centro, space_centro_2, eje_div=eje_secundario
        )

        if len(tramos_centro) == 3:
            space_patio, centro_3, space_sum = tramos_centro
        else:
            logging.warning(
                "⚠️ No caben todos los ambientes del centro simultáneamente. "
                "Iniciando ubicación incremental por prioridad..."
            )
            # INTENTO 2: Ubicación incremental uno a uno
            # Probar cada ambiente individualmente en el espacio restante de acuerdo a la lista
            espacio_disponible_actual = space_centro_2

            for amb in data_pab_medio:
                nombre_amb = amb.get("Ambientes", "").upper().replace(" ", "")

                if (
                    "PATIOINICIAL" in nombre_amb
                    and patio_inicial_values
                    and not space_patio
                ):
                    # Validar límites
                    bounds = espacio_disponible_actual.bounds
                    w_disp, h_disp = bounds[2] - bounds[0], bounds[3] - bounds[1]

                    if (ancho_patio <= w_disp and largo_patio <= h_disp) or (
                        largo_patio <= w_disp and ancho_patio <= h_disp
                    ):
                        tramos = div_logic(
                            [ancho_patio, "auto"],
                            espacio_disponible_actual,
                            eje_div=eje_secundario,
                        )
                        if len(tramos) >= 1:
                            space_patio = tramos[0]
                            espacio_disponible_actual = (
                                tramos[-1]
                                if len(tramos) > 1
                                else espacio_disponible_actual
                            )

                elif (
                    "LOSADEPORTIVA" in nombre_amb
                    and patio_losa_dep_values
                    and not centro_3
                ):
                    if isinstance(ancho_losa, (int, float)):
                        tramos = div_logic(
                            [ancho_losa, "auto"],
                            espacio_disponible_actual,
                            eje_div=eje_secundario,
                        )
                        if len(tramos) >= 1:
                            centro_3 = tramos[0]
                            espacio_disponible_actual = (
                                tramos[-1]
                                if len(tramos) > 1
                                else espacio_disponible_actual
                            )
                    else:
                        centro_3 = espacio_disponible_actual

                elif "SUM" in nombre_amb and sum_salon_usos_mult_val and not space_sum:
                    if isinstance(ancho_sum, (int, float)):
                        tramos = div_logic(
                            [ancho_sum, "auto"],
                            espacio_disponible_actual,
                            eje_div=eje_secundario,
                        )
                        if len(tramos) >= 1:
                            space_sum = tramos[0]
                            espacio_disponible_actual = (
                                tramos[-1]
                                if len(tramos) > 1
                                else espacio_disponible_actual
                            )
                    else:
                        space_sum = espacio_disponible_actual

        # 4. Creación de geometrías finales si obtuvieron slot
        if patio_inicial_values and space_patio:

            tramos_patio = div_logic(
                ["auto", largo_patio, "auto"], space_patio, eje_div=eje_principal
            )
            print("TRAMOS PATIO", tramos_patio)
            if len(tramos_patio) == 3:
                _, patio_inicial, _ = tramos_patio
            else:
                patio_inicial = space_patio  # Fallback si no cabe centrado

        if patio_losa_dep_values and centro_3:
            tramos_losa = div_logic(
                ["auto", largo_losa, "auto"], centro_3, eje_div=eje_principal
            )
            if len(tramos_losa) == 3:
                _, losa_deportiva, _ = tramos_losa
            else:
                losa_deportiva = centro_3  # Fallback

        if sum_salon_usos_mult_val and space_sum:
            sum_ambiente = (
                obtener_sub_polygon_centrado(
                    space_sum,
                    sum_salon_usos_mult_val["Largo"],
                    sum_salon_usos_mult_val["Ancho"],
                )
                or space_sum
            )

        if sum_salon_usos_mult_val:
            print("LARGO SUM", sum_salon_usos_mult_val.get("Largo"))
            print("ANCHO SUM", sum_salon_usos_mult_val.get("Ancho"))

    # =========================================================================
    # RENDERIZADO DE BLOQUES DEL CENTRO
    # =========================================================================
    if patio_inicial:
        imprimir_dimensiones_poligono(patio_inicial, "Patio Inicial")
        new_block(
            polygon=patio_inicial,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Patio Inicial - Nivel 1",
            color_hex="#D8D8D8",
            factory_capas=factory_capas,
        )

    if losa_deportiva:
        new_block(
            polygon=losa_deportiva,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Losa Deportiva",
            color_hex="#D8D8D8",
            factory_capas=factory_capas,
        )

    # if sum_ambiente:
    #     sum_polygons = ajustar_dividir_sum(space_sum, sum_ambiente)
    #     print(sum_polygons)
    #     for i, poly in enumerate(sum_polygons):
    #         sufijo = f"SUM_{i+1}" if len(sum_polygons) > 1 else "SUM"

    #         create_structure(
    #             ensamblaje=mi_modelo,
    #             polygon_pabellon=space_sum,
    #             polygon=poly,
    #             largos_habitaciones=[sum_salon_usos_mult_val["Largo"]],
    #             anchos_habitaciones=[sum_salon_usos_mult_val["Ancho"]],
    #             sufijo_nombre=sufijo,
    #             posicion_puerta="bottom",
    #             nivel=1,
    #             max_nivel=1,
    #             names_ambientes=["Sala de Usos Múltiples"],
    #             factory_capas=factory_capas,
    #         )
    #     # create_structure(
    #     #     ensamblaje=mi_modelo,
    #     #     polygon_pabellon=space_sum,  # Parámetro contenedor corregido
    #     #     polygon=sum_ambiente,
    #     #     largos_habitaciones=[sum_salon_usos_mult_val["Largo"]],
    #     #     anchos_habitaciones=[sum_salon_usos_mult_val["Ancho"]],
    #     #     sufijo_nombre="SUM",
    #     #     posicion_puerta="bottom",
    #     #     nivel=1,
    #     #     max_nivel=1,
    #     #     names_ambientes=["Sala de Usos Múltiples"],
    #     #     factory_capas=factory_capas,
    #     # )

    local_glb_filename = f"plane_{id_project}.glb"
    mi_modelo.save(local_glb_filename)

    try:
        bucket_destino = "plaindes"

        file_bytes = obtener_archivo_en_binario(local_glb_filename)
        archivo_binario_stream = io.BytesIO(file_bytes)

        url_resultado = subir_archivo_a_s3(
            archivo_binario=archivo_binario_stream,
            nombre_archivo=local_glb_filename,
            bucket_name=bucket_destino,
        )

        if url_resultado:
            print(
                f"Archivo GLB '{local_glb_filename}' subido con éxito a S3: {url_resultado}"
            )
            os.remove(local_glb_filename)
            print(f"Archivo local '{local_glb_filename}' borrado.")
    except Exception as e:
        print(f"❌ Error durante la subida o borrado del archivo GLB: {e}")

    # reunir metadatos
    RESUMEN_AREAS = []

    RESUMEN_AREAS.append(
        {
            "inicial": limpiar_distribucion_para_resumen(
                distribuciones_finales["inicial"]
            )
        }
    )
    RESUMEN_AREAS.append(
        {
            "primaria": limpiar_distribucion_para_resumen(
                distribuciones_finales["primaria"]
            )
        }
    )
    RESUMEN_AREAS.append(
        {
            "secundaria": limpiar_distribucion_para_resumen(
                distribuciones_finales["secundaria"]
            )
        }
    )
    RESUMEN_AREAS.append(
        {"admin": limpiar_distribucion_para_resumen(distribuciones_finales["admin"])}
    )

    return mi_modelo, factory_capas, RESUMEN_AREAS
