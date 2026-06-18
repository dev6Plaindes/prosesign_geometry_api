from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.bim.repository import update_data_project, update_status_job_project
from src.bim.schemas.schema_dto import ProjectUpdateDTO
from src.utils.logger import logger

def stage_update_data_project(ctx : PipelineContext):
    
    tipo_institucion = [item["grado"] for item in ctx.request.aforo]
    tipo_institucion = ", ".join(tipo_institucion)
    
    data_project : ProjectUpdateDTO = {
        "aforo": ctx.request.aforo,
        "region": ctx.region,
        "resumen_ambientes" : ctx.resumen_ambientes,
        "tipo_institucion" : tipo_institucion,
        "vertices" : ctx.vertices_plano
    }
    logger.info(f"ACTUALIZANDO DATOS GENERADOS AL PROYECTO ID: {ctx.id_project}, VERSION ID:{ctx.id_version_project}")
    
    update_status_job_project(id=ctx.id_version_project, status="finished")
    update_data_project(ctx.id_version_project, data_project)