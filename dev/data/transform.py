

def agrupar_ambientes_por_pabellon(data_dict_ambientes):
    """
    Clasifica los ambientes en una sola pasada según su pabellón correspondiente.
    
    Retorna un diccionario con las listas clasificadas:
        - "medio": Pabellón Medio
        - "primaria": Pabellón Izquierda
        - "secundaria": Pabellón Derecha
        - "inicial": Pabellón Inferior
        - "admin": Pabellón Superior
    """
    # Inicializamos los contenedores
    resultado = {
        "medio": [],
        "primaria": [],
        "secundaria": [],
        "inicial": [],
        "admin": []
    }
    
    # Mapeo directo para evitar bloques "if/elif" repetitivos
    mapeo_pabellones = {
        "Medio": "medio",
        "Izquierda": "primaria",
        "Derecha": "secundaria",
        "Inferior": "inicial",
        "Superior": "admin"
    }
    
    # Una sola pasada por toda la data (Ultra eficiente)
    for row in data_dict_ambientes:
        pabellon_raw = row.get("Pabellon")
        clave_destino = mapeo_pabellones.get(pabellon_raw)
        
        if clave_destino:
            resultado[clave_destino].append(row)
            
    return resultado