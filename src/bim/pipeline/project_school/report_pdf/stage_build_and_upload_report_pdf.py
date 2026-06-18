    

import os
from src.bim.adapters.upload_aws_file import subir_archivo_a_s3
from src.bim.pipeline.project_school.report_pdf.schema import PipelineContextReport
from src.bim.report_pdf.school_report_pdf import SchoolReportePDF, limpiar_archivos
from src.bim.repository import update_url_pdf_project
from src.utils.logger import logger

def stage_build_and_upload_report_pdf(ctx: PipelineContextReport):
    logger.info("GENERANDO PDF DEL PROYECTO")
    
    project_data = ctx.model_dump()
    pdf = SchoolReportePDF(data_project=project_data, output_path=f"reporte_{ctx.id}.pdf")
    pdf.portada()
    pdf.info_project()
    pdf.add_svgs_from_folder(folder_path=ctx.path_temp_steps)
    pdf.add_area_summary_table(ctx.resumen_ambientes_raw)
    archivo_binario  =  pdf.save_to_bin()
    
    AWS_PATH_FILES = os.getenv("AWS_PATH_FILES", "prodesign/test/")
    
    nombre_archivo_pdf = f"{AWS_PATH_FILES}plane_{ctx.id}.pdf"
    bucket_name = "plaindes"
    
    logger.info("GUARDANDO ARCHIVO EN S3")
    url_resultado = subir_archivo_a_s3(
        archivo_binario=archivo_binario,
        nombre_archivo=nombre_archivo_pdf,
        bucket_name=bucket_name,
    )
    logger.info(f"ARCHIVO GUARDADO EN S3: {url_resultado}")
    
    update_url_pdf_project(ctx.id, url_resultado)
    logger.info(f"GUARDANDO RUTA DEL PDF EN DB: {url_resultado}")
    ctx.url_pdf = url_resultado
    limpiar_archivos(
            pdf_path=f"reporte_{ctx.id}.pdf",
            folder_path=ctx.path_temp_steps
        )
    logger.info(f"LIMPIANDO ARCHIVOS TEMPORALES DE: {ctx.path_temp_steps}")
