import heapq

def sequential_first_fit_packing(data, largo_max_terreno=80.0, min_floors=1):
    """
    Algoritmo de empaquetado 1D (Sequential First-Fit) para distribuir ambientes en pisos.
    Llena cada piso secuencialmente hasta su capacidad máxima antes de abrir uno nuevo.
    No reordena los ambientes, procesándolos en el orden de entrada.
    """
    elementos = []
    for row in data:
        elementos.append({
            'nombre': row['Ambientes'],
            'largo': float(row['Largo']),
            'ancho': float(row['Ancho'])
        })

    # No ordenar elementos, procesar en el orden de entrada.

    # Validación temprana: si algún ambiente es más grande que el espacio disponible, es un error.
    for el in elementos:
        if el['largo'] > largo_max_terreno:
            return (
                f"Error: El ambiente '{el['nombre']}' con largo {el['largo']:.2f}m "
                f"es más grande que el espacio disponible de {largo_max_terreno:.2f}m."
            )

    # Si no hay elementos, retornar una estructura vacía pero válida.
    if not elementos:
        pisos = {
            i + 1: {"largo_acumulado": 0.0, "ambientes": [], "largos": [], "anchos": []}
            for i in range(min_floors)
        }
        return {
            "Pisos_Ideales": min_floors,
            "Largo_Contenedor": 0,
            "Promedio_Teorico": 0,
            "Detalle": pisos
        }

    # Inicialización del primer piso.
    pisos = {
        i + 1: {"largo_acumulado": 0.0, "ambientes": [], "largos": [], "anchos": []}
        for i in range(min_floors)
    }
    num_pisos = min_floors

    # Distribuir elementos usando la estrategia First-Fit
    for el in elementos:
        placed = False
        # Intentar colocar en un piso existente, desde el primero
        for i in range(1, num_pisos + 1):
            if pisos[i]['largo_acumulado'] + el['largo'] <= largo_max_terreno:
                pisos[i]['largo_acumulado'] += el['largo']
                pisos[i]['ambientes'].append(el['nombre'])
                pisos[i]['largos'].append(el['largo'])
                pisos[i]['anchos'].append(el['ancho'])
                placed = True
                break  # Elemento colocado, pasar al siguiente

        # Si no cabe en ningún piso existente, se crea uno nuevo para este elemento.
        if not placed:
            num_pisos += 1
            if num_pisos > 30: # Límite de seguridad
                return (
                    "Error: La distribución excede los 30 pisos. Verifique las dimensiones."
                )
            pisos[num_pisos] = {
                "largo_acumulado": el['largo'],
                "ambientes": [el['nombre']],
                "largos": [el['largo']],
                "anchos": [el['ancho']]
            }

    # Asegurar el número mínimo de pisos requerido.
    num_pisos_generados = len(pisos)
    if num_pisos_generados < min_floors:
        for i in range(num_pisos_generados + 1, min_floors + 1):
            pisos[i] = {"largo_acumulado": 0.0, "ambientes": [], "largos": [], "anchos": []}

    num_pisos = len(pisos)
    largo_piso_maximo = max(p['largo_acumulado'] for p in pisos.values()) if pisos else 0
    largo_total_elementos = sum(el['largo'] for el in elementos)

    return {
        "Pisos_Ideales": num_pisos,
        "Largo_Contenedor": round(largo_piso_maximo, 2),
        "Promedio_Teorico": round(largo_total_elementos / num_pisos, 2) if num_pisos > 0 else 0,
        "Detalle": pisos
    }