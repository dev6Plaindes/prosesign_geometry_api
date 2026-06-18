import os
from secrets import token_hex

from src.bim.convert.stepToSVG import procesar_archivos_step_a_svg
from src.bim.pipeline.project_school.report_pdf.schema import PipelineContextReport
from src.bim.repository import get_content_step
from src.bim.schemas.schema_dto import NivelesStepDTO
from src.utils.logger import logger

def stage_get_step_from_db_to_svg(ctx : PipelineContextReport):
    logger.info(f"OBTENIENDO FORMATOS STEPS DEL PROYECTO")
    code_id = token_hex(6)
    path_temp_steps = f"temp_{code_id}"
    ctx.path_temp_steps = path_temp_steps

    steps : list[NivelesStepDTO] = get_content_step(id_project=ctx.id)
    
    os.makedirs(path_temp_steps, exist_ok=True)
    
    for step in steps:
        content_step = step["content_step"]  # o step.content_step si es objeto
        nivel = step.get("nivel", "unknown")

        file_name = f"MODELO_3D_CAPA_{nivel}.step"
        file_path = os.path.join(path_temp_steps, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_step)
            
    logger.info(f"CONVIERTIENDO STEPS A SVG y GUARDANDO EN: /{path_temp_steps}")
    procesar_archivos_step_a_svg(path_temp_steps)
    