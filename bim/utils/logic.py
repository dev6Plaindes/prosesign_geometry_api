# =====================================================================
# LÓGICA DE DISTRIBUCIÓN
# =====================================================================
from typing import List, Union

from bim.utils.algoritm_distibution import auto_distribution_ambientes_y

def div_logic(medidas: List[Union[int, float, str]], medida_total: float) -> List[float]:
    suma_fijos = sum(m for m in medidas if isinstance(m, (int, float)))
    if suma_fijos > medida_total:
        return []

    cantidad_auto = medidas.count("auto")
    valor_auto = (medida_total - suma_fijos) / cantidad_auto if cantidad_auto > 0 else 0

    return [valor_auto if m == "auto" else m for m in medidas]

def acumulate_coords(medidas: list, x_init: float) -> list:
    """
    Toma un array de medidas y genera intervalos [inicio, fin]
    acumulando los valores secuencialmente a partir de x_init.
    """
    resultado = []
    puntero_x = x_init

    for medida in medidas:
        siguiente_x = puntero_x + medida
        # Redondeamos a 2 decimales para evitar problemas de coma flotante
        resultado.append([round(puntero_x, 2), round(siguiente_x, 2)])
        puntero_x = siguiente_x
    return resultado

def translate_norm(x, y, z):
    return x / 2, y / 2, z / 2


from itertools import groupby

def largos_for_piso(data, largo_total):
    
    pabellon_p = auto_distribution_ambientes_y(data, largo_total)

    resultado = [
        [round(item['Largo_Individual'],2) for item in grupo]
        for clave, grupo in groupby(pabellon_p, key=lambda x: x['Piso'])
    ]

    return resultado

from itertools import groupby

def largos_for_piso_and_ambiente(data, largo_total):
    # Genera la distribución automática de los ambientes
    pabellon_p = auto_distribution_ambientes_y(data, largo_total)

    # Mantenemos la estructura de lista de listas: [ [...], [...], [...] ]
    resultado = [
        [
            {
                "ambiente": item['Ambiente'], 
                "largo": round(item['Largo_Individual'], 2)
            } 
            for item in grupo
        ]
        for clave, grupo in groupby(pabellon_p, key=lambda x: x['Piso'])
    ]

    return resultado
