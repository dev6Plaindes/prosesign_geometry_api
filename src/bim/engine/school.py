
import pandas as pd
from bim.cuadrante_1 import cuadrante_1
from src.bim.engine.utils.get_region import clasificar_region_peru
from src.bim.schemas.schema_dto import ProjectUpdateDTO
from src.bim.repository import save_content_step, update_data_project, update_status_job_project
from src.motor.calculadora_sheets import procesar_y_extraer_sheets
import os
import re
import shutil

def format_vertices(vertices):
    return [[punto["x"], punto["y"]] for punto in vertices]

def adapter_aforo(aforo_api):
    
    return pd.DataFrame({
        "nivel": ["Inicial", "Primaria", "Secundaria"],
        "aforo_grado": [
            aforo_api["inicial"]["aforo_por_grado"], 
            aforo_api["primaria"]["aforo_por_grado"], 
            aforo_api["secundaria"]["aforo_por_grado"]
        ],
        "cantidad_aulas": [
            aforo_api["inicial"]["cantidad_aulas"], 
            aforo_api["primaria"]["cantidad_aulas"], 
            aforo_api["secundaria"]["cantidad_aulas"]
        ]
    })

def generate_bim(data, project_id):
    vertices_terreno = data["vertices"]
    vertices_terreno = format_vertices(vertices_terreno)
    aforo_api = data["aforo"]
    
    departamento = data["departamento"]
    provincia = data["provincia"]
    
    region = clasificar_region_peru(departamento=departamento, provincia=provincia)
    
    
    tipo_institucion = [item["grado"] for item in aforo_api]
    tipo_institucion = ", ".join(tipo_institucion)

    aforo_api = {item["grado"].lower(): item for item in aforo_api}
    
    df_aforo_api = adapter_aforo(aforo_api)

    # Procesar aforo y calcular
    df_excel_ambientes = procesar_y_extraer_sheets(
        datos = df_aforo_api.to_dict(orient="records"), 
        nombre_archivo_google="MARIATEGUI"
    )
    
    data_builded, ensamblaje, factory_capas, RESUMEN_AREAS = cuadrante_1(vertices_terreno, df_excel_ambientes)

    factory_capas.export_step_all_capas()
    path = factory_capas.path_folder
    
    for file in os.listdir(path):
        if file.lower().endswith((".step", ".stp")):
            file_path = os.path.join(path, file)

            # extraer nivel del nombre
            match = re.search(r"_(\d+)\.[a-zA-Z0-9]+$", file)
            nivel = match.group(1) if match else None

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content_step = f.read()

            save_content_step(
                id_project=project_id,
                content_step=content_step,
                nivel = nivel
            )
            
    if path and os.path.exists(path):
        shutil.rmtree(path)
    
    data_project : ProjectUpdateDTO = {
        "vertices" : data_builded,
        "resumen_ambientes" : RESUMEN_AREAS,
        "tipo_institucion": tipo_institucion,
        "aforo" : aforo_api,
        "region" : region
    }
    
    update_status_job_project(id=project_id,status="finished")
    update_data_project(project_id, data_project)