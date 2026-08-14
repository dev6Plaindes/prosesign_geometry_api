import pandas as pd

def exportar_pabellones_a_csv(pabellones: dict, ruta_salida: str = "medidas_ambientes.csv") -> str:
    """
    Recibe el diccionario de PABELLONES y genera un archivo CSV usando Pandas
    con solo las medidas y dimensiones de los ambientes.
    """
    filas = []

    for nombre_pabellon, lista_ambientes in pabellones.items():
        if not lista_ambientes:
            continue
            
        for amb in lista_ambientes:
            cantidad = float(amb.get("Cantidad", 1.0))
            unitario = float(amb.get("Unitario", 0.0))
            area_total = float(amb.get("Metros cuadrados", cantidad * unitario))
            
            filas.append({
                "Pabellón": nombre_pabellon.capitalize(),
                "Ambiente": amb.get("Ambientes", "Sin Nombre"),
                "Cantidad": cantidad,
                "Ancho (m)": float(amb.get("Ancho", 0.0)),
                "Largo (m)": float(amb.get("Largo", 0.0)),
                "Área Unit. (m²)": unitario,
                "Área Total (m²)": area_total
            })

    # Crear el DataFrame de Pandas
    df = pd.DataFrame(filas)

    # Exportar a CSV (usando ';' como separador para Excel en español)
    df.to_csv(ruta_salida, index=False, sep=";", encoding="utf-8-sig")
    
    print(f"✅ Archivo CSV de medidas exportado con éxito en: {ruta_salida}")
    return ruta_salida