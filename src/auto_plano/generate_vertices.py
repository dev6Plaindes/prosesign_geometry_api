

from src.auto_plano.render import Motor2D


def generate_geometry(df_excel, df_cuadrante_max):
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

    sshh_inicial = df_pab_inicial[df_pab_inicial["Ambientes"]=="SSHH Inicial"]
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
    
    ancho_c = df_cuadrante_max["ancho"][0]
    largo_c = df_cuadrante_max["largo"][0]

    max_largo = largo_c if ancho_c > largo_c else ancho_c
    max_ancho = ancho_c if ancho_c > largo_c else largo_c

    render2d = Motor2D(ancho = max_ancho, largo = max_largo)
    primaria, pas_prim, a, pas_sec, secundaria = render2d.areas_m(aula_in_ancho_prim, 1.2, "auto", 1.2, aula_in_ancho_sec, direccion="horizontal") # areas

    # primaria
    aula_in_prim = primaria.aula(aula_in_ancho_prim, aula_in_largo_prim, description="Aula de Innovacion")
    biblioteca_prim = primaria.aula(biblio_ancho_prim, biblio_largo_prim, description="Biblioteca")
    taller_prim = primaria.aula(taller_ancho_prim, taller_largo_prim, description="Taller creativo")
    aulas_prim = [primaria.aula(ancho_prim, largo_prim, description="Aula Primaria") for _ in range(cantidad_prim)]

    ancho_pas_prim = primaria.sumar_largos_aulas_por_piso(1)
    pas_prim.pasadizo(1.2 , ancho_pas_prim, piso=1)

    # secundaria
    aula_in_sec = secundaria.aula(aula_in_ancho_sec, aula_in_largo_sec, description="Aula de Innovacion", lado="left")
    biblioteca_sec = secundaria.aula(biblio_ancho_sec, biblio_largo_sec, description="Biblioteca", lado="left")
    taller_sec = secundaria.aula(taller_ancho_sec, taller_largo_sec, description="Taller creativo", lado="left")
    aulas_sec = [secundaria.aula(ancho_sec, largo_sec, description="Aula Secundaria", lado="left") for _ in range(cantidad_sec)]

    ancho_pas_sec = secundaria.sumar_largos_aulas_por_piso(1)
    pas_sec.pasadizo(1.2 , ancho_pas_sec, piso=1)

    inicial, b, admin = a.areas_m(ciclo1_largo, "auto",direccion_adm_largo, direccion="vertical")

    # admin
    direccion_adm_area = admin.aula(direccion_adm_ancho, direccion_adm_largo, description="Dirección Adm.", lado="top")
    area_espera_area = admin.aula(area_espera_ancho, area_espera_largo, description="Área de espera", lado="top")
    sala_reuniones_area = admin.aula(sala_reuniones_ancho, sala_reuniones_largo, description="Sala de Reuniones", lado="top")
    area_ingreso_area = admin.aula(area_ingreso_ancho, area_ingreso_largo, description="Área de ingreso", lado="top")
    sala_profesores_area = admin.aula(sala_profesores_ancho, sala_profesores_largo, description="Sala de Profesores", lado="top")
    sshh_adm_area = admin.aula(sshh_adm_ancho, sshh_adm_largo, description="SSHH Adm.", lado="top")
    admin.centrar_aulas()
    
    admin.create_columns_from_aulas(pos="B", heigth=5)
    admin.create_techos()

    # Inicial
    aulas_ciclo1_list = [inicial.aula(ciclo1_ancho, ciclo1_largo, description="Aula Ciclo I", lado="bottom") for _ in range(ciclo1_cantidad)]
    aulas_ciclo2_list = [inicial.aula(ciclo2_ancho, ciclo2_largo, description="Aula Ciclo II", lado="bottom") for _ in range(ciclo2_cantidad)]
    psicomotricidad_area = inicial.aula(psico_ancho, psico_largo, description="Aulas Psicomotricidad", lado="bottom")
    topico_area = inicial.aula(topico_ancho, topico_largo, description="Tópico", lado="bottom")
    lactario_area = inicial.aula(lactario_ancho, lactario_largo, description="Lactario", lado="bottom")
    sshh_inicial_area = inicial.aula(sshh_ancho, sshh_largo, description="SSHH Inicial", lado="bottom")
    cocina_inicial_area = inicial.aula(cocina_ancho, cocina_largo, description="Cocina Inicial", lado="bottom")
    inicial.centrar_aulas()
    
    inicial.create_columns_from_aulas()
    inicial.create_techos()

    pas_inicial, medio, pas_admin = b.areas_m(1.4, "auto",1.4 , direccion="vertical")

    ancho_pas_inicial = inicial.sumar_anchos_aulas_por_piso(1)
    pas_inicial.pasadizo(ancho_pas_inicial, 1.2, piso=1)
    pas_inicial.centrar_pasadizos()

    ancho_pas_admin = admin.sumar_anchos_aulas_por_piso(1)
    pas_admin.pasadizo(ancho_pas_admin, 1.2, piso=1)
    pas_admin.centrar_pasadizos()

    area_losa_inic, medio_m, sum_m = medio.areas_m(ancho_patio, "auto",largo_sum , direccion="vertical")


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
        
    ept.create_columns_from_aulas(heigth=largo_ept)
    ept.create_techos()
    
    # # Patio de Inicial (Cerca al pabellón de inicial)
    area_losa_inic.losa(ancho=largo_patio, largo=ancho_patio, description="Patio Inicial")
    area_losa_inic.centrar_losas()
    
    # render2d.render()
    
    return render2d.get_data()