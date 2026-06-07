from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.doors import _generate_door_geometry
from bim.creations.escaleras import create_stairs
from bim.creations.techos.techo_z1 import create_techo_z_1
from bim.creations.vigas import _generate_beams_geometry
from bim.creations.windows import _generate_windows_by_room
from bim.utils.algoritm_distibution import calcular_posiciones_columnas, encontrar_largo_equilibrado
import cadquery as cq
from bim.capas import FactoryCapas

def create_structure(
    ensamblaje,
    largos_habitaciones: list,
    ancho_hab: float,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    largo_bloque_fijo: float,
    posicion_puerta: str = "bottom",
    nivel=1,
    max_nivel =1,
    orientacion: str = "horizontal",
    names_ambientes: list = None,
    factory_capas: FactoryCapas = None
):
    """
    Construye UN solo bloque modular de ambientes variables (alineadas en X o Y).
    Garantiza consistencia 3D e integra puertas y ventanas analizadas por habitación.
    """

    altura_piso = CONFIG_PROYECTO['alto_nivel']
    alto = CONFIG_PROYECTO['alto_nivel']
    e_muro = CONFIG_PROYECTO['e_muro']

    ancho_col = CONFIG_PROYECTO['ancho_col']
    desfase_z = (nivel - 1) * altura_piso

    largo_total_hab = largo_bloque_fijo
    ancho_total_hab = ancho_hab
    ancho_interior = ancho_hab - (e_muro * 2)

    # =========================================================
    # 1. BASE DE MUROS
    # =========================================================
    muros_locales = (
        cq.Workplane("XY")
        .box(largo_total_hab, ancho_total_hab, alto)
        .translate((
            largo_total_hab / 2 + desplazamiento_x,
            ancho_total_hab / 2 + desplazamiento_y,
            (alto / 2) + desfase_z
        ))
    )

    # =========================================================
    # 2. COLUMNAS
    # =========================================================
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

        centro_x_columna = (
            ((col_inicio + col_fin) / 2)
            + desplazamiento_x
        )

        esquinas_globales.update([
            (centro_x_columna, pos_y_inferior),
            (centro_x_columna, pos_y_superior)
        ])

    # =========================================================
    # 3. REDIMENSIONAMIENTO DE HABITACIONES
    # =========================================================
    num_hab = len(largos_habitaciones)

    espacio_muros_interiores = (num_hab + 1) * e_muro

    espacio_neto_disponible = (
        largo_total_hab
        - espacio_muros_interiores
    )

    suma_largos_originales = largo_total_hab

    largos_corregidos = [
        (l / suma_largos_originales) * espacio_neto_disponible
        for l in largos_habitaciones
    ]

    # =========================================================
    # 4. HABITACIONES
    # =========================================================
    borde_x = desplazamiento_x + e_muro

    puertas_lista = []
    ventanas_cortadores = []
    ventanas_paneles_lista = []

    for idx, l_hab in enumerate(largos_corregidos):

        centro_x = borde_x + (l_hab / 2)

        centro_y = (
            desplazamiento_y
            + e_muro
            + (ancho_interior / 2)
        )

        # -----------------------------------------------------
        # VACIADO INTERIOR
        # -----------------------------------------------------
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
        
        # -----------------------------------------------------
        # 🆕 AGREGAR VOLUMEN / GEOMETRÍA DEL AMBIENTE PARA LA LEYENDA
        # -----------------------------------------------------
        # 1. Obtener el nombre del ambiente con el formato [ambiente]
        if names_ambientes and idx < len(names_ambientes):
            ambiente_base = names_ambientes[idx] # ◄--- Cambiado de idx + 1 a idx
        else:
            ambiente_base = f"Ambiente_{idx + 1}"
        
        nombre_ambiente_formato = f"[{ambiente_base} {idx + 1}]"

        # 2. Crear la caja del tamaño exacto del espacio de la habitación
        # Usamos una altura representativa (por ejemplo, 0.1 o el alto total si deseas el volumen completo)
        geometria_ambiente = (
            cq.Workplane("XY")
            .box(l_hab, ancho_interior, alto) # Mismo tamaño que el cortador
            .translate((
                centro_x,
                centro_y,
                (alto / 2) + desfase_z
            ))
        )

        # 3. Aplicar rotación si la estructura completa es vertical para que coincida con los muros
        if orientacion.lower() == "vertical":
            pivote = (desplazamiento_x, desplazamiento_y, 0)
            geometria_ambiente = geometria_ambiente.rotate(
                pivote,
                (desplazamiento_x, desplazamiento_y, 1),
                90
            )

        # 4. Agregarlo al ensamblaje inmediatamente
        # USO PARA SOMBREAR DE COLOR LOS AMBIENTES
        # factory_capas.add_in_capa_auto(
        #     workplane = geometria_ambiente,
        #     nivel = nivel,
        #     name=f"{nombre_ambiente_formato} {sufijo_nombre} - Nivel {nivel}"
        # )
        
        ensamblaje.add(
            geometria_ambiente, 
            name=f"{nombre_ambiente_formato} {sufijo_nombre} - Nivel {nivel}"
        )

        # -----------------------------------------------------
        # PUERTA
        # -----------------------------------------------------
        (
            cortador_vano,
            bloque_puerta,
            rango_puerta_x
        ) = _generate_door_geometry(
            posicion_puerta,
            borde_x,
            l_hab,
            desplazamiento_y,
            ancho_total_hab,
            desfase_z,
            pos_columnas,
            desplazamiento_x
        )

        if cortador_vano and bloque_puerta:

            muros_locales = muros_locales.cut(cortador_vano)

            puertas_lista.append(bloque_puerta)

        # -----------------------------------------------------
        # VENTANAS
        # -----------------------------------------------------
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
        ventanas_paneles_lista.extend(paneles_w)

        borde_x = borde_x + l_hab + e_muro

    # =========================================================
    # 5. CORTES DE VENTANAS
    # =========================================================
    for cortador_ventana in ventanas_cortadores:

        muros_locales = muros_locales.cut(cortador_ventana)

    # =========================================================
    # 6. COLUMNAS FINALES
    # =========================================================
    altura_total = alto + CONFIG_PROYECTO["ancho_viga"]

    columnas_final = (
        cq.Workplane("XY")
        .pushPoints(list(esquinas_globales))
        .box(ancho_col, ancho_col, altura_total)
        # Trasladamos exactamente la mitad de la altura total para que la base quede en Z = 0, más el desfase
        .translate((0, 0, (altura_total / 2) + desfase_z))
    )

    # =========================================================
    # 7. CORTE BOOLEANO FINAL
    # =========================================================
    muros_final = muros_locales.cut(columnas_final)

    # =========================================================
    # 8. VIGAS
    # =========================================================
    vigas_final = _generate_beams_geometry(
        pos_columnas=pos_columnas,
        desplazamiento_x=desplazamiento_x,
        desplazamiento_y=desplazamiento_y,
        ancho_total_hab=ancho_total_hab,
        ancho_col=ancho_col,
        alto_muro=alto,
        desfase_z=desfase_z
    )

    # =========================================================
    # 9. ROTACIÓN SI ES VERTICAL
    # =========================================================
    if orientacion.lower() == "vertical":

        pivote = (
            desplazamiento_x,
            desplazamiento_y,
            0
        )

        muros_final = muros_final.rotate(
            pivote,
            (desplazamiento_x, desplazamiento_y, 1),
            90
        )

        columnas_final = columnas_final.rotate(
            pivote,
            (desplazamiento_x, desplazamiento_y, 1),
            90
        )

        vigas_final = vigas_final.rotate(
            pivote,
            (desplazamiento_x, desplazamiento_y, 1),
            90
        )

        puertas_lista = [
            p.rotate(
                pivote,
                (desplazamiento_x, desplazamiento_y, 1),
                90
            )
            for p in puertas_lista
        ]

        ventanas_paneles_lista = [
            w.rotate(
                pivote,
                (desplazamiento_x, desplazamiento_y, 1),
                90
            )
            for w in ventanas_paneles_lista
        ]
        
    # ESCALERAS
    if nivel> 1:
        desplazamiento_y_escalera = desplazamiento_y + ancho_hab - 3
        nivel_escalera = nivel - 1
        if posicion_puerta == "bottom":
            desplazamiento_y_escalera = desplazamiento_y
        escalera = create_stairs(
            ensamblaje=ensamblaje,
            ancho_hab=0,
            desplazamiento_x=desplazamiento_x + largo_bloque_fijo,
            desplazamiento_y=desplazamiento_y_escalera,
            sufijo_nombre=sufijo_nombre,
            posicion_puerta=posicion_puerta,      # Se alineará abajo en el eje Y
            nivel=nivel_escalera,                     # Construye en el suelo para subir al Nivel 2
            orientacion="vertical",    # Dirección del desarrollo de la escalera
            huella=0.28,                 # 28 cm de pisada
            contrahuella_max=0.17        # Altura máxima por peldaño (aprox 16.4cm reales)
            )
        
        if orientacion.lower() == "vertical":
            escalera = escalera.rotate(
                pivote,
                (desplazamiento_x, desplazamiento_y, 1),
                90
            )
        name_obj = f"Escalera {sufijo_nombre} - Nivel {nivel_escalera}"

        factory_capas.add_in_capa_auto(
            workplane = escalera,
            nivel = nivel - 1,
            name=name_obj
        )

        ensamblaje.add(escalera, name=name_obj)
        
    # TECHO
    if max_nivel == nivel and CONFIG_PROYECTO["zona_climatica"] == "z1":
        techo = create_techo_z_1(
            ancho_techo=largo_bloque_fijo,
            desplazamiento_x=desplazamiento_x,
            desplazamiento_y=desplazamiento_y,
            sufijo_nombre=sufijo_nombre,
            posicion_puerta=posicion_puerta,
            largo_inclinado=ancho_hab,
            nivel=nivel,
            orientacion=orientacion
        )
        
        ensamblaje.add(techo, name=f"Techo Especial Z1 {sufijo_nombre} - Nivel {nivel}")
        
    

    # =========================================================
    # 10. ENSAMBLAJE FINAL
    # =========================================================
    # MUROS
    ensamblaje.add(
        muros_final,
        name=f"Muros {sufijo_nombre} - Nivel {nivel}"
    )
    
    factory_capas.add_in_capa_auto(
            workplane = muros_final,
            nivel = nivel,
            name=f"Muros {sufijo_nombre} - Nivel {nivel}"
        )

    # COLUMNAS
    ensamblaje.add(
        columnas_final,
        name=f"Columnas {sufijo_nombre} - Nivel {nivel}"
    )
    
    factory_capas.add_in_capa_auto(
            workplane = columnas_final,
            nivel = nivel,
            name=f"Columnas {sufijo_nombre} - Nivel {nivel}"
        )

    # VIGAS
    ensamblaje.add(
        vigas_final,
        name=f"Vigas {sufijo_nombre} - Nivel {nivel}"
    )
    
    factory_capas.add_in_capa_auto(
            workplane = vigas_final,
            nivel = nivel,
            name=f"Vigas {sufijo_nombre} - Nivel {nivel}"
        )

    for i, puerta_solido in enumerate(puertas_lista):

        ensamblaje.add(
            puerta_solido,
            name=f"Puerta {sufijo_nombre} - Nivel {nivel} - {i+1}"
        )

    for j, ventana_solido in enumerate(ventanas_paneles_lista):

        ensamblaje.add(
            ventana_solido,
            name=f"Ventana {sufijo_nombre} - Nivel {nivel} - {j+1}"
        )



