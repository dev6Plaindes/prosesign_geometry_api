import heapq


def encontrar_configuracion_ideal(data, largo_max_terreno=80.0):

    elementos = []

    for row in data:

        elementos.append({
            'nombre': row['Ambientes'],
            'largo': float(row['Largo']),
            'ancho': float(row['Ancho'])
        })

    elementos = sorted(
        elementos,
        key=lambda x: x['largo'],
        reverse=True
    )

    largo_total = sum(
        el['largo'] for el in elementos
    )

    num_pisos = 1

    configuracion_valida = False

    resultado_final = {}

    largo_max_final = 0

    # -------------------------------------------------

    while not configuracion_valida:

        pisos = {}

        heap_pisos = []

        # ---------------------------------------------
        # CREAR PISOS + HEAP
        # ---------------------------------------------

        for i in range(num_pisos):

            piso_id = i + 1

            piso_data = {
                "largo_acumulado": 0.0,
                "ambientes": [],
                "largos": [],
                "anchos": []
            }

            pisos[piso_id] = piso_data

            # (prioridad, id_piso)
            heapq.heappush(
                heap_pisos,
                (0.0, piso_id)
            )

        # ---------------------------------------------
        # DISTRIBUCIÓN GREEDY
        # ---------------------------------------------

        for el in elementos:

            # sacar el piso menos lleno
            largo_actual, piso_id = heapq.heappop(
                heap_pisos
            )

            piso = pisos[piso_id]

            nuevo_largo = (
                largo_actual + el['largo']
            )

            piso['largo_acumulado'] = nuevo_largo

            piso['ambientes'].append(
                el['nombre']
            )

            piso['largos'].append(
                el['largo']
            )

            piso['anchos'].append(
                el['ancho']
            )

            # volver a insertarlo actualizado
            heapq.heappush(
                heap_pisos,
                (nuevo_largo, piso_id)
            )

        # ---------------------------------------------
        # EL MÁS GRANDE
        # ---------------------------------------------

        largo_piso_maximo = max(
            p['largo_acumulado']
            for p in pisos.values()
        )

        # ---------------------------------------------

        if largo_piso_maximo <= largo_max_terreno:

            configuracion_valida = True

            resultado_final = pisos

            largo_max_final = largo_piso_maximo

        else:

            num_pisos += 1

            if num_pisos > 30:

                return (
                    "Error: Los ambientes son demasiado "
                    "largos para el terreno o exceden 30 pisos."
                )

    # -------------------------------------------------

    return {
        "Pisos_Ideales": num_pisos,
        "Largo_Contenedor": round(largo_max_final, 2),
        "Promedio_Teorico": round(
            largo_total / num_pisos,
            2
        ),
        "Detalle": resultado_final
    }