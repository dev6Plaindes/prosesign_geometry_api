import io
import tempfile

import pandas as pd
from bim.cuadrante_1 import cuadrante_1
from src.bim.repository import update_status_job_project, update_vertices_project
from src.motor.calculadora_sheets import procesar_y_extraer_sheets
from bim.upload_aws_file import obtener_archivo_en_binario, subir_archivo_a_s3

def format_vertices(vertices):
    return [[punto["x"], punto["y"]] for punto in vertices]

def generate_bim(data, project_id):
    vertices_terreno = data["vertices"]
    vertices_terreno = format_vertices(vertices_terreno)
    aforo_api = data["aforo"]

    aforo_api = {item["grado"].lower(): item for item in aforo_api}
    
    df_aforo_api = pd.DataFrame({
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

    # Procesar aforo y calcular
    df_excel = procesar_y_extraer_sheets(df_aforo_api.to_dict(orient="records"), "MARIATEGUI")
    data_builded, ensamblaje = cuadrante_1(vertices_terreno, df_excel, project_id)


    bucket_destino = "plaindes"
    ruta_en_s3 = f"plane_{project_id}.step"
    ensamblaje.save(ruta_en_s3)
    
    file_bytes = obtener_archivo_en_binario(ruta_en_s3)
    archivo_binario_stream = io.BytesIO(file_bytes)

    url_resultado = subir_archivo_a_s3(
        archivo_binario=archivo_binario_stream, 
        nombre_archivo=ruta_en_s3,
        bucket_name=bucket_destino
    )
    
    print(f"Archivo subido a S3 con URL: {url_resultado}")
    update_status_job_project(id=project_id,status="finished")
    update_vertices_project(project_id, data_builded)