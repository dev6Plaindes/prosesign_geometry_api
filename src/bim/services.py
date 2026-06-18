import os
from fastapi import HTTPException, status
from src.motor.calculadora_sheets import procesar_y_extraer_sheets, procesar_y_extraer_sheets_costos
from src.bim.engine.utils.get_region import clasificar_region_peru
from src.bim.report_pdf.school_report_pdf import SchoolReportePDF, analizar_pisos_pabellon, calcular_total_alumnos, limpiar_archivos, transform_areas
from src.bim.convert.stepToSVG import procesar_archivos_step_a_svg
from src.bim.schemas.schema_dto import NivelesStepDTO
from bim.upload_aws_file import subir_archivo_a_s3
from src.bim.schemas.schema_response import ResponseGenerateProject, ResponseGetJob
from src.bim.engine.school import adapter_aforo, generate_bim
from src.bim.repository import get_content_step, get_project_by_id, insert_new_project_school, update_status_job_project, update_url_pdf_project
from rq import Queue
from redis_conn import redis_conn
from rq.job import Job
from rq.exceptions import NoSuchJobError
from secrets import token_hex
import json
from dotenv import load_dotenv

load_dotenv()

q = Queue("prodesign:bim:school", connection=redis_conn)

def service_generate_costos_infraestructue(id_project):
    project_data = get_project_by_id(id_project)

    aforo = project_data["aforo"]
    aforo_json = json.loads(aforo)
    df_aforo_api = adapter_aforo(aforo_json)
    datos = df_aforo_api.to_dict(orient="records")

    df_excel_infra = procesar_y_extraer_sheets_costos(
        datos = datos,
        nombre_archivo_google="COSTOS_INFRAESTRUCTURA"
    )

    # COSTOS_INFRAESTRUCTURA
    return {
        "calculo_infraestructura" : aforo
    }

def service_generate_project(data : dict) -> ResponseGenerateProject:
    id_v1_project_school = insert_new_project_school(data)
    
    job = q.enqueue(generate_bim, data, id_v1_project_school, job_timeout=150)

    update_status_job_project(
        id=id_v1_project_school, status="processing", job_id=job.id
    )

    return {"job_id": job.id, "project_id": id_v1_project_school}


def service_get_job(job_id : int) -> ResponseGetJob:
    try:
        # 1. Intentar buscar el trabajo en Redis
        job = Job.fetch(job_id, connection=redis_conn)

    except NoSuchJobError:
        # Si el ID no existe en Redis, devolvemos un 404 limpio
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El job con ID '{job_id}' no fue encontrado o ya expiró.",
        )
    except ConnectionError:
        # Si Redis se cayó o no conecta
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar al servicio de mensajería (Redis).",
        )
    except Exception as e:
        # Cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al consultar el job: {str(e)}",
        )

    # 2. Controlar el estado interno del Job por si falló la tarea de fondo
    job_status = job.get_status()

    # Si el trabajo falló, es buena práctica avisar al frontend por qué falló
    if job_status == "failed":
        return {
            "id": job.id,
            "status": job_status,
            "error": job.exc_info,  # Contiene el traceback del error en el worker
        }

    # 3. Respuesta exitosa (en progreso o finalizado)
    return {
        "id": job.id,
        "status": job_status,
        "result": job.result if job.is_finished else None,
    }

    
def service_generate_pdf_project(project_id : int):
    project_data = get_project_by_id(project_id)
    code_id = token_hex(6)
    new_path_files = f"temp_{code_id}"
    
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Definición de nombres de archivos locales
    AWS_PATH_FILES = os.getenv("AWS_PATH_FILES", "prodesign/test/")
    nombre_archivo_pdf = f"{AWS_PATH_FILES}plane_{project_id}.pdf"
    
    bucket_name = "plaindes"

    # 1. Obtener los steps desde la bd
    steps : list[NivelesStepDTO] = get_content_step(id_project=project_id)
    
    os.makedirs(new_path_files, exist_ok=True)
    
    # guardar cada STEP como archivo
    for step in steps:
        content_step = step["content_step"]  # o step.content_step si es objeto
        nivel = step.get("nivel", "unknown")

        file_name = f"MODELO_3D_CAPA_{nivel}.step"
        file_path = os.path.join(new_path_files, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_step)
    
    procesar_archivos_step_a_svg(new_path_files)
    
    data_raw = project_data["resumen_ambientes"]
    aforo = project_data["aforo"]
    total_alumnos = calcular_total_alumnos(json.loads(aforo))
    
    project_data["total_alumnos"] = total_alumnos
    
    
    # PISOS PABELLON
    # {
    #     "inicial": 2,
    #     "primaria": 1,
    #     "secundaria": 1,
    #     "admin": 1
    # }
    project_data["pisos_pabellon"] = analizar_pisos_pabellon(project_data["resumen_ambientes"])

    if isinstance(data_raw, str):
        data_raw = json.loads(data_raw)
        data_raw = transform_areas(data_raw)
    
    pdf = SchoolReportePDF(data_project=project_data, output_path=f"reporte_{code_id}.pdf")
    
    pdf.portada()
    pdf.info_project()
    pdf.add_svgs_from_folder(folder_path=new_path_files)
    pdf.add_area_summary_table(data_raw)
    archivo_binario  =  pdf.save_to_bin()
    
    url_resultado = subir_archivo_a_s3(
        archivo_binario=archivo_binario,
        nombre_archivo=nombre_archivo_pdf,
        bucket_name=bucket_name,
    )
    
    update_url_pdf_project(project_id, url_resultado)
    
    # limpiar_archivos(
    #     pdf_path=f"reporte_{code_id}.pdf",
    #     folder_path=new_path_files
    # )
    
    return {
        "status": "success",
        "url_pdf" : url_resultado, 
        "id_project": project_id
    }
    