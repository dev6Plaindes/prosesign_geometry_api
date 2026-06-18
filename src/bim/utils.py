from typing import List, Union

def div_logic(medidas: List[Union[int, float, str]], medida_total: float) -> List[float]:
    suma_fijos = sum(m for m in medidas if isinstance(m, (int, float)))
    if suma_fijos > medida_total:
        return []

    cantidad_auto = medidas.count("auto")
    valor_auto = (medida_total - suma_fijos) / cantidad_auto if cantidad_auto > 0 else 0

    return [valor_auto if m == "auto" else m for m in medidas]


