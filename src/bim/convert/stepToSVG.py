import os
import cadquery as cq

def exportar_svg_desde_step(path_step, nombre_salida):
    """
    Importa un archivo STEP y lo exporta inmediatamente como SVG.
    """
    # 1. Importar el archivo STEP
    solido = cq.importers.importStep(path_step)
    
    # 2. Convertirlo en un Workplane para poder exportar
    plano_2d = cq.Workplane("XY").add(solido)
    
    # 3. Exportar a SVG
    plano_2d.export(
        nombre_salida,
        opt={
            "width": 4000,
            "height": 2700,
            "showAxes": False,
            "projectionDir": (0, 0, 1),
            "strokeWidth": 0.05,
            "strokeColor": (0, 0, 0)
        }
    )
    print(f"-> ¡Éxito! SVG recreado desde STEP: {nombre_salida}")

def procesar_archivos_step_a_svg(folder_path : str):
    """
    Recorre todos los archivos .step en folder_path y genera
    su correspondiente versión .svg en la misma carpeta.
    """
    if not os.path.exists(folder_path):
        print(f"Error: La carpeta {folder_path} no existe.")
        return

    # Listamos todos los archivos en la carpeta
    archivos = os.listdir(folder_path)
    
    for archivo in archivos:
        # Solo procesar archivos que terminen en .step
        if archivo.lower().endswith(".step"):
            ruta_step = os.path.join(folder_path, archivo)
            
            # Definir el nombre del archivo de salida (cambiar .step por .svg)
            nombre_svg = os.path.splitext(archivo)[0] + ".svg"
            ruta_svg = os.path.join(folder_path, nombre_svg)
            
            print(f"Procesando: {archivo} -> {nombre_svg}")
            
            # Llamada a tu función de exportación
            try:
                exportar_svg_desde_step(ruta_step, ruta_svg)
            except Exception as e:
                print(f"Error al procesar {archivo}: {e}")