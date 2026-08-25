import os
from pathlib import Path
from fastapi import HTTPException, status
from matplotlib.font_manager import json_dump
from src.bim.pipeline.project_school.create.main_pipeline import generate_project_school_pipeline
from src.bim.schemas.project_schema import ProjectRequest
from src.bim.schemas.schema_dto import ProjectDataForReport
from src.bim.schemas.schema_response import ResponseGenerateProject, ResponseGetJob
from src.bim.repository import create_new_version_project, get_project_by_id, insert_new_project_school, update_status_job_project
from src.utils.logger import logger
from rq import Queue
from redis_conn import redis_conn
from rq.job import Job
from rq.exceptions import NoSuchJobError
from secrets import token_hex
import json
from dotenv import load_dotenv
from src.bim.pipeline.project_school.report_pdf.main_pipeline import report_pdf_pipeline
load_dotenv()

q = Queue("prodesign:bim:school", connection=redis_conn)
q_pdf = Queue("prodesign:bim:pdf", connection=redis_conn)

def service_generate_costos_infraestructue(id_project, data_form_costos):
    project_data = get_project_by_id(id_project)

    return {
        "calculo_infraestructura" : ""
    }

def service_generate_project(request_data : ProjectRequest) -> ResponseGenerateProject:
    
    id_new_project = insert_new_project_school(request_data)

    id_new_v_project = create_new_version_project(request_data, id_new_project)

    # generate_project_school_pipeline(
    #     request_data=data_project,
    #     id_parent_project= id_new_project,
    #     id_version_project=id_new_v_project
    # )
    
    job = q.enqueue(
        generate_project_school_pipeline, 
        request_data, 
        id_new_project,
        id_new_v_project,
        job_timeout=300
    )

    update_status_job_project(
        id=id_new_v_project, status="processing", job_id=job.id
    )

    return {"job_id": job.id, "project_id": id_new_v_project}

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
        # [DOCUMENTACIÓN] Se extrae únicamente la última línea del traceback para mostrar un mensaje claro al usuario en el frontend
        error_msg = "Error desconocido al procesar el plano"
        if job.exc_info:
            lines = str(job.exc_info).strip().splitlines()
            if lines:
                error_msg = lines[-1]
        return {
            "id": job.id,
            "status": job_status,
            "error": error_msg,
        }

    # 3. Respuesta exitosa (en progreso o finalizado)
    return {
        "id": job.id,
        "status": job_status,
        "result": job.result if job.is_finished else None,
    }

def run_pdf_pipeline(project_id: int):
    data_project = get_project_by_id(project_id)
    if not data_project:
        raise ValueError(f"Project with id {project_id} not found")

    aforo_raw = data_project.get("aforo")
    if isinstance(aforo_raw, str):
        try:
            data_project["aforo"] = json.loads(aforo_raw)
        except Exception:
            data_project["aforo"] = []
    elif not isinstance(aforo_raw, list):
        data_project["aforo"] = []

    resumen_raw = data_project.get("resumen_ambientes")
    if isinstance(resumen_raw, str):
        try:
            data_project["resumen_ambientes"] = json.loads(resumen_raw)
        except Exception:
            data_project["resumen_ambientes"] = []
    elif not isinstance(resumen_raw, list):
        data_project["resumen_ambientes"] = []

    data_for_report = ProjectDataForReport(**data_project)
    url_resultado = report_pdf_pipeline(data_for_report)

    if url_resultado:
        return {"status": "success", "url_pdf": url_resultado, "id_project": project_id}
    return {"status": "failed", "url_pdf": None, "id_project": project_id}


def service_generate_pdf_project_async(project_id: int):
    project_data = get_project_by_id(project_id)
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    try:
        job = q_pdf.enqueue(
            run_pdf_pipeline,
            project_id,
            job_timeout=300,
        )
        return {"job_id": job.id, "project_id": project_id}
    except Exception as e:
        logger.warning(f"No se pudo encolar PDF async, fallback a sync: {e}")
        return service_generate_pdf_project(project_id)


def service_generate_pdf_project(project_id : int):
    data_project = get_project_by_id(project_id)

    path = Path("data_project_payload.json")
    
    path.write_text(
        json.dumps(data_project, default=str, indent=4),
        encoding="utf-8"
    )
    
    # [DOCUMENTACIÓN] Se robusteció la conversión de aforo y resumen_ambientes para evitar crasheos si ya son listas/diccionarios o si son nulos en la base de datos
    aforo_raw = data_project.get("aforo")
    if isinstance(aforo_raw, str):
        try:
            data_project["aforo"] = json.loads(aforo_raw)
        except Exception:
            data_project["aforo"] = []
    elif not isinstance(aforo_raw, list):
        data_project["aforo"] = []

    resumen_raw = data_project.get("resumen_ambientes")
    if isinstance(resumen_raw, str):
        try:
            data_project["resumen_ambientes"] = json.loads(resumen_raw)
        except Exception:
            data_project["resumen_ambientes"] = []
    elif not isinstance(resumen_raw, list):
        data_project["resumen_ambientes"] = []


    data_for_report = ProjectDataForReport(**data_project)

    url_resultado = report_pdf_pipeline(data_for_report)
    
    if url_resultado :
        return {
                "status": "success",
                "url_pdf" : url_resultado, 
                "id_project": project_id
            }

    return {
        "status": "failed",
        "url_pdf" : None, 
        "id_project": project_id
    }
    