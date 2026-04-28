from src.motor.generate_distribution import auto_distribution_ambientes_y
from src.motor.motor_2d_3d import Motor2D
import numpy as np
import pandas as pd
from shapely import affinity

def process_ambientes_motor_to_dict(df_excel, ancho_cuadrante, largo_cuadrante, angle):
    
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

    # PRIMARIA
    aulas_prim = df_pab_prim[df_pab_prim["Ambientes"]=="Aulas Primaria"]
    ancho_prim = aulas_prim["Ancho"].iloc[0]
    largo_prim = aulas_prim["Largo"].iloc[0]
    cantidad_prim = int(aulas_prim["Cantidad"].iloc[0])

    biblioteca_prim = df_pab_prim[df_pab_prim["Ambientes"]=="Biblioteca"]
    biblio_ancho_prim = biblioteca_prim["Ancho"].iloc[0]
    biblio_largo_prim = biblioteca_prim["Largo"].iloc[0]
    biblio_cantidad_prim = int(biblioteca_prim["Cantidad"].iloc[0])

    aula_in_prim = df_pab_prim[df_pab_prim["Ambientes"]=="Aula de Innovacion Prim"]
    aula_in_ancho_prim = aula_in_prim["Ancho"].iloc[0]
    aula_in_largo_prim = aula_in_prim["Largo"].iloc[0]
    aula_in_cantidad_prim = int(aula_in_prim["Cantidad"].iloc[0])

    # Taller creativo Prim
    taller_prim = df_pab_prim[df_pab_prim["Ambientes"]=="Taller creativo Prim"]
    taller_ancho_prim = taller_prim["Ancho"].iloc[0]
    taller_largo_prim = taller_prim["Largo"].iloc[0]
    taller_cantidad_prim = int(taller_prim["Cantidad"].iloc[0])

    # SECUNDARIA
    aulas_sec = df_pab_sec[df_pab_sec["Ambientes"]=="Aulas Secundaria"]
    ancho_sec = aulas_sec["Ancho"].iloc[0]
    largo_sec = aulas_sec["Largo"].iloc[0]
    cantidad_sec = int(aulas_sec["Cantidad"].iloc[0])

    biblioteca_sec = df_pab_sec[df_pab_sec["Ambientes"]=="Laboratorio"]
    biblio_ancho_sec = biblioteca_sec["Ancho"].iloc[0]
    biblio_largo_sec = biblioteca_sec["Largo"].iloc[0]
    biblio_cantidad_sec = int(biblioteca_sec["Cantidad"].iloc[0])

    aula_in_sec = df_pab_sec[df_pab_sec["Ambientes"]=="Aula de Innovacion Sec"]
    aula_in_ancho_sec = aula_in_sec["Ancho"].iloc[0]
    aula_in_largo_sec = aula_in_sec["Largo"].iloc[0]
    aula_in_cantidad_sec = int(aula_in_sec["Cantidad"].iloc[0])

    # Taller creativo Sec
    taller_sec = df_pab_sec[df_pab_sec["Ambientes"]=="Taller creativo Sec"]
    taller_ancho_sec = taller_sec["Ancho"].iloc[0]
    taller_largo_sec = taller_sec["Largo"].iloc[0]
    taller_cantidad_sec = int(taller_sec["Cantidad"].iloc[0])

    # ADMIN
    direccion_adm = df_pab_sup[df_pab_sup["Ambientes"]=="Direccion Adm."]
    direccion_adm_ancho = direccion_adm["Ancho"].iloc[0]
    direccion_adm_largo = direccion_adm["Largo"].iloc[0]
    direccion_adm_cantidad = int(direccion_adm["Cantidad"].iloc[0])

    area_espera = df_pab_sup[df_pab_sup["Ambientes"]=="Área de espera"]
    area_espera_ancho = area_espera["Ancho"].iloc[0]
    area_espera_largo = area_espera["Largo"].iloc[0]
    area_espera_cantidad = int(area_espera["Cantidad"].iloc[0])

    sala_reuniones = df_pab_sup[df_pab_sup["Ambientes"]=="Sala de Reuniones"]
    sala_reuniones_ancho = sala_reuniones["Ancho"].iloc[0]
    sala_reuniones_largo = sala_reuniones["Largo"].iloc[0]
    sala_reuniones_cantidad = int(sala_reuniones["Cantidad"].iloc[0])

    area_ingreso = df_pab_sup[df_pab_sup["Ambientes"]=="Area de ingreso"]
    area_ingreso_ancho = area_ingreso["Ancho"].iloc[0]
    area_ingreso_largo = area_ingreso["Largo"].iloc[0]
    area_ingreso_cantidad = int(area_ingreso["Cantidad"].iloc[0])

    sala_profesores = df_pab_sup[df_pab_sup["Ambientes"]=="Sala de Profesores"]
    sala_profesores_ancho = sala_profesores["Ancho"].iloc[0]
    sala_profesores_largo = sala_profesores["Largo"].iloc[0]
    sala_profesores_cantidad = int(sala_profesores["Cantidad"].iloc[0])

    sshh_adm = df_pab_sup[df_pab_sup["Ambientes"]=="SSHH Adm."]
    sshh_adm_ancho = sshh_adm["Ancho"].iloc[0]
    sshh_adm_largo = sshh_adm["Largo"].iloc[0]
    sshh_adm_cantidad = int(sshh_adm["Cantidad"].iloc[0])

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
    psico_cantidad = int(psicomotricidad["Cantidad"].iloc[0])

    topico = df_pab_inicial[df_pab_inicial["Ambientes"]=="Topico"]
    topico_ancho = topico["Ancho"].iloc[0]
    topico_largo = topico["Largo"].iloc[0]
    topico_cantidad = int(topico["Cantidad"].iloc[0])

    lactario = df_pab_inicial[df_pab_inicial["Ambientes"]=="Lactario"]
    lactario_ancho = lactario["Ancho"].iloc[0]
    lactario_largo = lactario["Largo"].iloc[0]
    lactario_cantidad = int(lactario["Cantidad"].iloc[0])

    sshh_inicial = df_pab_inicial[df_pab_inicial["Ambientes"]=="SSHH Inicial - Hombres"]
    sshh_ancho = sshh_inicial["Ancho"].iloc[0]
    sshh_largo = sshh_inicial["Largo"].iloc[0]
    sshh_cantidad = int(sshh_inicial["Cantidad"].iloc[0])

    cocina_inicial = df_pab_inicial[df_pab_inicial["Ambientes"]=="Cocina Inicial"]
    cocina_ancho = cocina_inicial["Ancho"].iloc[0]
    cocina_largo = cocina_inicial["Largo"].iloc[0]
    cocina_cantidad = int(cocina_inicial["Cantidad"].iloc[0])


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

    render2d = Motor2D(ancho = max_ancho, largo = max_largo)
    pab_primaria, pas_prim, a, pas_sec, pab_secundaria = render2d.areas_m(aula_in_ancho_prim, 1.2, "auto", 1.2, aula_in_ancho_sec, direccion="horizontal") # areas

    # primaria

    esc_prim, primaria, esc_prim_2 = pab_primaria.areas_m(2.4, "auto", 2.4, direccion="vertical")

    _, esp_esc_prim = esc_prim.areas_m("auto",4 , direccion="horizontal")
    
    pabellon_primaria = auto_distribution_ambientes_y(df_excel, ancho_c)
    pisos_primaria = pabellon_primaria["Piso"].max()
    esp_esc_prim.escalera(direccion="este", pisos=pisos_primaria)

    for index, row in pabellon_primaria.iterrows():
        aula_in_prim = primaria.aula(row["Ancho_Individual"], row["Largo_Individual"], description="Aula de Innovacion", piso=row["Piso"])

    for i in range(1,pisos_primaria + 1):
        sshh_in_prim = primaria.bano(7.5, 2, description=f"SSHH Primaria Hombres {i}", piso=i)
        sshh_in_prim_2 = primaria.bano(7.5, 2, description=f"SSHH Primaria Mujeres {i}", piso=i)

    ancho_pas_prim = pab_primaria.largo
    pabellon_prim_largo = pabellon_primaria["Largo_Total_Piso"].max() + esc_prim.largo + (sshh_in_prim.largo * 2)
    
    info_pisos_prim = primaria.obtener_resumen_pisos()

    pas_prim.pasadizos_mult(ancho=2 , largo =ancho_pas_prim, largo_balcon=pabellon_prim_largo, pisos=primaria.pisos, lado="O", info_pisos= info_pisos_prim)

    # secundaria
    esc_sec, secundaria, esc_sec_2 = pab_secundaria.areas_m(2.4, "auto", 2.4, direccion="vertical")

    esp_esc_secundaria,_  = esc_sec.areas_m(4 ,"auto", direccion="horizontal")

    pabellon_sec = auto_distribution_ambientes_y(df_excel, ancho_c, pabellon="Derecha")
    pisos_secundaria = pabellon_sec["Piso"].max()
    esp_esc_secundaria.escalera(direccion="oeste", pisos=pisos_secundaria)

    for index, row in pabellon_sec.iterrows():
        aula_in_prim = secundaria.aula(row["Ancho_Individual"], row["Largo_Individual"], description=row["Ambiente"], piso=row["Piso"], lado="left")

    for i in range(1,pisos_secundaria + 1):
        sshh_in_sec = secundaria.bano(7.5, 2, description=f"SSHH secundaria Hombres {i}", piso=i, lado="left")
        sshh_in_sec_2 = secundaria.bano(7.5, 2, description=f"SSHH secundaria Mujeres {i}", piso=i, lado="left")


    ancho_pas_sec = pab_secundaria.largo
    info_pisos_sec = secundaria.obtener_resumen_pisos()
    pabellon_sec_largo = pabellon_sec["Largo_Total_Piso"].max() + esc_sec.largo + (sshh_in_sec.largo * 2)
    
    pas_sec.pasadizos_mult(ancho=2 , largo=ancho_pas_sec, largo_balcon=pabellon_sec_largo, pisos=secundaria.pisos, info_pisos= info_pisos_sec)

    inicial, b, admin = a.areas_m(ciclo1_largo, "auto",direccion_adm_largo, direccion="vertical")

    # admin
    direccion_adm_area = admin.aula(direccion_adm_ancho, direccion_adm_largo, description="Dirección Adm.", lado="top")
    area_espera_area = admin.aula(area_espera_ancho, area_espera_largo, description="Área de espera", lado="top")
    sala_reuniones_area = admin.aula(sala_reuniones_ancho, sala_reuniones_largo, description="Sala de Reuniones", lado="top")
    area_ingreso_area = admin.aula(area_ingreso_ancho, area_ingreso_largo, description="Área de ingreso", lado="top")
    sala_profesores_area = admin.aula(sala_profesores_ancho, sala_profesores_largo, description="Sala de Profesores", lado="top")
    sshh_adm_area = admin.aula(sshh_adm_ancho, sshh_adm_largo, description="SSHH Adm.", lado="top")
    admin.centrar_aulas()

    aulas_ciclo1_list = [inicial.aula(ciclo1_ancho, ciclo1_largo, description="Aula Ciclo I", lado="bottom") for _ in range(ciclo1_cantidad)]
    aulas_ciclo2_list = [inicial.aula(ciclo2_ancho, ciclo2_largo, description="Aula Ciclo II", lado="bottom") for _ in range(ciclo2_cantidad)]
    psicomotricidad_area = inicial.aula(psico_ancho, psico_largo, description="Aulas Psicomotricidad", lado="bottom")
    topico_area = inicial.aula(topico_ancho, topico_largo, description="Tópico", lado="bottom")
    lactario_area = inicial.aula(lactario_ancho, lactario_largo, description="Lactario", lado="bottom")
    sshh_inicial_area = inicial.bano(sshh_ancho, sshh_largo, description="SSHH Inicial", lado="bottom")
    cocina_inicial_area = inicial.aula(cocina_ancho, cocina_largo, description="Cocina Inicial", lado="bottom")
    inicial.centrar_aulas()

    pas_inicial, medio, pas_admin = b.areas_m(1.4, "auto",1.4 , direccion="vertical")

    ancho_pas_inicial = inicial.sumar_anchos_aulas_por_piso(1)
    pas_inicial.pasadizo(pas_inicial.ancho, 1.2, piso=1)
    pas_inicial.centrar_pasadizos()


    # escaleras = inicial.escalera(1, 2.4,lado="top")

    ancho_pas_admin = admin.sumar_anchos_aulas_por_piso(1)
    pas_admin.pasadizo(admin.ancho, 1.2, piso=1)
    pas_admin.centrar_pasadizos()

    area_losa_inic, medio_m, sum_m = medio.areas_m(ancho_patio, "auto",largo_sum * 1.4, direccion="vertical")

    # medio.aula(ancho=ancho_losa, largo=largo_losa, description="Losa Deportiva", lado="top")

    # # SUM y Cocina (Deben estar cerca según tu nota)
    sum_m.aula(ancho=ancho_sum, largo=largo_sum, description="SUM", lado="top")
    sum_m.aula(ancho=ancho_cocina, largo=largo_cocina, description="Cocina", lado="top")
    sum_m.centrar_aulas()

    # # Taller EPT (Cerca a secundaria)

    losas, ept =medio_m.areas_m("auto", largo_ept, direccion="horizontal")

    losas.insertar_losas(
        cantidad_losas=3,
        gap=1,
        ancho_losa=ancho_losa,
        largo_losa=largo_losa
    )
    losas.centrar_losas()
    
    if ept.largo >=ancho_ept:
        ept.aula(ancho=ancho_ept, largo=largo_ept, description="Taller EPT", lado="right")
        ept.centrar_aulas()
    # # Patio de Inicial (Cerca al pabellón de inicial)

    # if exist_2do_cuad ==False:
    area_losa_inic.losa(ancho=largo_patio, largo=ancho_patio, description="Patio Inicial")
    area_losa_inic.centrar_losas()

    data =  render2d.get_data()
    # data_to_dict = data.to_dict(orient="records")

    return data, angulo_final

    # render2d.render_3d()
    # render_2 = Render(data_to_dict, pisos=2)
    # render_2.render_2d()



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

def transformar_df_con_referencia(df, df_cuadrante_real):
    """
    Halla el ángulo automáticamente y alinea el tipo 'render' 
    exactamente con el cuadrante real.
    """
    df_result = df.copy()
    
    # 1. REFERENCIAS DE GEOMETRÍA
    g_real = df_cuadrante_real.iloc[0]["geometria"]
    
    df_render = df[df['tipo'] == 'render']
    if df_render.empty:
        raise ValueError("No se encontró objeto tipo 'render' para alinear.")
    g_render_local = df_render.iloc[0]["geometria"]

    # 2. HALLAR ÁNGULO AUTOMÁTICAMENTE
    # Calculamos la orientación de ambos y hallamos la diferencia
    ang_real = obtener_angulo_orientacion(g_real)
    ang_local = obtener_angulo_orientacion(g_render_local)
    
    # El ángulo necesario es la diferencia para que el local sea igual al real
    angulo_necesario = ang_real - ang_local

    # 3. PUNTOS DE ANCLAJE (Centroides para calce perfecto)
    dest_x, dest_y = g_real.centroid.x, g_real.centroid.y
    orig_x, orig_y = g_render_local.centroid.x, g_render_local.centroid.y

    nuevas_geoms = []

    # 4. TRANSFORMACIÓN SOLIDARIA
    for geom in df_result["geometria"]:
        if geom is None:
            nuevas_geoms.append(None)
            continue

        # PASO A: Rotar respecto al centro del RENDER usando el ángulo calculado
        g_rot = affinity.rotate(
            geom, 
            angulo_necesario, 
            origin=(orig_x, orig_y)
        )
        
        # PASO B: Trasladar para que los centros coincidan
        g_final = affinity.translate(
            g_rot, 
            xoff = dest_x - orig_x, 
            yoff = dest_y - orig_y
        )

        nuevas_geoms.append(g_final)

    df_result["geometria"] = nuevas_geoms
    
    # Actualizar coordenadas para el DataFrame
    df_result["x"] = df_result["geometria"].apply(lambda g: g.bounds[0] if g else None)
    df_result["y"] = df_result["geometria"].apply(lambda g: g.bounds[1] if g else None)

    # print(f"✨ Alineación Automática: {angulo_necesario:.2f}° aplicados.")
    
    return df_result