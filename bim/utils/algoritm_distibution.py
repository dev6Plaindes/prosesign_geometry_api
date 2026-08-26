import numpy as np
import math
from bim.utils.algoritm_packing_sequential_first_fit import sequential_first_fit_packing

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
                'Largo_Total_Piso': contenido['largo_acumulado']
            })

    return filas

# [DOCUMENTACIÓN] Se agregó min_floors para forzar la distribución según la Tarea 5&6.
def auto_distribution_ambientes_y(data_ambientes, largo_cuadrante, min_floors=1):
 
    # MEDIDAS
    largo_escalera = 2.4
    largo_banios = 4

    espacio_escalera_banio = largo_escalera + largo_banios

    largo_restante = largo_cuadrante - espacio_escalera_banio

    print(f"LARGO RESTANTE={largo_restante}")
    # ---------------- FILTRADO ----------------
    
    ambientes_filtrados = []

    for row in data_ambientes:

        nombre = row["Ambientes"]

        if "Escalera" in nombre:
            continue
        
        # [DOCUMENTACIÓN] Se utiliza un casteo seguro para evitar caídas si la cantidad viene con decimales o cadenas inválidas (ej. #DIV/0!)
        try:
            cantidad = int(float(str(row["Cantidad"]).strip()))
        except (ValueError, TypeError):
            cantidad = 0

        for _ in range(cantidad):

            ambientes_filtrados.append({
                "Ambientes": row["Ambientes"],
                "Largo": row["Largo"],
                "Ancho": row["Ancho"]
            })

    print("AMBIENTES FILTRADOS", ambientes_filtrados)
    # ------------------------------------------

    sum_largo_ambientes_prim = sum(
        row["Largo"] for row in ambientes_filtrados
    )

    # --- CÁLCULO DE PISOS ---

    if sum_largo_ambientes_prim <= largo_restante or not ambientes_filtrados: # Manejar el caso de lista vacía
        cantidad_pisos_prim = 1
    else:
        cantidad_pisos_prim = max(
            1,
            int(np.ceil(sum_largo_ambientes_prim / largo_restante))
        )

    # -----------------------

    solucion = sequential_first_fit_packing(
        ambientes_filtrados,
        largo_max_terreno=largo_restante,
        min_floors=min_floors
    )

    if isinstance(solucion, str):
        return solucion

    df_final = solucion_a_lista(solucion["Detalle"])

    largo_contenedor_sol = solucion["Largo_Contenedor"]

    # ---------------------------------------------------------
    # AGRUPACIÓN POR PISO
    # ---------------------------------------------------------

    pisos_map = {}

    for row in df_final:

        piso = row["Piso"]

        if piso not in pisos_map:
            pisos_map[piso] = []

        pisos_map[piso].append(row)

    # ---------------------------------------------------------
    # CÁLCULO DE LARGO TOTAL POR PISO (SIN REDISTRIBUCIÓN)
    # ---------------------------------------------------------

    for piso, ambientes_piso in pisos_map.items():
        # Se calcula el largo total real del piso como la suma de los largos individuales.
        largo_total_piso = sum(row["Largo_Individual"] for row in ambientes_piso)
        # Se asigna este largo total a cada ambiente del piso, sin modificar sus largos individuales.
        for row in ambientes_piso:
            row["Largo_Total_Piso"] = largo_total_piso

    # ---------------------------------------------------------
    # REDONDEO FINAL
    # ---------------------------------------------------------

    for row in df_final:

        row["Largo_Individual"] = round(
            row["Largo_Individual"],
            2
        )

        # El largo total del piso ya se calculó y asignó, aquí solo lo redondeamos.
        row["Largo_Total_Piso"] = round(row["Largo_Total_Piso"], 2)

        row["ID_Piso"] = f'PISO_{row["Piso"]}'

    return df_final

def encontrar_largo_equilibrado(largo_total, min_largo, max_largo, grosor_columna):
    """
    Encuentra la medida individual equilibrada para una estructura.
    Asume que la estructura empieza y termina con una columna (N + 1 columnas).
    """
    # 1. Calcular el rango de N (número de ambientes/paneles) posibles
    # Despejando N de la fórmula: N = (LargoTotal - GrosorColumna) / (LargoIndividual + GrosorColumna)

    # Para el largo máximo, obtendremos el número MÍNIMO de paneles
    n_min = (largo_total - grosor_columna) / (max_largo + grosor_columna)
    # Para el largo mínimo, obtendremos el número MÁXIMO de paneles
    n_max = (largo_total - grosor_columna) / (min_largo + grosor_columna)

    # Redondeamos al entero más cercano dentro del rango viable
    n_paneles_ideal = round((n_min + n_max) / 2)

    # Forzar a que esté dentro de los límites enteros posibles
    n_paneles_ideal = max(math.ceil(n_min), min(math.floor(n_max), n_paneles_ideal))

    # Si no es posible dividir el espacio en este rango
    if n_paneles_ideal <= 0:
        raise ValueError("No es posible equilibrar las medidas con el rango y grosor de columna proporcionados.")

    # 2. Calcular el largo individual exacto despejando con el N ideal
    espacio_disponible_paneles = largo_total - ((n_paneles_ideal + 1) * grosor_columna)
    largo_individual_equilibrado = espacio_disponible_paneles / n_paneles_ideal

    return {
        "numero_paneles": n_paneles_ideal,
        "numero_columnas": n_paneles_ideal + 1,
        "largo_individual_exacto": round(largo_individual_equilibrado, 3),
        "largo_total_verificado": (n_paneles_ideal * largo_individual_equilibrado) + ((n_paneles_ideal + 1) * grosor_columna)
    }

def calcular_posiciones_columnas(cantidad_columnas, ancho_col, espacios_m):
    positions_columns = []
    cursor_x_col = 0.0  # El punto de partida de la primera columna es 0

    for i in range(cantidad_columnas):
        # 1. Calcular dónde inicia y termina la columna actual
        pos_x_init = cursor_x_col
        pos_x_end = pos_x_init + ancho_col

        # 2. Guardar el intervalo ocupado por la columna
        positions_columns.append((round(pos_x_init, 3), round(pos_x_end, 3)))

        # 3. Mover el cursor al inicio de la SIGUIENTE columna
        # El cursor avanza el ancho del panel (espacios_m) más el ancho de la columna
        cursor_x_col = pos_x_end + espacios_m

    return positions_columns