    

import os
from src.bim.adapters.upload_aws_file import subir_archivo_a_s3
from src.bim.pipeline.project_school.report_pdf.schema import PipelineContextReport
from src.bim.report_pdf.school_report_pdf import SchoolReportePDF, limpiar_archivos
from src.bim.repository import update_url_pdf_project, update_content_pdf
from src.utils.logger import logger

def stage_build_and_upload_report_pdf(ctx: PipelineContextReport):
    logger.info("GENERANDO PDF DEL PROYECTO")
    
    project_data = ctx.model_dump()
    pdf_filename = f"reporte_{ctx.id}.pdf"
    pdf = SchoolReportePDF(data_project=project_data, output_path=pdf_filename)
    pdf.portada()
    pdf.info_project()
    pdf.add_aforo_table()
    pdf.add_terrain_measurements_table()
    pdf.add_svgs_from_folder(folder_path=ctx.path_temp_steps)
    pdf.add_area_summary_table(ctx.resumen_ambientes_raw)
    archivo_binario  =  pdf.save_to_bin()
    
    pdf_bytes = archivo_binario.getvalue()
    
    local_dir = "local_pdfs"
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, f"plane_{ctx.id}.pdf")
    with open(local_path, "wb") as f:
        f.write(pdf_bytes)
    
    try:
        update_content_pdf(ctx.id, pdf_bytes)
        logger.info(f"PDF guardado en DB para proyecto {ctx.id}")
    except Exception as e:
        logger.warning(f"No se pudo guardar PDF en DB (columna content_pdf puede no existir): {e}")
        
    # [DOCUMENTACIÓN] Se quitó el prefijo AWS_PATH_FILES del nombre del archivo enviado a subir_archivo_a_s3 para evitar duplicación de rutas, delegando la estructuración del prefijo al adaptador.
    nombre_archivo_pdf = f"plane_{ctx.id}.pdf"
    bucket_name = "plaindes"
    
    logger.info("GUARDANDO ARCHIVO EN S3")
    try:
        url_resultado = subir_archivo_a_s3(
            archivo_binario=archivo_binario,
            nombre_archivo=nombre_archivo_pdf,
            bucket_name=bucket_name,
        )
        logger.info(f"ARCHIVO GUARDADO EN S3: {url_resultado}")
    except Exception as s3_error:
        logger.error(f"Error al subir a S3: {s3_error}. Usando fallback DB.")
        base_url = os.getenv("BASE_URL_SERVER", "http://localhost:8001")
        url_resultado = f"{base_url}/api/v3/project/pdf-download/{ctx.id}"
    
    update_url_pdf_project(ctx.id, url_resultado)
    logger.info(f"RUTA DEL PDF GUARDADA EN DB: {url_resultado}")
    ctx.url_pdf = url_resultado

    try:
        if ctx.path_temp_steps and os.path.exists(ctx.path_temp_steps):
            import shutil
            shutil.rmtree(ctx.path_temp_steps)
            logger.info(f"Carpeta temporal eliminada: {ctx.path_temp_steps}")
    except Exception as e:
        logger.warning(f"No se pudo eliminar carpeta temporal: {e}")

