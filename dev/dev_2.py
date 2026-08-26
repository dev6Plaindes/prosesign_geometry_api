import cadquery as cq
from ocp_vscode import show
from dev.data_test import data_test, ambientes_test
from bim.v2.cuadrante_1_v2 import cuadrante_1_v2
from src.bim.pipeline.project_school.create.stage_get_ambientes import stage_get_ambientes, stage_get_ambientes_test
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.bim.schemas.project_schema import ProjectRequest

# 1. Obtener datos de prueba y configurar contexto
request_data = ProjectRequest(**data_test)
ctx = PipelineContext(
    request=request_data, 
    id_project=1040, 
    id_version_project=1040
)
ctx.ambientes = ambientes_test

# 2. Procesar y filtrar ambientes
stage_get_ambientes(ctx)

# 3. Llamar a la función principal que encapsula toda la lógica de construcción
vertices_cuadrante = ctx.request.vertices_rectangle
vertices_terreno = ctx.request.vertices

mi_modelo, factory_capas, resumen_areas = cuadrante_1_v2(
    vertices_terreno=vertices_terreno,
    vertices_cuadrante=vertices_cuadrante,
    ambientes=ctx.ambientes,
    id_project=ctx.id_project
)

# 4. Guardar el modelo 3D resultante en un archivo GLB
mi_modelo.save("pabellon.glb")
mi_modelo.save("plano_3d.step")
# seccion_2d = mi_modelo.faces(">Z").workplane()  # Selecciona vista/cara
# cq.exporters.export(seccion_2d, "plano_2d.dxf")

# 5. Visualizar el modelo en el visor OCP de VSCode
show(
    mi_modelo,
    alphas=[0.6]
)
