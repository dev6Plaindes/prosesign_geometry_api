"""
    Pipeline que genera el proyecto
"""
from src.bim.pipeline.project_school.create.stage_build_plane import stage_build_plane
from src.bim.pipeline.project_school.create.stage_classifer_region import stage_classifier_region
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.bim.pipeline.project_school.create.stage_convert_plane_and_save import stage_convert_plane_and_save
from src.bim.pipeline.project_school.create.stage_get_ambientes import stage_get_ambientes
from src.bim.pipeline.project_school.create.stage_update_data_project import stage_update_data_project
from src.bim.schemas.project_schema import ProjectRequest

def generate_project_school_pipeline(
    request_data : ProjectRequest,
    id_parent_project : int,
    id_version_project : int
    ):
    
    ctx_data = PipelineContext(request=request_data, id_project=id_parent_project, id_version_project=id_version_project)
    
    # Clasificar y obtener region
    stage_classifier_region(ctx_data)
    
    # Obtener medidas y lista de ambientes
    stage_get_ambientes(ctx_data)

    # Construir plano de colegio
    stage_build_plane(ctx_data)
    
    # Convertir Plano a step y Guardar en la version del proyecto
    stage_convert_plane_and_save(ctx_data)
    
    # Actualizar campos en la bd para el proyecto
    stage_update_data_project(ctx_data)
    
    
    
    