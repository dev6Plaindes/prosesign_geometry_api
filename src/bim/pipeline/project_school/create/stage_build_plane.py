from bim.cuadrante_1 import cuadrante_1
from bim.utils.step_to_json import ensamblaje_to_array
from bim.v2.cuadrante_1_v2 import cuadrante_1_v2
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger

# [DOCUMENTACIÓN] Se filtra la lista de vértices eliminando los excluidos, y se pasan vertices_rectangle y angle a cuadrante_1.
def stage_build_plane(ctx : PipelineContext):
    logger.info("CONSTRUYENDO PLANO COLEGIO...")
    
    vertices = ctx.request.vertices
    vertices = [[punto["x"], punto["y"]] for punto in vertices]
    
    # [DOCUMENTACIÓN] Filtrar los vértices excluidos usando comparación con tolerancia
    excluded = ctx.request.excluded_vertices or []
    available_vertices = []
    for x, y in vertices:
        is_excluded = any(
            abs(vx - x) < 0.001 and abs(vy - y) < 0.001
            for vx, vy in excluded
        )
        if not is_excluded:
            available_vertices.append([x, y])
            
    # Caída segura: si quedan menos de 3 puntos no excluidos, usamos el terreno completo
    if len(available_vertices) < 3:
        available_vertices = vertices
    
    # data_builded, _, factory_capas, RESUMEN_AREAS = cuadrante_1(
    #     available_vertices,
    #     ctx.ambientes,
    #     number_floors=ctx.request.number_floors,
    #     vertices_rectangle=ctx.request.vertices_rectangle,
    #     angle=ctx.request.angle
    # )
    
    vertices_cuadrante = ctx.request.vertices_rectangle
    vertices_terreno = ctx.request.vertices
    
    print(vertices_cuadrante)
    print(vertices_terreno)
    
    
    # Genera plano y guarda en s3 tambien
    ensamblaje, factory_capas, RESUMEN_AREAS = cuadrante_1_v2(
        vertices_terreno,
        vertices_cuadrante,
        ctx.ambientes,
        ctx.id_project
    )
    
    datos_ensamblaje = ensamblaje_to_array(ensamblaje)
    
    ctx.resumen_ambientes = RESUMEN_AREAS
    ctx.factory_capas = factory_capas
    ctx.vertices_plano = datos_ensamblaje
    
    logger.info("PLANO DE COLEGIO CONSTRUIDO")
    