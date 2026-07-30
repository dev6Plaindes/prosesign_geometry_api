import json

def guardar_en_json(datos, nombre_archivo='prueba.json'):
    """
    Guarda un objeto (lista o dict) en un archivo JSON.
    """
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            # indent=4 hace que el archivo sea legible para humanos
            # ensure_ascii=False permite guardar caracteres especiales como tildes
            json.dump(datos, f, indent=4, ensure_ascii=False)
        print(f"Datos guardados exitosamente en {nombre_archivo}")
    except Exception as e:
        print(f"Ocurrió un error al guardar el archivo: {e}")