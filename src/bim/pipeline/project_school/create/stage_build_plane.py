from bim.cuadrante_1 import cuadrante_1
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger

def stage_build_plane(ctx : PipelineContext):
    logger.info("CONSTRUYENDO PLANO COLEGIO...")
    
    vertices = ctx.request.vertices
    vertices = [[punto["x"], punto["y"]] for punto in vertices]
    terreno_maximo_cuadrante= ctx.request.terreno_maximo_cuadrante
    
    data_builded, _, factory_capas, RESUMEN_AREAS = cuadrante_1(
        vertices,
        ctx.ambientes,
        terreno_maximo_cuadrante
    )
    
    ctx.resumen_ambientes = RESUMEN_AREAS
    ctx.factory_capas = factory_capas
    ctx.vertices_plano = data_builded
    
    logger.info("PLANO DE COLEGIO CONSTRUIDO")
    