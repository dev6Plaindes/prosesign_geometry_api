import pandas as pd

from src.bim.adapters.google_sheets_adapter import procesar_y_extraer_sheets
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger

def stage_get_ambientes(ctx : PipelineContext):
    
    aforo = ctx.request.aforo
    logger.info("PROCESANDO AMBIENTES...")
    
    df_excel_ambientes = procesar_y_extraer_sheets(
        datos = aforo, 
        nombre_archivo_google="MARIATEGUI"
    )
    logger.info("AMBIENTES CARGADOS!")
    ctx.ambientes = df_excel_ambientes.to_dict(orient="records")