
import shutil

from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
import os, re

from src.bim.repository import save_content_step
from src.utils.logger import logger

def stage_convert_plane_and_save(ctx : PipelineContext):
    
    logger.info("CONVIRTIENDO PLANO A FORMATO STEP")
    factory_capas = ctx.factory_capas
    factory_capas.export_step_all_capas()
    path = factory_capas.path_folder
    
    logger.info(f"GUARDANDOS FORMATOS STEP ID VERSION PROJECT: {ctx.id_version_project}")
    for file in os.listdir(path):
        if file.lower().endswith((".step", ".stp")):
            file_path = os.path.join(path, file)

            # extraer nivel del nombre
            match = re.search(r"_(\d+)\.[a-zA-Z0-9]+$", file)
            nivel = match.group(1) if match else None

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content_step = f.read()

            # Generar SVG desde STEP y cachearlo en DB
            content_svg = None
            try:
                svg_path = file_path.replace(".step", ".svg").replace(".stp", ".svg")
                from src.bim.convert.stepToSVG import exportar_svg_desde_step
                exportar_svg_desde_step(file_path, svg_path)
                if os.path.exists(svg_path):
                    with open(svg_path, "r", encoding="utf-8") as f:
                        content_svg = f.read()
                    os.remove(svg_path)
                    logger.info(f"SVG generado y cacheado para nivel {nivel}")
            except Exception as e:
                logger.warning(f"No se pudo generar SVG para nivel {nivel}: {e}")

            save_content_step(
                id_project=ctx.id_version_project,
                content_step=content_step,
                nivel = nivel,
                content_svg = content_svg
            )
            
    if path and os.path.exists(path):
        shutil.rmtree(path)
    
    