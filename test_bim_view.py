import os
import pandas as pd
from src.bim.report_pdf.school_report_pdf import DataProject, SchoolReportePDF
from bim.cuadrante_1 import cuadrante_1
import cadquery as cq
import streamlit as st

vertices_terreno = [
    [272095.00, 8692195.00],
    [272075.00, 8692215.00],
    [272080.00, 8692250.00],
    [272110.00, 8692275.00],
    [272150.00, 8692265.00],
    [272165.00, 8692235.00],
    [272155.00, 8692205.00],
    [272125.00, 8692185.00],
]

df_excel = pd.read_csv("./data_ambiente.csv")
data_builded, ensamblaje, factory_capas = cuadrante_1(vertices_terreno, df_excel)

# # 1. Convertimos el ensamblaje en un solo sólido combinado
# solido_combinado = ensamblaje.toCompound()

# # 2. Lo metemos dentro de un Workplane SIMPLEMENTE para poder exportarlo
# #    Ya NO usamos .section() ni .projectTo2D()
# plano_2d = cq.Workplane("XY").add(solido_combinado)

factory_capas.export_step_all_capas()

path = factory_capas.path_folder

# print(factory_capas.path_folder)

data_project : DataProject = {
    "name_project" : "Nuevo Proyecto",
    "niveles" : ["Primaria", "Secundaria"]
}

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
            "width": 800,
            "height": 800,
            "showAxes": False,
            "projectionDir": (0, 0, 1),
            "strokeWidth": 0.05,
            "strokeColor": (0, 0, 0)
        }
    )
    print(f"-> ¡Éxito! SVG recreado desde STEP: {nombre_salida}")

def procesar_archivos_step_a_svg(folder_path):
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

# Ejecución usando el path_folder de tu factoría
path_a_procesar = factory_capas.path_folder
procesar_archivos_step_a_svg(path_a_procesar)


import streamlit.components.v1 as components

archivos = os.listdir(path_a_procesar)

for archivo in archivos:
    if archivo.lower().endswith(".svg"):
        ruta_svg = os.path.join(path_a_procesar, archivo)

        st.subheader(archivo)

        with open(ruta_svg, "r", encoding="utf-8") as f:
            svg = f.read()

        components.html(
            svg,
            height=800,
            scrolling=True
        )

# pdf = SchoolReportePDF(orientation="P", unit="mm", format="A4", data_project=data_project)

# # pdf.write("Nuevo reporte")
# pdf.output("reporte_fpdf2.pdf")
