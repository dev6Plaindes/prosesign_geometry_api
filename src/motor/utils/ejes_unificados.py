def calcular_ejes_unificados(ambientes):
    """
    ambientes:
    list[dict]

    Retorna:
    (
        resumen_por_piso,
        ejes_finales
    )
    """

    todos_los_puntos = set()
    pisos = {}

    # ====================================
    # AGRUPAR POR PISO
    # ====================================
    for amb in ambientes:

        piso_id = amb["ID_Piso"]

        if piso_id not in pisos:
            pisos[piso_id] = []

        pisos[piso_id].append(amb)

    # ====================================
    # CALCULAR PUNTOS CRÍTICOS
    # ====================================
    for piso_id, grupo in pisos.items():

        acumulado = 0.0

        # inicio común
        todos_los_puntos.add(0.0)

        for fila in grupo:

            largo = fila["Largo_Individual"]

            # Regla:
            # ambientes > 8m tienen columna intermedia
            if largo > 8:

                punto_medio = acumulado + (largo / 2)

                todos_los_puntos.add(
                    round(punto_medio, 3)
                )

            # Unión entre ambientes
            acumulado += largo

            todos_los_puntos.add(
                round(acumulado, 3)
            )

    # ====================================
    # Ejes finales unificados
    # ====================================
    ejes_finales = sorted(todos_los_puntos)

    # ====================================
    # Resumen por piso
    # ====================================
    resumen = []

    total_columnas = len(ejes_finales)

    for piso_id in pisos:

        resumen.append({
            "ID_Piso": piso_id,
            "Ejes_Columnas_Alineados": ejes_finales,
            "Total_Columnas": total_columnas
        })

    return resumen, ejes_finales