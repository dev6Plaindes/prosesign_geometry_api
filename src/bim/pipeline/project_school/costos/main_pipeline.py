import json

from httpx import request
from pydantic import BaseModel
from src.bim.adapters.google_sheets_infra import procesar_y_extraer_sheets_costos_infra
from src.bim.pipeline.project_school.costos.schema import PipelineContextCostos
from src.bim.repository import create_data_calculo_costos_project, update_data_calculo_costos_project
from src.bim.schemas.schema_dto import ProjectDataForCostos
from src.utils.logger import logger
from src.bim.schemas.schema_request import CostosRequest

# calcula los costos de infraestructura del proyecto
def calculate_costos_pipeline(data_project : ProjectDataForCostos, data_req : CostosRequest):
    logger.info(f"INICIANDO PIPELINE DE COSTOS DE PROYECTO ID:{data_project.id}")
        
    ctx = PipelineContextCostos(data_req=data_req, data_project=data_project)
    
    logger.info(f"REGION DEL PROYECTO: {data_project.region}")
    
    procesar_y_extraer_sheets_costos_infra(ctx)
    
    data_calculo_costos = json.dumps(ctx.data_calculo_costos)
    create_data_calculo_costos_project(id=ctx.data_project.id, data_calculo_costos=data_calculo_costos)

    return data_calculo_costos
        