# algoritm_packing.pyx
def obtener_largo(x):
    return x['largo']

cpdef encontrar_configuracion_ideal(
    list data,
    double largo_max_terreno=80.0
):

    cdef:
        list elementos = []
        dict row
        dict el
        dict piso_data
        double largo_total = 0.0
        int num_pisos = 1
        bint configuracion_valida = False
        dict resultado_final = {}
        double largo_max_final = 0.0
        dict pisos
        int piso_mas_vacio
        double largo_piso_maximo
        double min_largo
        int p

    # -------------------------------------------------
    # PREPARAR ELEMENTOS
    # -------------------------------------------------

    for row in data:

        elementos.append({
            'nombre': row['Ambientes'],
            'largo': float(row['Largo']),
            'ancho': float(row['Ancho'])
        })

    elementos = sorted(
        elementos,
        key=obtener_largo,
        reverse=True
    )

    for el in elementos:
        largo_total += el['largo']

    # -------------------------------------------------
    # LOOP PRINCIPAL
    # -------------------------------------------------

    while not configuracion_valida:

        pisos = {}

        for p in range(1, num_pisos + 1):

            pisos[p] = {
                "largo_acumulado": 0.0,
                "ambientes": [],
                "largos": [],
                "anchos": []
            }

        # ---------------------------------------------

        for el in elementos:

            min_largo = 999999999.0
            piso_mas_vacio = 1

            for p in pisos:

                if pisos[p]['largo_acumulado'] < min_largo:

                    min_largo = pisos[p]['largo_acumulado']
                    piso_mas_vacio = p

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

        # ---------------------------------------------

        largo_piso_maximo = 0.0

        for piso_data in pisos.values():

            if piso_data['largo_acumulado'] > largo_piso_maximo:

                largo_piso_maximo = piso_data['largo_acumulado']

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