import pandas as pd
import numpy as np

def auto_distribution_ambientes_y(df_ambientes, largo_cuadrante, pabellon="Izquierda"):
    # MEDIDAS
    largo_escalera = (2.4 + 0.25) * 2  # Escaleras a los extremos
    largo_banios = 4 

    espacio_escalera_banio = largo_escalera + largo_banios

    # Largo restante inicial (asumiendo que hay escaleras)
    largo_restante = largo_cuadrante - espacio_escalera_banio

    df = df_ambientes

    df_ambientes = df[~df["Ambientes"].str.contains('SSHH', na=False)]
    df_ambientes = df_ambientes[~df_ambientes["Ambientes"].str.contains('Escalera', na=False)]

    df_pabellon = df_ambientes[df_ambientes['Pabellon'] == 'Izquierda']
    df_pabellon_exp = df_pabellon.loc[df_pabellon.index.repeat(df_pabellon["Cantidad"])].copy()
    df_pabellon_exp = df_pabellon_exp.reset_index(drop=True)
    df_pabellon_exp = df_pabellon_exp.drop(columns=['Pabellon', "Metros cuadrados", "Tipo"])

    # Suma de largos de los ambientes
    sum_largo_ambientes_prim = df_pabellon_exp["Largo"].sum()

    # --- CORRECCIÓN AQUÍ ---
    # Calculamos la cantidad de pisos. Si la suma es menor al espacio, es 1 piso.
    if sum_largo_ambientes_prim <= largo_restante:
        cantidad_pisos_prim = 1
    else:
        # Usamos math.ceil o una división que asegure al menos 1
        cantidad_pisos_prim = max(1, int(np.ceil(sum_largo_ambientes_prim / largo_restante)))

    # Si resulta ser 1 solo piso, recuperamos el espacio de la escalera (ya que no se necesita subir)
    if cantidad_pisos_prim == 1:
        largo_restante = largo_cuadrante - largo_banios # Se quita la escalera del descuento
    # -----------------------

    # Evitamos división por cero en aulas_por_piso
    cantidad_aulas = df_pabellon_exp.shape[0] 
    aulas_por_piso = int(cantidad_aulas // cantidad_pisos_prim) if cantidad_pisos_prim > 0 else cantidad_aulas

    solucion = encontrar_configuracion_ideal(df_pabellon_exp, largo_max_terreno=largo_restante)

    # Verificación de error en la función ideal
    if isinstance(solucion, str):
        return solucion

    df_final = solucion_a_dataframe(solucion["Detalle"])

    ambientes_por_piso = []
    largo_contenedor_sol = solucion["Largo_Contenedor"]

    for num_piso, datos_piso in df_final.groupby('Piso'):
        df_temp = datos_piso.copy()
        df_temp['ID_Piso'] = f"PISO_{num_piso}"
        ambientes_por_piso.append(df_temp)

    for df_piso in ambientes_por_piso:
        cantidad_ambientes = len(df_piso)
        largo_actual_piso = df_piso["Largo_Total_Piso"].iloc[0]

        if largo_actual_piso < largo_contenedor_sol:
            m_faltante = largo_contenedor_sol - largo_actual_piso
            m_aprox_unit = m_faltante / cantidad_ambientes

            for index in df_piso.index:
                df_piso.at[index, "Largo_Individual"] += m_aprox_unit

            df_piso["Largo_Total_Piso"] = largo_contenedor_sol

    df_final_procesado = pd.concat(ambientes_por_piso, ignore_index=True)
    return df_final_procesado


def encontrar_configuracion_ideal(df, largo_max_terreno=80.0):
    """
    Distribuye los ambientes del DataFrame fila por fila en pisos,
    respetando el largo máximo del terreno.
    """
    # 1. Extraer elementos directamente de las filas (Agregado 'ancho')
    elementos = []
    for _, row in df.iterrows():
        elementos.append({
            'nombre': row['Ambientes'],
            'largo': float(row['Largo']),
            'ancho': float(row['Ancho'])  # <--- Agregado
        })

    # 2. Ordenar de mayor a menor (Heurística LPT) para mejor encaje
    elementos = sorted(elementos, key=lambda x: x['largo'], reverse=True)
    largo_total = sum(el['largo'] for el in elementos)

    num_pisos = 1
    configuracion_valida = False
    resultado_final = {}
    largo_max_final = 0

    while not configuracion_valida:
        # Inicializar estructura de pisos (Agregado 'anchos')
        pisos = {i+1: {"largo_acumulado": 0.0, "ambientes": [], "largos": [], "anchos": []} for i in range(num_pisos)}

        # Distribuir en el piso que tenga más espacio libre actualmente
        for el in elementos:
            piso_mas_vacio = min(pisos, key=lambda p: pisos[p]['largo_acumulado'])
            pisos[piso_mas_vacio]['largo_acumulado'] += el['largo']
            # Se muestra nombre, largo y ancho en el detalle
            pisos[piso_mas_vacio]['ambientes'].append(f"{el['nombre']} ({el['largo']}m x {el['ancho']}m)")
            pisos[piso_mas_vacio]['largos'].append(el['largo'])
            pisos[piso_mas_vacio]['anchos'].append(el['ancho']) # <--- Agregado

        # Validar si el piso más largo de esta iteración cabe en el terreno
        largo_piso_maximo = max(p['largo_acumulado'] for p in pisos.values())

        if largo_piso_maximo <= largo_max_terreno:
            configuracion_valida = True
            resultado_final = pisos
            largo_max_final = largo_piso_maximo
        else:
            num_pisos += 1
            if num_pisos > 30: # Límite de seguridad
                return "Error: Los ambientes son demasiado largos para el terreno o exceden 30 pisos."

    return {
        "Pisos_Ideales": num_pisos,
        "Largo_Contenedor": round(largo_max_final, 2),
        "Promedio_Teorico": round(largo_total / num_pisos, 2),
        "Detalle": resultado_final
    }

def solucion_a_dataframe(solucion_dict):
    filas = []

    # Iteramos sobre cada piso (1, 2, 3...)
    for num_piso, contenido in solucion_dict.items():
        # Agregamos 'anchos' al zip para extraer las tres listas en paralelo
        for nombre, largo, ancho in zip(contenido['ambientes'], contenido['largos'], contenido['anchos']):
            filas.append({
                'Piso': num_piso,
                'Ambiente': nombre,
                'Largo_Individual': largo,
                'Ancho_Individual': ancho,  # <--- Nueva columna
                'Largo_Total_Piso': contenido['largo_acumulado']
            })

    # Creamos el DataFrame
    df_resultado = pd.DataFrame(filas)
    return df_resultado

