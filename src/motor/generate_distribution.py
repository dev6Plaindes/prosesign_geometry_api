import math


def auto_distribution_ambientes_y(
    ambientes,
    largo_cuadrante,
    pabellon="Izquierda"
):
    """
    Version SIN pandas.
    Mantiene EXACTAMENTE la misma lógica.
    """

    # =========================
    # MEDIDAS
    # =========================
    largo_escalera = (2.4 + 0.25) * 2
    largo_banios = 4

    espacio_escalera_banio = largo_escalera + largo_banios

    largo_restante = largo_cuadrante - espacio_escalera_banio

    # =========================
    # FILTRADO
    # =========================
    df_ambientes = []

    for row in ambientes:

        nombre = row["Ambientes"]

        if 'SSHH' in nombre:
            continue

        if 'Escalera' in nombre:
            continue

        df_ambientes.append(row)

    # =========================
    # FILTRAR PABELLÓN
    # =========================
    df_pabellon = []

    for row in df_ambientes:

        if row["Pabellon"] == pabellon:
            df_pabellon.append(row)

    # =========================
    # EXPANDIR POR CANTIDAD
    # =========================
    df_pabellon_exp = []

    for row in df_pabellon:

        cantidad = int(row["Cantidad"])

        for _ in range(cantidad):

            df_pabellon_exp.append({
                "Ambientes": row["Ambientes"],
                "Largo": float(row["Largo"]),
                "Ancho": float(row["Ancho"])
            })

    # =========================
    # SUMA LARGOS
    # =========================
    sum_largo_ambientes_prim = sum(
        row["Largo"]
        for row in df_pabellon_exp
    )

    # =========================
    # CANTIDAD PISOS
    # =========================
    if sum_largo_ambientes_prim <= largo_restante:

        cantidad_pisos_prim = 1

    else:

        cantidad_pisos_prim = max(
            1,
            math.ceil(
                sum_largo_ambientes_prim / largo_restante
            )
        )

    # =========================
    # RECUPERAR ESPACIO ESCALERA
    # =========================
    if cantidad_pisos_prim == 1:

        largo_restante = (
            largo_cuadrante - largo_banios
        )

    # =========================
    # MISMA LÓGICA ORIGINAL
    # (aunque no se use)
    # =========================
    cantidad_aulas = len(df_pabellon_exp)

    aulas_por_piso = (
        int(cantidad_aulas // cantidad_pisos_prim)
        if cantidad_pisos_prim > 0
        else cantidad_aulas
    )

    # =========================
    # SOLUCIÓN
    # =========================
    solucion = encontrar_configuracion_ideal(
        df_pabellon_exp,
        largo_max_terreno=largo_restante
    )

    if isinstance(solucion, str):
        return solucion

    df_final = solucion_a_lista(
        solucion["Detalle"]
    )

    # =========================
    # GROUPBY PISO
    # =========================
    ambientes_por_piso = {}

    for row in df_final:

        piso = row["Piso"]

        if piso not in ambientes_por_piso:
            ambientes_por_piso[piso] = []

        ambientes_por_piso[piso].append(row)

    largo_contenedor_sol = solucion["Largo_Contenedor"]

    # =========================
    # MANTENER EXACTAMENTE
    # LA MISMA LÓGICA ORIGINAL
    # =========================
    for num_piso, datos_piso in ambientes_por_piso.items():

        for row in datos_piso:

            row["ID_Piso"] = f"PISO_{num_piso}"

        cantidad_ambientes = len(datos_piso)

        largo_actual_piso = (
            datos_piso[0]["Largo_Total_Piso"]
        )

        if largo_actual_piso < largo_contenedor_sol:

            m_faltante = (
                largo_contenedor_sol
                - largo_actual_piso
            )

            m_aprox_unit = (
                m_faltante / cantidad_ambientes
            )

            # EXACTAMENTE igual
            for row in datos_piso:

                row["Largo_Individual"] += (
                    m_aprox_unit
                )

            for row in datos_piso:

                row["Largo_Total_Piso"] = (
                    largo_contenedor_sol
                )

    # =========================
    # CONCAT
    # =========================
    df_final_procesado = []

    for datos_piso in ambientes_por_piso.values():

        df_final_procesado.extend(datos_piso)

    return df_final_procesado


def encontrar_configuracion_ideal(
    df,
    largo_max_terreno=80.0
):
    """
    MISMA lógica original.
    """

    # =========================
    # EXTRAER ELEMENTOS
    # =========================
    elementos = []

    for row in df:

        elementos.append({
            'nombre': row['Ambientes'],
            'largo': float(row['Largo']),
            'ancho': float(row['Ancho'])
        })

    # =========================
    # ORDENAR
    # =========================
    elementos = sorted(
        elementos,
        key=lambda x: x['largo'],
        reverse=True
    )

    largo_total = sum(
        el['largo']
        for el in elementos
    )

    num_pisos = 1

    configuracion_valida = False

    resultado_final = {}

    largo_max_final = 0

    while not configuracion_valida:

        pisos = {
            i + 1: {
                "largo_acumulado": 0.0,
                "ambientes": [],
                "largos": [],
                "anchos": []
            }
            for i in range(num_pisos)
        }

        # =========================
        # DISTRIBUCIÓN
        # =========================
        for el in elementos:

            piso_mas_vacio = min(
                pisos,
                key=lambda p:
                pisos[p]['largo_acumulado']
            )

            pisos[piso_mas_vacio][
                'largo_acumulado'
            ] += el['largo']

            pisos[piso_mas_vacio][
                'ambientes'
            ].append(el['nombre'])

            pisos[piso_mas_vacio][
                'largos'
            ].append(el['largo'])

            pisos[piso_mas_vacio][
                'anchos'
            ].append(el['ancho'])

        # =========================
        # VALIDACIÓN
        # =========================
        largo_piso_maximo = max(
            p['largo_acumulado']
            for p in pisos.values()
        )

        if largo_piso_maximo <= largo_max_terreno:

            configuracion_valida = True

            resultado_final = pisos

            largo_max_final = largo_piso_maximo

        else:

            num_pisos += 1

            if num_pisos > 30:

                return (
                    "Error: Los ambientes "
                    "son demasiado largos "
                    "para el terreno "
                    "o exceden 30 pisos."
                )

    return {
        "Pisos_Ideales": num_pisos,
        "Largo_Contenedor": round(
            largo_max_final,
            2
        ),
        "Promedio_Teorico": round(
            largo_total / num_pisos,
            2
        ),
        "Detalle": resultado_final
    }


def solucion_a_lista(solucion_dict):

    filas = []

    for num_piso, contenido in solucion_dict.items():

        for nombre, largo, ancho in zip(
            contenido['ambientes'],
            contenido['largos'],
            contenido['anchos']
        ):

            filas.append({
                'Piso': num_piso,
                'Ambiente': nombre,
                'Largo_Individual': largo,
                'Ancho_Individual': ancho,
                'Largo_Total_Piso':
                    contenido['largo_acumulado']
            })

    return filas