from src.bim.pipeline.project_school.report_pdf.schema import PipelineContextReport
from src.bim.pipeline.project_school.report_pdf.stage_build_and_upload_report_pdf import stage_build_and_upload_report_pdf
from src.bim.pipeline.project_school.report_pdf.stage_calculate_data import stage_calculate_data
from src.bim.pipeline.project_school.report_pdf.stage_get_step_from_db_to_svg import (
    stage_get_step_from_db_to_svg,
)
from src.bim.schemas.schema_dto import ProjectDataForReport
from src.utils.logger import logger

def report_pdf_pipeline(data: ProjectDataForReport) -> str:

    ctx: PipelineContextReport = PipelineContextReport(**data.model_dump())
    logger.info(f"INICIANDO PIPELINE REPORTE PDF | VERSION ID PROJECT:{ctx.id}")

    # Obtener steps (plano 3D de la version del proyecto) desde la bd y convertir a svg
    stage_get_step_from_db_to_svg(ctx)

    # calcula medidas como pisos, y areas
    stage_calculate_data(ctx)
    stage_build_and_upload_report_pdf(ctx)

    if(ctx.url_pdf):
        logger.info(f"PDF GENERADO CON EXITO")
        
    return ctx.url_pdf