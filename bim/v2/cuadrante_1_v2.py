import cadquery as cq
import os
import io
import logging

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
from dev.utils.calculate_medidas import largos_for_piso_and_ambiente, limpiar_distribucion_para_resumen, obtener_polygon_real_del_piso
from dev.utils.largo_ancho_cuadrante import obtener_dimensiones_cuadrante
from bim.upload_aws_file import subir_archivo_a_s3, obtener_archivo_en_binario
from dev.utils.tools import div_logic, div_logic_with_spacing, obtener_sub_polygon_centrado

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
        cuadrante_maximo, 
        terreno_real
    )

    print(f"Punto Cero Georreferenciado (UTM): {origen_utm}")

    # 4. Procesamos y agregamos el cuadrante de referencia al assembly
    # Nota: Pasamos la data normalizada. El offset devuelto localmente será (0, 0)
    cuadrante_shapely = build_cuadrante_shapely(
        vertices=cuadrante_norm, 
        assembly=mi_modelo, 
        nombre="Límite del Cuadrante",
        color_hex="#CDCDCD" # Rojo para notar el límite
    )

    # 5. Agregamos el Terreno Real usando la data ya normalizada
    terreno_assembly(
        vertices_dict=terreno_norm,
        assembly=mi_modelo,
        nombre="Terreno Real (Polígono)",
        color_hex="#2ECC71" # Verde para el terreno real
    )


    largo_cuadrante, ancho_cuadrante = obtener_dimensiones_cuadrante(cuadrante_norm)
    print(f"📐 Dimensiones del Cuadrante: Largo (X) = {largo_cuadrante:.3f} m | Ancho (Y) = {ancho_cuadrante:.3f} m")
    CONFIG_PROYECTO["ancho_cuadrante"] = ancho_cuadrante
    CONFIG_PROYECTO["largo_cuadrante"] = largo_cuadrante

    # offset_x, offset_y = offset_local

    ancho_pasadiso=CONFIG_PROYECTO["ancho_pasadiso"]
    ancho_aula=CONFIG_PROYECTO["ancho_aula"]

    medidas = [ancho_aula, ancho_pasadiso, "auto", ancho_pasadiso, ancho_aula]

    # # Llamada a la función
    tramos_poligonos = div_logic(medidas, cuadrante_shapely, eje_div="x")
    primaria, pasadizo_primaria, space_centro_1, pasadizo_secundaria, secundaria =tramos_poligonos

    tramos_poligonos_2 = div_logic(medidas, space_centro_1, eje_div="x")
    admin, pasadizo_admin, space_centro_2, pasadizo_inicial, inicial =tramos_poligonos_2

    # Agrupas todo en una sola llamada
    pabellones = agrupar_ambientes_por_pabellon(ambientes)

    # Extraes las variables que necesitas con nombres limpios y consistentes
    data_pab_medio: list[DataAmbientes] = pabellones["medio"]
    data_primaria: list[DataAmbientes] = pabellones["primaria"]
    data_secundaria: list[DataAmbientes] = pabellones["secundaria"]
    data_inicial: list[DataAmbientes] = pabellones["inicial"]
    data_admin: list[DataAmbientes] = pabellones["admin"]

    # Lógica para determinar la orientación de la puerta hacia el centro
    centro_absoluto = space_centro_2.centroid

    def determinar_posicion_puerta(pabellon_polygon, centro_layout, nombre_pabellon):
        """
        Determina si la puerta debe estar en el lado 'top' o 'bottom' para que mire hacia el patio central.
        La lógica asume que los pabellones son más largos que anchos (verticales) y que la función 
        create_structure los rotará 90 grados para trabajar. En esa rotación, el lado derecho (+X)
        se convierte en el lado superior (+Y, 'top'), y el izquierdo (-X) en el inferior (-Y, 'bottom').
        """
        centro_pabellon = pabellon_polygon.centroid
        
        # Si el pabellón está a la izquierda del centro, su puerta debe estar en su lado derecho.
        # Lado derecho (+X) se convierte en 'top'.
        if centro_pabellon.x < centro_layout.x:
            return "top"
        # Si el pabellón está a la derecha del centro, su puerta debe estar en su lado izquierdo.
        # Lado izquierdo (-X) se convierte en 'bottom'.
        else:
            return "bottom"
        
    pos_puerta_primaria = determinar_posicion_puerta(primaria, centro_absoluto, "primaria")
    pos_puerta_secundaria = determinar_posicion_puerta(secundaria, centro_absoluto, "secundaria")
    pos_puerta_inicial = determinar_posicion_puerta(inicial, centro_absoluto, "inicial")
    pos_puerta_admin = determinar_posicion_puerta(admin, centro_absoluto, "admin")

    # PRIMARIA
    distribucion_primaria = []
    if data_primaria:
        distribucion_primaria = largos_for_piso_and_ambiente(
            data=data_primaria,
            polygon=primaria,
            name_pabellon="Primaria"
        )
    
    if distribucion_primaria:
        container_primaria = obtener_polygon_real_del_piso(distribucion_primaria[0], primaria)
        max_nivel_primaria = len(distribucion_primaria)

        for index, piso_data in enumerate(distribucion_primaria):
            nivel_actual = index + 1
            nombres_ambientes_piso = [item["ambiente"] for item in piso_data]
            largos_habitaciones_piso = [item["largo"] for item in piso_data]
            
            create_structure(
                ensamblaje=mi_modelo,
                polygon=container_primaria,                       # El Polygon de Shapely del tramo
                largos_habitaciones=largos_habitaciones_piso,
                sufijo_nombre="Primaria",
                posicion_puerta=pos_puerta_primaria,                  # Orientación de la puerta (top/bottom)
                nivel=nivel_actual,
                max_nivel=max_nivel_primaria,
                names_ambientes=nombres_ambientes_piso,
                factory_capas=factory_capas
            )

            create_balcony(
                ensamblaje=mi_modelo,
                polygon=container_primaria,
                sufijo_nombre="Primaria",
                posicion_puerta=pos_puerta_primaria,
                nivel=nivel_actual,
                ancho_balcon=1.8,
                factory_capas=factory_capas
            )

        new_block(
            polygon=pasadizo_primaria,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Pasadizo Primaria - Nivel 1",
            color_hex="#D8D8D8",
            factory_capas=factory_capas
        )
    else:
        logging.warning("No se encontraron datos de ambientes para Primaria o no se pudo generar la distribución. Omitiendo pabellón de Primaria.")

    # SECUNDARIA
    distribucion_sec = []
    if data_secundaria:
        distribucion_sec = largos_for_piso_and_ambiente(
            data=data_secundaria,
            polygon=secundaria,
            name_pabellon="Secundaria"
        )
    
    if distribucion_sec:
        container_secundaria = obtener_polygon_real_del_piso(distribucion_sec[0], secundaria)
        max_nivel_secundaria = len(distribucion_sec)

        for index, piso_data in enumerate(distribucion_sec):
            nivel_actual = index + 1
            nombres_ambientes_piso = [item["ambiente"] for item in piso_data]
            largos_habitaciones_piso = [item["largo"] for item in piso_data]
            
            create_structure(
                ensamblaje=mi_modelo,
                polygon=container_secundaria,                       # El Polygon de Shapely del tramo
                largos_habitaciones=largos_habitaciones_piso,
                sufijo_nombre="Secundaria",
                posicion_puerta=pos_puerta_secundaria,                  # Orientación de la puerta (top/bottom)
                nivel=nivel_actual,
                max_nivel=max_nivel_secundaria,
                names_ambientes=nombres_ambientes_piso,
                factory_capas=factory_capas
            )

            create_balcony(
                ensamblaje=mi_modelo,
                polygon=container_secundaria,
                sufijo_nombre="Secundaria",
                posicion_puerta=pos_puerta_secundaria,
                nivel=nivel_actual,
                ancho_balcon=1.8,
                factory_capas=factory_capas
            )

        new_block(
            polygon=pasadizo_secundaria,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Pasadizo Secundaria Nivel 1",
            color_hex="#D8D8D8",
            factory_capas=factory_capas
        )
    else:
        logging.warning("No se encontraron datos de ambientes para Secundaria o no se pudo generar la distribución. Omitiendo pabellón de Secundaria.")

    # INICIAL
    distribucion_inicial = []
    if data_inicial:
        distribucion_inicial = largos_for_piso_and_ambiente(
            data=data_inicial,
            polygon=inicial,
            name_pabellon="Inicial"
        )
    
    if distribucion_inicial:
        container_inicial = obtener_polygon_real_del_piso(distribucion_inicial[0], inicial)
        max_nivel_inicial = len(distribucion_inicial)

        for index, piso_data in enumerate(distribucion_inicial):
            nivel_actual = index + 1
            nombres_ambientes_piso = [item["ambiente"] for item in piso_data]
            largos_habitaciones_piso = [item["largo"] for item in piso_data]
            
            create_structure(
                ensamblaje=mi_modelo,
                polygon=container_inicial,                       # El Polygon de Shapely del tramo
                largos_habitaciones=largos_habitaciones_piso,
                sufijo_nombre="Inicial",
                posicion_puerta=pos_puerta_inicial,             # Orientación de la puerta (top/bottom)
                nivel=nivel_actual,
                max_nivel=max_nivel_inicial,
                names_ambientes=nombres_ambientes_piso,
                factory_capas=factory_capas
            )

            create_balcony(
                ensamblaje=mi_modelo,
                polygon=container_inicial,
                sufijo_nombre="Inicial",
                posicion_puerta=pos_puerta_inicial,
                nivel=nivel_actual,
                ancho_balcon=1.8,
                factory_capas=factory_capas
            )
    else:
        logging.warning("No se encontraron datos de ambientes para Inicial o no se pudo generar la distribución. Omitiendo pabellón de Inicial.")
        
        
    # ADMIN
    distribucion_admin = []
    if data_admin:
        distribucion_admin = largos_for_piso_and_ambiente(
            data=data_admin,
            polygon=admin,
            name_pabellon="Admin"
        )
    if distribucion_admin:
        container_admin = obtener_polygon_real_del_piso(distribucion_admin[0], admin)
        max_nivel_admin = len(distribucion_admin)

        for index, piso_data in enumerate(distribucion_admin):
            nivel_actual = index + 1
            nombres_ambientes_piso = [item["ambiente"] for item in piso_data]
            largos_habitaciones_piso = [item["largo"] for item in piso_data]
            
            create_structure(
                ensamblaje=mi_modelo,
                polygon=container_admin,                       # El Polygon de Shapely del tramo
                largos_habitaciones=largos_habitaciones_piso,
                sufijo_nombre="Admin",
                posicion_puerta=pos_puerta_admin,             # Orientación de la puerta (top/bottom)
                nivel=nivel_actual,
                max_nivel=max_nivel_admin,
                names_ambientes=nombres_ambientes_piso,
                factory_capas=factory_capas
            )

            create_balcony(
                ensamblaje=mi_modelo,
                polygon=container_admin,
                sufijo_nombre="Admin",
                posicion_puerta=pos_puerta_admin,
                nivel=nivel_actual,
                ancho_balcon=1.8,
                factory_capas=factory_capas
            )
    else:
        logging.warning("No se encontraron datos de ambientes para Admin o no se pudo generar la distribución. Omitiendo pabellón de Admin.")
            
    if distribucion_inicial:
        new_block(
            polygon=pasadizo_inicial,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Pasadizo Inicial Nivel 1",
            color_hex="#D8D8D8",         # Azul
            factory_capas=factory_capas
        )

    if distribucion_admin:
        new_block(
            polygon=pasadizo_admin,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Pasadizo Admin Nivel 1",
            color_hex="#D8D8D8",         # Azul
            factory_capas=factory_capas
        )

    # CENTRO

    # Patio inicial y losa Deportiva y SUM
    # 1. Búsqueda de ambientes
    patio_inicial_list = [row for row in data_pab_medio if "Patio Inicial" in row["Ambientes"]]
    patio_losa_dep_list = [row for row in data_pab_medio if "Losa Deportiva" in row["Ambientes"]]
    sum_salon_usos_mult_list = [row for row in data_pab_medio if "SUM" in row["Ambientes"]]

    # Variables de salida inicializadas por defecto
    patio_inicial = None
    losa_deportiva = None
    patio_inicial_values = patio_inicial_list[0] if patio_inicial_list else None
    patio_losa_dep_values = patio_losa_dep_list[0] if patio_losa_dep_list else None
    sum_salon_usos_mult_val = sum_salon_usos_mult_list[0] if sum_salon_usos_mult_list else None

    # 2. Configuración condicional de dimensiones
    ancho_patio = 0
    largo_patio = 0
    if patio_inicial_values:
        name_ambiente, m2, cantidad, _, ancho_patio, largo_patio, *rest = patio_inicial_values.values()

    ancho_losa = patio_losa_dep_values["Ancho"] if patio_losa_dep_values else "auto"
    largo_losa = patio_losa_dep_values["Largo"] if patio_losa_dep_values else "auto"
    ancho_sum = sum_salon_usos_mult_val["Ancho"] if sum_salon_usos_mult_val else "auto"

    # 3. Lógica de espaciado central
    medidas_centro = [
        ancho_patio if patio_inicial_values else "auto", 
        ancho_losa, 
        ancho_sum
    ]
    tramos_centro = div_logic_with_spacing(medidas_centro, space_centro_2, eje_div="y")
    space_patio, centro_3, space_sum = tramos_centro if len(tramos_centro) == 3 else (None, None, None)

    # 4. Creación condicional de geometrías (Solo si existen)
    if patio_inicial_values and space_patio:
        tramos_patio = div_logic(["auto", largo_patio, "auto"], space_patio, eje_div="y")
        if len(tramos_patio) == 3:
            _, patio_inicial, _ = tramos_patio

    if patio_losa_dep_values and centro_3:
        tramos_losa = div_logic(["auto", largo_losa, "auto"], centro_3, eje_div="y")
        if len(tramos_losa) == 3:
            _, losa_deportiva, _ = tramos_losa
    # Salon de usos multiples
    sum_ambiente = obtener_sub_polygon_centrado(space_sum, sum_salon_usos_mult_val["Largo"], sum_salon_usos_mult_val["Ancho"]) if sum_salon_usos_mult_val and space_sum else None

    if patio_inicial:
        new_block(
            polygon=patio_inicial,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Patio Inicial",
            color_hex="#D8D8D8",
            factory_capas=factory_capas
        )

    if losa_deportiva:
        new_block(
            polygon=losa_deportiva,
            alto_z=0.3,
            assembly=mi_modelo,
            nombre="Losa Deportiva",
            color_hex="#D8D8D8",
            factory_capas=factory_capas
        )

    if sum_ambiente:
        create_structure(
                ensamblaje=mi_modelo,
                polygon=sum_ambiente,                       # El Polygon de Shapely del tramo
                largos_habitaciones=[sum_salon_usos_mult_val["Largo"]],
                sufijo_nombre="SUM",
                posicion_puerta="bottom",             # Orientación de la puerta (top/bottom)
                nivel=1,
                max_nivel=1,
                names_ambientes=["SUM"],
                factory_capas=factory_capas
            )

    local_glb_filename = f"plane_{id_project}.glb"
    mi_modelo.save(local_glb_filename)

    try:
        bucket_destino = "plaindes"

        file_bytes = obtener_archivo_en_binario(local_glb_filename)
        archivo_binario_stream = io.BytesIO(file_bytes)

        url_resultado = subir_archivo_a_s3(
            archivo_binario=archivo_binario_stream,
            nombre_archivo=local_glb_filename,
            bucket_name=bucket_destino
        )

        if url_resultado:
            print(f"Archivo GLB '{local_glb_filename}' subido con éxito a S3: {url_resultado}")
            os.remove(local_glb_filename)
            print(f"Archivo local '{local_glb_filename}' borrado.")
    except Exception as e:
        print(f"❌ Error durante la subida o borrado del archivo GLB: {e}")
    

    # reunir metadatos
    RESUMEN_AREAS = []
    
    RESUMEN_AREAS.append({"inicial": limpiar_distribucion_para_resumen(distribucion_inicial)})
    RESUMEN_AREAS.append({"primaria" : limpiar_distribucion_para_resumen(distribucion_primaria)})
    RESUMEN_AREAS.append({"secundaria" : limpiar_distribucion_para_resumen(distribucion_sec)})
    RESUMEN_AREAS.append({"admin" : limpiar_distribucion_para_resumen(distribucion_admin)})
    
    return mi_modelo, factory_capas, RESUMEN_AREAS