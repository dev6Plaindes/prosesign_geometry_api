# [DOCUMENTACIÓN] Se modificó stage_classifier_region para importar get_zona_provincia y CONFIG_PROYECTO, y configurar dinámicamente zona_climatica en z1 o z3 de acuerdo a la provincia.
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger
from src.bim.rules.region_classifier import region_classifier
from bim.get_zona_prov import get_zona_provincia
from bim.config_proyect import CONFIG_PROYECTO

def stage_classifier_region(ctx : PipelineContext):
    
    region = region_classifier(
        departamento=ctx.request.departamento, 
        provincia=ctx.request.provincia
    )
    
    ctx.region = region
    
    logger.info(f"PROYECTO EN REGION: {region}")

    # Configuración dinámica de la zona climática basada en la provincia
    zona, techo = get_zona_provincia(ctx.request.provincia)
    if zona in ["zona_1", "zona_2"]:
        CONFIG_PROYECTO["zona_climatica"] = "z1"
    else:
        CONFIG_PROYECTO["zona_climatica"] = "z3"
    
    logger.info(f"[DOCUMENTACIÓN] Zona climática configurada: {CONFIG_PROYECTO['zona_climatica']} (Techo: {techo})")

    