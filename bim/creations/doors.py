from bim.config_proyect import CONFIG_PROYECTO
import cadquery as cq

def _generate_door_geometry(
    posicion_puerta: str,
    borde_x: float,
    l_hab: float,
    desplazamiento_y: float,
    ancho_total_hab: float,
    desfase_z: float,
    pos_columnas: list,
    desplazamiento_x: float,
    lado_puerta: str = "left"
):
    """Calcula la posición y genera el sólido de la puerta y su cortador de vano,
    evitando colisiones transformando pos_columnas a coordenadas globales.
    """
    # Dimensiones estándar fijas
    ancho_p = 0.90
    alto_p = 2.10
    mocheta = 0.30
    
    e_muro = CONFIG_PROYECTO['e_muro']

    posicion = posicion_puerta.lower()

    # 1. Definición inicial en coordenadas globales de la escena
    if posicion == "bottom":
        p_box_x, p_box_y = ancho_p, e_muro
        if lado_puerta == "right":
            p_centro_x = borde_x + l_hab - mocheta - (ancho_p / 2)
        else:
            p_centro_x = borde_x + mocheta + (ancho_p / 2)
        p_centro_y = desplazamiento_y + (e_muro / 2)

    elif posicion == "top":
        p_box_x, p_box_y = ancho_p, e_muro
        if lado_puerta == "right":
            p_centro_x = borde_x + l_hab - mocheta - (ancho_p / 2)
        else:
            p_centro_x = borde_x + mocheta + (ancho_p / 2)
        p_centro_y = desplazamiento_y + ancho_total_hab - (e_muro / 2)

    elif posicion == "left":
        p_box_x, p_box_y = e_muro, ancho_p
        p_centro_x = borde_x
        p_centro_y = desplazamiento_y + e_muro + mocheta + (ancho_p / 2)

    elif posicion == "right":
        p_box_x, p_box_y = e_muro, ancho_p
        p_centro_x = borde_x + l_hab + e_muro
        p_centro_y = desplazamiento_y + e_muro + mocheta + (ancho_p / 2)
    else:
        return None, None

    # 2. Algoritmo de evasión en coordenadas globales absolutas
    holgura = mocheta

    if posicion in ["bottom", "top"]:
        # Rango ocupado por la puerta en el eje X global
        puerta_izq_global = p_centro_x - (ancho_p / 2)
        puerta_der_global = puerta_izq_global + ancho_p

        if lado_puerta == "right":
            # Iteramos sobre las columnas convirtiéndolas a la misma escala global
            for col_inicio, col_fin in pos_columnas:
                # Mapeamos la columna local sumándole el desplazamiento_x inicial del bloque
                col_inicio_global = col_inicio + desplazamiento_x
                col_fin_global = col_fin + desplazamiento_x

                # Límites de la columna con su respectiva holgura de seguridad
                zona_col_izq = col_inicio_global - holgura
                zona_col_der = col_fin_global + holgura

                # Verificar solapamiento de intervalos en X global
                if max(puerta_izq_global, zona_col_izq) < min(puerta_der_global, zona_col_der):
                    # Desplazamos el inicio de la puerta a la izquierda de la columna
                    puerta_der_global = zona_col_izq
                    puerta_izq_global = puerta_der_global - ancho_p

            # Re-calculamos el centro X global tras resolver todos los conflictos
            p_centro_x = puerta_izq_global + (ancho_p / 2)

            # Restricción perimetral: No permitir que la puerta escape del final de su respectiva habitación
            limite_izquierdo_hab = borde_x
            if (p_centro_x - (ancho_p / 2)) < limite_izquierdo_hab:
                # Fallback dinámico: Pegamos la puerta al inicio derecho del muro de esta habitación
                p_centro_x = borde_x + l_hab - (ancho_p / 2)
                puerta_der_global = p_centro_x + (ancho_p / 2)
                for col_inicio, col_fin in pos_columnas:
                    col_inicio_global = col_inicio + desplazamiento_x
                    col_fin_global = col_fin + desplazamiento_x
                    if max(puerta_der_global - ancho_p, col_inicio_global - holgura) < min(puerta_der_global, col_fin_global + holgura):
                        # Si choca, la empujamos a la izquierda de esa columna
                        p_centro_x = col_inicio_global - holgura - (ancho_p / 2)
                        break
        else:
            # Iteramos sobre las columnas convirtiéndolas a la misma escala global
            for col_inicio, col_fin in pos_columnas:
                col_inicio_global = col_inicio + desplazamiento_x
                col_fin_global = col_fin + desplazamiento_x

                zona_col_izq = col_inicio_global - holgura
                zona_col_der = col_fin_global + holgura

                if max(puerta_izq_global, zona_col_izq) < min(puerta_der_global, zona_col_der):
                    puerta_izq_global = zona_col_der
                    puerta_der_global = puerta_izq_global + ancho_p

            p_centro_x = puerta_izq_global + (ancho_p / 2)

            limite_derecho_hab = borde_x + l_hab
            if (p_centro_x + (ancho_p / 2)) > limite_derecho_hab:
                p_centro_x = borde_x + (ancho_p / 2)
                puerta_izq_global = p_centro_x - (ancho_p / 2)
                for col_inicio, col_fin in pos_columnas:
                    col_inicio_global = col_inicio + desplazamiento_x
                    col_fin_global = col_fin + desplazamiento_x
                    if max(puerta_izq_global, col_inicio_global - holgura) < min(puerta_izq_global + ancho_p, col_fin_global + holgura):
                        p_centro_x = col_inicio_global + holgura + (ancho_p / 2)
                        break

    elif posicion in ["left", "right"]:
        ancho_col = CONFIG_PROYECTO['ancho_col']
        puerta_inf = p_centro_y - (ancho_p / 2)
        puerta_sup = p_centro_y + (ancho_p / 2)

        if puerta_inf < (desplazamiento_y + ancho_col + holgura):
            p_centro_y = desplazamiento_y + ancho_col + holgura + (ancho_p / 2)
        elif puerta_sup > (desplazamiento_y + ancho_total_hab - ancho_col - holgura):
            p_centro_y = desplazamiento_y + ancho_total_hab - ancho_col - holgura - (ancho_p / 2)

    # 3. Construcción geométrica final
    espesor_cortador_x = p_box_x + 0.1 if posicion in ["left", "right"] else p_box_x
    espesor_cortador_y = p_box_y + 0.1 if posicion in ["top", "bottom"] else p_box_y

    z_pos = (alto_p / 2) + desfase_z

    cortador_vano = (
        cq.Workplane("XY")
        .box(espesor_cortador_x, espesor_cortador_y, alto_p)
        .translate((p_centro_x, p_centro_y, z_pos))
    )

    bloque_puerta = (
        cq.Workplane("XY")
        .box(p_box_x, p_box_y, alto_p)
        .translate((p_centro_x, p_centro_y, z_pos))
    )

    if posicion in ["bottom", "top"]:
        x_inicio_puerta = p_centro_x - (ancho_p / 2)
        x_fin_puerta = p_centro_x + (ancho_p / 2)

    else:
        # Para left/right usamos igualmente X global
        x_inicio_puerta = p_centro_x - (e_muro / 2)
        x_fin_puerta = p_centro_x + (e_muro / 2)

    rango_puerta_x = [
        x_inicio_puerta,
        x_fin_puerta
    ]

    return (
        cortador_vano,
        bloque_puerta,
        rango_puerta_x
    )