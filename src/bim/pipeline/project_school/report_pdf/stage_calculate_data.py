    
from src.bim.pipeline.project_school.report_pdf.schema import PipelineContextReport
from src.bim.report_pdf.school_report_pdf import analizar_pisos_pabellon, calcular_total_alumnos, transform_areas
from src.utils.logger import logger

def stage_calculate_data(ctx: PipelineContextReport):
    logger.info("CALCULANDO PISOS POR PABELLON, TOTAL ALUMNOS, Y AREAS M2")
    
    ctx.pisos_pabellon = analizar_pisos_pabellon(ctx.resumen_ambientes)
    ctx.total_alumnos = calcular_total_alumnos(ctx.aforo)
    ctx.resumen_ambientes_raw = transform_areas(ctx.resumen_ambientes)
    