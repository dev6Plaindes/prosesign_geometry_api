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

    if not steps:
        logger.warning(f"No se encontraron steps para el proyecto {ctx.id}. El PDF se generará sin planos.")
        os.makedirs(path_temp_steps, exist_ok=True)
        return

    os.makedirs(path_temp_steps, exist_ok=True)

    has_cadquery_conversion = False

    for step in steps:
        content_step = step["content_step"]
        content_svg = step.get("content_svg")
        nivel = step.get("nivel", "unknown")

        svg_file_name = f"MODELO_3D_CAPA_{nivel}.svg"
        svg_file_path = os.path.join(path_temp_steps, svg_file_name)

        if content_svg:
            # Usar SVG cacheado desde DB
            with open(svg_file_path, "w", encoding="utf-8") as f:
                f.write(content_svg)
            logger.info(f"SVG cacheado usado para nivel {nivel}")
        else:
            # Fallback: escribir STEP y convertir con CadQuery
            step_file_name = f"MODELO_3D_CAPA_{nivel}.step"
            step_file_path = os.path.join(path_temp_steps, step_file_name)

            with open(step_file_path, "w", encoding="utf-8") as f:
                f.write(content_step)

            has_cadquery_conversion = True

    if has_cadquery_conversion:
        logger.info(f"CONVIRTIENDO STEPS A SVG (fallback CadQuery) en: /{path_temp_steps}")
        procesar_archivos_step_a_svg(path_temp_steps)
    else:
        logger.info(f"Todos los SVGs obtenidos desde caché DB, se omite CadQuery")
    