import cadquery as cq

def _generate_beams_geometry(
    pos_columnas: list,
    desplazamiento_x: float,
    desplazamiento_y: float,
    ancho_total_hab: float,
    ancho_col: float,
    alto_muro: float,       # El 'alto' de tus muros/columnas actuales
    desfase_z: float
):
    """
    Genera el sistema de vigas aéreas (longitudinales y transversales)
    conectando los centros superiores de las columnas calculadas.
    """
    ancho_viga = 0.30
    alto_viga = 0.30

    # La base de la viga se apoya exactamente donde termina el muro/columna
    z_centro = alto_muro + (alto_viga / 2) + desfase_z

    # Coordenadas fijas en Y para los ejes de las columnas
    y_inf = desplazamiento_y + (ancho_col / 2)
    y_sup = desplazamiento_y + ancho_total_hab - (ancho_col / 2)

    vigas_list = []

    # Convertimos los centros locales de las columnas a globales en X
    centros_x = [((c_init + c_end) / 2) + desplazamiento_x for c_init, c_end in pos_columnas]

    # 1. Generar Vigas Longitudinales (Eje X) y Transversales (Eje Y)
    for i in range(len(centros_x)):
        x_actual = centros_x[i]

        # --- Vigas Transversales (Amarran el ancho del edificio en Y) ---
        # Conectan la columna inferior con la superior en la misma posición X
        largo_viga_y = y_sup - y_inf
        viga_transversal = (
            cq.Workplane("XY")
            .box(ancho_viga, largo_viga_y, alto_viga)
            .translate((x_actual, (y_inf + y_sup) / 2, z_centro))
        )
        vigas_list.append(viga_transversal)

        # --- Vigas Longitudinales (Corren por todo el largo en X) ---
        # Conectan la columna actual con la siguiente (i a i+1)
        if i < len(centros_x) - 1:
            x_siguiente = centros_x[i + 1]
            largo_viga_x = x_siguiente - x_actual
            centro_viga_x = (x_actual + x_siguiente) / 2

            # Viga longitudinal fila inferior
            viga_long_inf = (
                cq.Workplane("XY")
                .box(largo_viga_x, ancho_viga, alto_viga)
                .translate((centro_viga_x, y_inf, z_centro))
            )
            # Viga longitudinal fila superior
            viga_long_sup = (
                cq.Workplane("XY")
                .box(largo_viga_x, ancho_viga, alto_viga)
                .translate((centro_viga_x, y_sup, z_centro))
            )

            vigas_list.append(viga_long_inf)
            vigas_list.append(viga_long_sup)

    # Unificamos todos los sólidos de las vigas en un único objeto compuesto
    vigas_unificadas = vigas_list[0]
    for viga in vigas_list[1:]:
        vigas_unificadas = vigas_unificadas.union(viga)

    return vigas_unificadas