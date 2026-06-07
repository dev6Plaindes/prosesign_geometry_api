from src.motor.generate_distribution import auto_distribution_ambientes_y
from src.motor.motor_2d_3d import Motor2D
import numpy as np
import pandas as pd
from shapely import Point, affinity

def process_ambientes_motor_to_dict(df_excel, ancho_cuadrante, largo_cuadrante, angle, zona="zona_1"):
    
    # Valores iniciales
    ancho_c = ancho_cuadrante
    largo_c = largo_cuadrante

    # 1. El movimiento de ángulo ocurre si el largo es mayor al ancho
    # Queremos que el valor más grande termine en 'max_ancho'
    angulo_movido = 90 if largo_c > ancho_c else 0

    # 2. Asignación: max_ancho siempre será el valor mayor
    if angulo_movido == 90:
        max_ancho = largo_c
        max_largo = ancho_c
    else:
        max_ancho = ancho_c
        max_largo = largo_c

    # 3. Guardar el ángulo final (Normalizado a 180°)
    angulo_final = (angle + angulo_movido) % 180
    
    df_pab_sec =  df_excel[df_excel["Pabellon"]=="Derecha"]
    df_pab_prim = df_excel[df_excel["Pabellon"]=="Izquierda"]
    df_pab_inicial = df_excel[df_excel["Pabellon"]=="Inferior"]
    df_pab_sup =  df_excel[df_excel["Pabellon"]=="Superior"]
    df_pab_medio =  df_excel[df_excel["Pabellon"]=="Medio"]

    aula_in_prim = df_pab_prim[df_pab_prim["Ambientes"]=="Aula de Innovacion Prim"]
    aula_in_ancho_prim = aula_in_prim["Ancho"].iloc[0]

    # SECUNDARIA
    aula_in_sec = df_pab_sec[df_pab_sec["Ambientes"]=="Aula de Innovacion Sec"]
    aula_in_ancho_sec = aula_in_sec["Ancho"].iloc[0]

    # ADMIN
    direccion_adm = df_pab_sup[df_pab_sup["Ambientes"]=="Direccion Adm."]
    direccion_adm_ancho = direccion_adm["Ancho"].iloc[0]
    direccion_adm_largo = direccion_adm["Largo"].iloc[0]

    area_espera = df_pab_sup[df_pab_sup["Ambientes"]=="Área de espera"]
    area_espera_ancho = area_espera["Ancho"].iloc[0]
    area_espera_largo = area_espera["Largo"].iloc[0]

    sala_reuniones = df_pab_sup[df_pab_sup["Ambientes"]=="Sala de Reuniones"]
    sala_reuniones_ancho = sala_reuniones["Ancho"].iloc[0]
    sala_reuniones_largo = sala_reuniones["Largo"].iloc[0]

    area_ingreso = df_pab_sup[df_pab_sup["Ambientes"]=="Area de ingreso"]
    area_ingreso_ancho = area_ingreso["Ancho"].iloc[0]
    area_ingreso_largo = area_ingreso["Largo"].iloc[0]

    sala_profesores = df_pab_sup[df_pab_sup["Ambientes"]=="Sala de Profesores"]
    sala_profesores_ancho = sala_profesores["Ancho"].iloc[0]
    sala_profesores_largo = sala_profesores["Largo"].iloc[0]

    sshh_adm = df_pab_sup[df_pab_sup["Ambientes"]=="SSHH Adm. - Hombres"]
    sshh_adm_largo = sshh_adm["Largo"].iloc[0]

    # Inicial - Definición de variables por ambiente
    aulas_ciclo1 = df_pab_inicial[df_pab_inicial["Ambientes"]=="Aulas Ciclo I"]
    ciclo1_ancho = aulas_ciclo1["Ancho"].iloc[0]
    ciclo1_largo = aulas_ciclo1["Largo"].iloc[0]
    ciclo1_cantidad = int(aulas_ciclo1["Cantidad"].iloc[0])

    aulas_ciclo2 = df_pab_inicial[df_pab_inicial["Ambientes"]=="Aulas Ciclo II"]
    ciclo2_ancho = aulas_ciclo2["Ancho"].iloc[0]
    ciclo2_largo = aulas_ciclo2["Largo"].iloc[0]
    ciclo2_cantidad = int(aulas_ciclo2["Cantidad"].iloc[0])

    psicomotricidad = df_pab_inicial[df_pab_inicial["Ambientes"]=="Aulas Psicomotricidad"]
    psico_ancho = psicomotricidad["Ancho"].iloc[0]
    psico_largo = psicomotricidad["Largo"].iloc[0]

    topico = df_pab_inicial[df_pab_inicial["Ambientes"]=="Topico"]
    topico_ancho = topico["Ancho"].iloc[0]
    topico_largo = topico["Largo"].iloc[0]

    lactario = df_pab_inicial[df_pab_inicial["Ambientes"]=="Lactario"]
    lactario_ancho = lactario["Ancho"].iloc[0]
    lactario_largo = lactario["Largo"].iloc[0]

    sshh_inicial = df_pab_inicial[df_pab_inicial["Ambientes"]=="SSHH Inicial - Hombres"]
    sshh_ancho = sshh_inicial["Ancho"].iloc[0]
    sshh_largo = sshh_inicial["Largo"].iloc[0]

    cocina_inicial = df_pab_inicial[df_pab_inicial["Ambientes"]=="Cocina Inicial"]
    cocina_ancho = cocina_inicial["Ancho"].iloc[0]
    cocina_largo = cocina_inicial["Largo"].iloc[0]
    
    # --- EXTRACCIÓN DE DATOS PABELLÓN MEDIO ---

    # 1. Losa Deportiva
    losa_data = df_pab_medio[df_pab_medio["Ambientes"]=="Losa Deportiva"]
    ancho_losa = losa_data["Ancho"].iloc[0]
    largo_losa = losa_data["Largo"].iloc[0]

    # 2. Taller EPT
    taller_ept = df_pab_medio[df_pab_medio["Ambientes"]=="Taller EPT"]
    ancho_ept = taller_ept["Ancho"].iloc[0]
    largo_ept = taller_ept["Largo"].iloc[0]

    # 3. SUM (Salón de Usos Múltiples)
    sum_data = df_pab_medio[df_pab_medio["Ambientes"]=="SUM"]
    ancho_sum = sum_data["Ancho"].iloc[0]
    largo_sum = sum_data["Largo"].iloc[0]

    # 4. Cocina
    cocina_data = df_pab_medio[df_pab_medio["Ambientes"]=="Cocina Prim - Sec"]
    ancho_cocina = cocina_data["Ancho"].iloc[0]
    largo_cocina = cocina_data["Largo"].iloc[0]

    # 5. Patio de Inicial
    patio_ini = df_pab_medio[df_pab_medio["Ambientes"]=="Patio de Inicial"]
    ancho_patio = patio_ini["Ancho"].iloc[0]
    largo_patio = patio_ini["Largo"].iloc[0]

    ancho_c = ancho_cuadrante
    largo_c = largo_cuadrante

    max_largo = largo_c if ancho_c > largo_c else ancho_c
    max_ancho = ancho_c if ancho_c > largo_c else largo_c
    
    # ZONA TIPO TECHO
    tipo_techo = zona
    ancho_pasadizo = 1.8
    render2d = Motor2D(ancho = max_ancho, largo = max_largo)
    pab_primaria, pas_prim, a, pas_sec, pab_secundaria = render2d.areas_m(aula_in_ancho_prim, ancho_pasadizo, "auto", ancho_pasadizo, aula_in_ancho_sec, direccion="horizontal") # areas

    # primaria
    esc_prim, primaria, esc_prim_2 = pab_primaria.areas_m(2.4, "auto", 2.4, direccion="vertical")

    _, esp_esc_prim = esc_prim.areas_m("auto",4 , direccion="horizontal")
    
    df_excel = df_excel.to_dict(orient="records")
    pabellon_primaria = auto_distribution_ambientes_y(df_excel, ancho_c, pabellon="Izquierda")
    
    pisos_primaria = max(
        (x["Piso"] for x in pabellon_primaria),
        default=0
    )

    esp_esc_prim.escalera(direccion="este", pisos=pisos_primaria)

    for row in pabellon_primaria:
        aula_in_prim = primaria.aula(
            row["Ancho_Individual"],
            row["Largo_Individual"],
            description=row["Ambiente"],
            piso=row["Piso"]
        )
        
    for i in range(1,pisos_primaria + 1):
        sshh_in_prim = primaria.bano(7.5, 2, description=f"SSHH Primaria Hombres {i}", piso=i)
        sshh_in_prim_2 = primaria.bano(7.5, 2, description=f"SSHH Primaria Mujeres {i}", piso=i)

    primaria.create_columns("y", pabellon_primaria)
    primaria.create_muros_frontales("y")
    primaria.create_muros_laterales("y")
    primaria.create_vigas_frontales("y", orientacion_balcon="R")
    primaria.create_vigas_laterales("y")
    primaria.create_techos(orientacion="W", tipo_techo= tipo_techo)

    pabellon_prim_largo = (
        max(
            (x["Largo_Total_Piso"] for x in pabellon_primaria),
            default=0
        )
        + esc_prim.largo
        + (sshh_in_prim.largo * 2)
    )
    
    ancho_pas_prim = pab_primaria.largo
    info_pisos_prim = primaria.obtener_resumen_pisos()

    pas_prim.pasadizos_mult(ancho=2 , largo=ancho_pas_prim, largo_balcon=pabellon_prim_largo, pisos=primaria.pisos, lado="O", info_pisos= info_pisos_prim)

    # secundaria
    esc_sec, secundaria, esc_sec_2 = pab_secundaria.areas_m(2.4, "auto", 2.4, direccion="vertical")

    esp_esc_secundaria,_  = esc_sec.areas_m(4 ,"auto", direccion="horizontal")

    pabellon_sec = auto_distribution_ambientes_y(df_excel, ancho_c, pabellon="Derecha")
    pisos_secundaria = max(
        (x["Piso"] for x in pabellon_sec),
        default=0
    )
    
    esp_esc_secundaria.escalera(direccion="oeste", pisos=pisos_secundaria)

    for row in pabellon_sec:
        aula_in_prim = secundaria.aula(
            row["Ancho_Individual"],
            row["Largo_Individual"],
            description=row["Ambiente"],
            piso=row["Piso"],
            lado="left"
        )

    for i in range(1,pisos_secundaria + 1):
        sshh_in_sec = secundaria.bano(7.5, 2, description=f"SSHH secundaria Hombres {i}", piso=i, lado="left")
        sshh_in_sec_2 = secundaria.bano(7.5, 2, description=f"SSHH secundaria Mujeres {i}", piso=i, lado="left")

    secundaria.create_columns("y", pabellon_sec)
    secundaria.create_muros_frontales("y", pos_balcon="L")
    secundaria.create_muros_laterales("y")
    secundaria.create_vigas_frontales("y", orientacion_balcon="L")
    secundaria.create_vigas_laterales("y", pos_balcon="L")
    secundaria.create_techos(orientacion="E", tipo_techo= tipo_techo)

    ancho_pas_sec = pab_secundaria.largo
    info_pisos_sec = secundaria.obtener_resumen_pisos()
    pabellon_sec_largo = (
        max(
            (x["Largo_Total_Piso"] for x in pabellon_sec),
            default=0
        )
        + esc_sec.largo
        + (sshh_in_sec.largo * 2)
    )

    pas_sec.pasadizos_mult(ancho=ancho_pasadizo , largo=ancho_pas_sec, largo_balcon=pabellon_sec_largo, pisos=secundaria.pisos, info_pisos= info_pisos_sec)

    inicial, b, admin = a.areas_m(ciclo1_largo, "auto",direccion_adm_largo, direccion="vertical")

    # ADMIN
    direccion_adm_area = admin.aula(direccion_adm_ancho, direccion_adm_largo, description="Dirección Adm.", lado="top")
    area_espera_area = admin.aula(area_espera_ancho, area_espera_largo, description="Área de espera", lado="top")
    sala_reuniones_area = admin.aula(sala_reuniones_ancho, sala_reuniones_largo, description="Sala de Reuniones", lado="top")
    area_ingreso_area = admin.aula(area_ingreso_ancho, area_ingreso_largo, description="Área de ingreso", lado="top")
    sala_profesores_area = admin.aula(sala_profesores_ancho, sala_profesores_largo, description="Sala de Profesores", lado="top")
    sshh_adm_area = admin.aula(3.5, sshh_adm_largo, description="SSHH Adm.", lado="top")
    admin.centrar_aulas()

    admin.create_columns_from_aulas(pos="B", heigth=5)
    admin.create_techos()

    # INICIAL
    aulas_ciclo1_list = [inicial.aula(ciclo1_ancho, ciclo1_largo, description="Aula Ciclo I", lado="bottom") for _ in range(ciclo1_cantidad)]
    aulas_ciclo2_list = [inicial.aula(ciclo2_ancho, ciclo2_largo, description="Aula Ciclo II", lado="bottom") for _ in range(ciclo2_cantidad)]
    psicomotricidad_area = inicial.aula(psico_ancho, psico_largo, description="Aulas Psicomotricidad", lado="bottom")
    topico_area = inicial.aula(topico_ancho, topico_largo, description="Tópico", lado="bottom")
    lactario_area = inicial.aula(lactario_ancho, lactario_largo, description="Lactario", lado="bottom")
    sshh_inicial_area = inicial.bano(sshh_ancho, sshh_largo, description="SSHH Inicial", lado="bottom")
    cocina_inicial_area = inicial.aula(cocina_ancho, cocina_largo, description="Cocina Inicial", lado="bottom")

    inicial.centrar_aulas()

    inicial.create_columns_from_aulas()
    inicial.create_techos()

    pas_inicial, medio, pas_admin = b.areas_m(1.4, "auto",1.4 , direccion="vertical")

    ancho_pas_inicial = inicial.sumar_anchos_aulas_por_piso(1)
    pas_inicial.pasadizo(pas_inicial.ancho, 1.2, piso=1)
    pas_inicial.centrar_pasadizos()

    ancho_pas_admin = admin.sumar_anchos_aulas_por_piso(1)
    pas_admin.pasadizo(admin.ancho, 1.2, piso=1)
    pas_admin.centrar_pasadizos()

    area_losa_inic, medio_m, sum_m = medio.areas_m(ancho_patio, "auto",largo_sum * 1.4, direccion="vertical")

    sum_m.aula(ancho=ancho_sum, largo=largo_sum, description="SUM", lado="top")
    sum_m.aula(ancho=ancho_cocina, largo=largo_cocina, description="Cocina", lado="top")
    sum_m.centrar_aulas()
    sum_m.create_columns_from_aulas(heigth=largo_sum)
    sum_m.create_techos()

    losas, ept =medio_m.areas_m("auto", largo_ept, direccion="horizontal")
    losas.insertar_losas(
        cantidad_losas=3,
        gap=1,
        ancho_losa=ancho_losa,
        largo_losa=largo_losa
    )
    
    losas.centrar_elementos()

    if ept.largo >=ancho_ept:
        ept.aula(ancho=ancho_ept, largo=largo_ept, description="Taller EPT", lado="right")
        ept.centrar_aulas()

    ept.create_columns_from_aulas(heigth=largo_ept)
    ept.create_techos()

    area_losa_inic.losa(ancho=largo_patio, largo=ancho_patio, description="Patio Inicial")
    area_losa_inic.centrar_losas()

    data =  render2d.get_data()

    return data, angulo_final


import numpy as np
from shapely import affinity
import math

def obtener_angulo_orientacion(poligono):
    """Calcula el ángulo del lado más largo del polígono respecto al eje X."""
    coords = list(poligono.exterior.coords)[:-1]
    max_dist = 0
    angulo_detectado = 0
    
    # Buscamos el segmento más largo del rectángulo para determinar su orientación
    for i in range(len(coords)):
        p1 = coords[i]
        p2 = coords[(i + 1) % len(coords)]
        dist = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        
        if dist > max_dist:
            max_dist = dist
            # Calcular ángulo en grados
            angulo_detectado = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
            
    return angulo_detectado

def transformar_df_con_referencia(
    data,
    data_cuadrante_real
):
    """
    MISMA lógica original.
    Solo elimina pandas.
    """

    # ==========================================
    # COPY (equivalente df.copy())
    # ==========================================
    df_result = [row.copy() for row in data]

    # ==========================================
    # REFERENCIAS DE GEOMETRÍA
    # ==========================================
    g_real = data_cuadrante_real[0]["geometria"]

    # Buscar render
    df_render = None

    for row in data:

        if row.get("tipo") == "render":

            df_render = row
            break

    if df_render is None:

        raise ValueError(
            "No se encontró objeto tipo "
            "'render' para alinear."
        )

    g_render_local = df_render["geometria"]

    # ==========================================
    # HALLAR ÁNGULO
    # ==========================================
    ang_real = obtener_angulo_orientacion(
        g_real
    )

    ang_local = obtener_angulo_orientacion(
        g_render_local
    )

    angulo_necesario = (
        ang_real - ang_local
    )

    # ==========================================
    # PUNTOS DE ANCLAJE
    # ==========================================
    dest_x = g_real.centroid.x
    dest_y = g_real.centroid.y

    orig_x = g_render_local.centroid.x
    orig_y = g_render_local.centroid.y

    # ==========================================
    # TRANSFORMACIÓN 2D
    # ==========================================
    nuevas_geoms = []

    for row in df_result:

        geom = row.get("geometria")

        if geom is None:

            nuevas_geoms.append(None)
            continue

        # ==============================
        # ROTACIÓN
        # ==============================
        g_rot = affinity.rotate(
            geom,
            angulo_necesario,
            origin=(orig_x, orig_y)
        )

        # ==============================
        # TRASLACIÓN
        # ==============================
        g_final = affinity.translate(
            g_rot,
            xoff=dest_x - orig_x,
            yoff=dest_y - orig_y
        )

        nuevas_geoms.append(g_final)

    # ==========================================
    # ACTUALIZAR GEOMETRÍAS + X/Y
    # ==========================================
    for row, nueva_geom in zip(
        df_result,
        nuevas_geoms
    ):

        row["geometria"] = nueva_geom

        if nueva_geom:

            bounds = nueva_geom.bounds

            row["x"] = bounds[0]
            row["y"] = bounds[1]

        else:

            row["x"] = None
            row["y"] = None

    # ==========================================
    # GEOMETRÍA 3D
    # ==========================================
    tiene_geo_3d = any(
        "geometria_3d" in row
        for row in df_result
    )

    if tiene_geo_3d:

        nuevas_geoms_3d = []

        for idx, row in enumerate(df_result):

            geo_3d = row.get("geometria_3d")

            if (
                not isinstance(geo_3d, dict)
                or 'x' not in geo_3d
                or 'y' not in geo_3d
                or 'z' not in geo_3d
            ):

                nuevas_geoms_3d.append(
                    geo_3d
                )

                continue

            try:

                nuevos_x = []
                nuevos_y = []

                # ======================
                # TRANSFORMAR VÉRTICES
                # ======================
                for px, py in zip(
                    geo_3d['x'],
                    geo_3d['y']
                ):

                    punto = Point(px, py)

                    # ROTACIÓN
                    punto_rot = affinity.rotate(
                        punto,
                        angulo_necesario,
                        origin=(orig_x, orig_y)
                    )

                    # TRASLACIÓN
                    punto_final = affinity.translate(
                        punto_rot,
                        xoff=dest_x - orig_x,
                        yoff=dest_y - orig_y
                    )

                    nuevos_x.append(
                        punto_final.x
                    )

                    nuevos_y.append(
                        punto_final.y
                    )

                nuevas_geoms_3d.append({
                    'x': nuevos_x,
                    'y': nuevos_y,
                    'z': geo_3d['z']
                })

            except Exception as e:

                print(
                    f"Error geometria_3d "
                    f"fila {idx}: {e}"
                )

                nuevas_geoms_3d.append(
                    geo_3d
                )

        # ======================================
        # ASIGNAR geometria_3d
        # ======================================
        for row, geo3d in zip(
            df_result,
            nuevas_geoms_3d
        ):

            row["geometria_3d"] = geo3d

    return df_result

