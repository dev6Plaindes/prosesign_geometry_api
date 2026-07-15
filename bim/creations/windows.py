from bim.config_proyect import CONFIG_PROYECTO
import cadquery as cq

def _generate_windows_by_room(
    inicio_hab_x: float,
    fin_hab_x: float,
    desplazamiento_y: float,
    ancho_total_hab: float,
    desfase_z: float,
    pos_columnas: list,
    desplazamiento_x: float,
    posicion_puerta: str,
    rango_puerta_x: list = None
):
    """
    Genera ventanas exclusivamente en el espacio útil
    después de la puerta y evitando columnas.
    """

    e_muro = CONFIG_PROYECTO['e_muro']

    alto_ventana = 1.20
    alfeizar_z = 1.00
    espesor_vidrio = 0.02

    margen_seguridad = 0.20

    # =========================================================
    # POSICIÓN Y DE VENTANA
    # =========================================================
    if posicion_puerta.lower() == "bottom":

        centro_y_ventana = (
            desplazamiento_y
            + (e_muro / 2)
        )

    else:

        centro_y_ventana = (
            desplazamiento_y
            + ancho_total_hab
            - (e_muro / 2)
        )

    # =========================================================
    # INICIO REAL DE VENTANAS
    # =========================================================
    if (
        rango_puerta_x
        and inicio_hab_x <= rango_puerta_x[0] <= fin_hab_x
    ):

        inicio_ventanas = (
            rango_puerta_x[1]
            + margen_seguridad
        )

    else:

        inicio_ventanas = (
            inicio_hab_x
            + margen_seguridad
        )

    limite_fin_hab = (
        fin_hab_x
        - margen_seguridad
    )

    # =========================================================
    # VALIDACIÓN DE ESPACIO
    # =========================================================
    if inicio_ventanas >= limite_fin_hab:

        return [], []

    # =========================================================
    # TRAMO INICIAL DISPONIBLE
    # =========================================================
    tramos_disponibles = [
        [inicio_ventanas, limite_fin_hab]
    ]

    # =========================================================
    # RECORTE POR COLUMNAS
    # =========================================================
    for col_ini, col_fin in pos_columnas:

        col_g_ini = col_ini + desplazamiento_x
        col_g_fin = col_fin + desplazamiento_x

        if (
            col_g_fin < inicio_ventanas
            or col_g_ini > limite_fin_hab
        ):
            continue

        limite_col_izq = (
            col_g_ini - margen_seguridad
        )

        limite_col_der = (
            col_g_fin + margen_seguridad
        )

        nuevos_tramos = []

        for t_ini, t_fin in tramos_disponibles:

            if (
                limite_col_izq < t_fin
                and limite_col_der > t_ini
            ):

                if t_ini < limite_col_izq:

                    nuevos_tramos.append([
                        t_ini,
                        limite_col_izq
                    ])

                if limite_col_der < t_fin:

                    nuevos_tramos.append([
                        limite_col_der,
                        t_fin
                    ])

            else:

                nuevos_tramos.append([
                    t_ini,
                    t_fin
                ])

        tramos_disponibles = nuevos_tramos

    # =========================================================
    # GEOMETRÍA FINAL
    # =========================================================
    cortadores = []
    paneles_vidrio = []

    for t_ini, t_fin in tramos_disponibles:

        largo_ventana = t_fin - t_ini

        if largo_ventana < 0.20:
            continue

        # [DOCUMENTACIÓN] Subdivisión de ventanas largas en módulos realistas (1.50m máximo separados por muros de 0.60m)
        # para que la fachada del pabellón no tenga paños de vidrio gigantescos y se asemeje a un diseño modular real.
        sub_tramos = []
        if largo_ventana > 2.0:
            target_w = 1.50
            separator_w = 0.60
            n_ventanas = int((largo_ventana + separator_w) // (target_w + separator_w))
            if n_ventanas < 1:
                n_ventanas = 1
            
            ancho_total_modulos = n_ventanas * target_w + (n_ventanas - 1) * separator_w
            desfase_inicio = (largo_ventana - ancho_total_modulos) / 2
            
            puntero_x = t_ini + desfase_inicio
            for _ in range(n_ventanas):
                sub_tramos.append((puntero_x, puntero_x + target_w))
                puntero_x += target_w + separator_w
        else:
            sub_tramos.append((t_ini, t_fin))

        for sub_ini, sub_fin in sub_tramos:
            largo_sub_v = sub_fin - sub_ini
            centro_x_w = (sub_ini + sub_fin) / 2

            centro_z_w = (
                desfase_z
                + alfeizar_z
                + (alto_ventana / 2)
            )

            # -----------------------------------------------------
            # VANO
            # -----------------------------------------------------
            cortador = (
                cq.Workplane("XY")
                .box(
                    largo_sub_v,
                    e_muro + 0.2,
                    alto_ventana
                )
                .translate((
                    centro_x_w,
                    centro_y_ventana,
                    centro_z_w
                ))
            )

            cortadores.append(cortador)

            # -----------------------------------------------------
            # VIDRIO
            # -----------------------------------------------------
            panel = (
                cq.Workplane("XY")
                .box(
                    largo_sub_v,
                    espesor_vidrio,
                    alto_ventana
                )
                .translate((
                    centro_x_w,
                    centro_y_ventana,
                    centro_z_w
                ))
            )

            paneles_vidrio.append(panel)

    return cortadores, paneles_vidrio
