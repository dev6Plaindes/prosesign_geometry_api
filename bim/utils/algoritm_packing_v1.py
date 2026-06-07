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

        for el in elementos:

            piso_mas_vacio = min(
                pisos,
                key=lambda p: pisos[p]['largo_acumulado']
            )

            pisos[piso_mas_vacio]['largo_acumulado'] += el['largo']

            pisos[piso_mas_vacio]['ambientes'].append(
                el['nombre']
            )

            pisos[piso_mas_vacio]['largos'].append(
                el['largo']
            )

            pisos[piso_mas_vacio]['anchos'].append(
                el['ancho']
            )

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
                    "Error: Los ambientes son demasiado "
                    "largos para el terreno o exceden 30 pisos."
                )

    return {
        "Pisos_Ideales": num_pisos,
        "Largo_Contenedor": round(largo_max_final, 2),
        "Promedio_Teorico": round(
            largo_total / num_pisos,
            2
        ),
        "Detalle": resultado_final
    }
