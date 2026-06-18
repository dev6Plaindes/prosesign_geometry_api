from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger
from src.bim.rules.region_classifier import region_classifier

def stage_classifier_region(ctx : PipelineContext):
    
    region = region_classifier(
        departamento=ctx.request.departamento, 
        provincia=ctx.request.provincia
    )
    
    ctx.region = region
    
    logger.info(f"PROYECTO EN REGION: {region}")
    