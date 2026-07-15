# [DOCUMENTACIÓN] Se importó FileResponse de fastapi.responses y se envolvió el endpoint de proinvierte y de render ia en bloques try/except para capturar fallas e impedir errores 500 / CORS en el cliente.
import base64
import json
from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse, FileResponse
from bim.render import save_render_image
from src.bim.pipeline.project_school.costos.main_pipeline import calculate_costos_pipeline
from src.bim.schemas.project_schema import ProjectRequest
from src.bim.schemas.schema_dto import ProjectDataForCostos
from src.bim.schemas.schema_request import CostosRequest
from src.bim.services import service_generate_costos_infraestructue, service_generate_pdf_project, service_generate_project, service_get_job
from src.bim.schemas.schema_response import ProjectPDFResponse, ResponseGenerateProject, ResponseGetJob
from bim.render_2d import (
    render_2d_shapely_automatico_regex,
)
from bim.render_3d import render_3d
from bim.render_wrap import wrap_plotly_figure_in_html
from bim.utils.step_to_json import datos_to_shapely
from src.bim.adapters.gemini_nanobanana import GeminiNanoBananaService

from src.bim.repository import (
    get_all_project,
    get_data_calculo_costos_project,
    get_project_by_id,
)
from fastapi import APIRouter, HTTPException, status
from src.utils.logger import logger
import os

router = APIRouter()

@router.post(
    "/generate-project", 
    response_model=ResponseGenerateProject
)
def generate_project(data: ProjectRequest):       # OK
    service = service_generate_project(data)
    return service

@router.get("/jobs/{job_id}", response_model=ResponseGetJob) # OK
def get_job(job_id: str):
    service = service_get_job(job_id)
    return service

@router.get("/project/costos/{project_id}") # OK
def get_costos_project(project_id: int):
    data = get_data_calculo_costos_project(project_id)
    
    return {
        "data" : data
    }
    
@router.post("/project/costos/{project_id}")
def create_costos_project(project_id: int, data_req : CostosRequest):
    project_data = get_project_by_id(project_id)

    project_data["aforo"] = json.loads(project_data["aforo"])
    project_data["resumen_ambientes"] = json.loads(project_data["resumen_ambientes"])
    project_data_model = ProjectDataForCostos(**project_data)

    data = calculate_costos_pipeline(
        data_req=data_req,
        data_project=project_data_model
    )
    
    return {
        "data" : {
            "data_calculo_costos" : [json.loads(data)],
            "id_project" : project_id
        }
    }
    

@router.get("/project/{project_id}", status_code=status.HTTP_200_OK)
def get_project(project_id: int):
    project_data = get_project_by_id(project_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return {"status": "success", "data": project_data}


@router.get(
    "/project/pdf/{project_id}", 
    status_code=status.HTTP_200_OK,
    response_model=ProjectPDFResponse
    )
def get_project_pdf_url(project_id: int):
    project_data = get_project_by_id(project_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return {
        "status": "success",
        "url_pdf": project_data["url_pdf"] if "url_pdf" in project_data else None,
    }


@router.get("/project-render/{item_id}", response_class=HTMLResponse)
def get_project_render(item_id: int, render: str):
    project_data = get_project_by_id(item_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {item_id} not found",
        )
    vertices = project_data.get("vertices", [])
    vertices = json.loads(vertices) if isinstance(vertices, str) else vertices

    if render == "3d":
        fig_3d = render_3d(vertices)
        html = wrap_plotly_figure_in_html(fig_3d)
        return HTMLResponse(content=html)

    elif render == "2d":
        vertices = datos_to_shapely(vertices)
        vertices_for_nivel = render_2d_shapely_automatico_regex(vertices)

        html_all_niveles = ""
        for nivel, grafico in vertices_for_nivel.items():
            html = wrap_plotly_figure_in_html(grafico)
            html_all_niveles += html

        return HTMLResponse(content=html_all_niveles)

    elif render == "render ia":
        # [DOCUMENTACIÓN] Se envolvió la llamada al servicio de IA (Gemini) en un bloque try/except para capturar credenciales inválidas u otros errores de API, devolviendo un HTML de error estilizado en lugar de un error 500
        try:
            fig_3d = render_3d(vertices)
            ruta_3d = save_render_image(fig_3d, tipo="3d")
            print(f"Render 3D guardado en: {ruta_3d}")

            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                raise ValueError("La clave GEMINI_API_KEY no está configurada en el archivo .env.")

            service = GeminiNanoBananaService(api_key=gemini_key)

            print("Generando render con IA...")

            result = service.generate_architecture_render(images_path=[ruta_3d])

            if result.get("success") and result.get("binary_image"):
                # Tomamos la primera imagen generada de la lista
                image_bytes = result["binary_image"]

                # Convertimos los bytes a una cadena Base64
                base64_image = base64.b64encode(image_bytes).decode("utf-8")

                # Construimos un HTML limpio para mostrar el resultado
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Render Generado</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f9;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            margin: 0;
                            padding: 20px;
                        }}
                        .container {{
                            background: white;
                            padding: 20px;
                            border-radius: 8px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            text-align: center;
                            max-width: 90%;
                        }}
                        img {{
                            max-width: 100%;
                            height: auto;
                            border-radius: 4px;
                            margin-top: 15px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Resultado del Render de Arquitectura</h2>
                        <img src="data:image/png;base64,{base64_image}" alt="Render de Arquitectura">
                    </div>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content, status_code=200)
            else:
                raise Exception("La respuesta del servicio de IA no devolvió imágenes válidas.")
        except Exception as ia_error:
            # Retornar página de error controlada para evitar pantallas de fallo de carga del navegador o errores CORS
            html_error = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Error Render IA</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #fff1f0;
                        color: #cf1322;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        margin: 0;
                        padding: 20px;
                        height: 90vh;
                    }}
                    .container {{
                        background: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 80%;
                        border: 1px solid #ffa39e;
                    }}
                    h3 {{ margin-top: 0; }}
                    p {{ color: #595959; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h3>Error al generar Render de IA</h3>
                    <p style="color: #cf1322; font-weight: bold;">{str(ia_error)}</p>
                    <p>Por favor verifique la clave GEMINI_API_KEY en su archivo .env del servidor de geometría.</p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_error, status_code=200)


    return {"status": "success", "data": vertices}

@router.get(
    "/project/generate-proinvierte/{project_id}", 
    status_code=status.HTTP_200_OK,
)
def generate_pdf_for_proinvierte(project_id: int):
    try:
        service = service_generate_pdf_project(project_id)
        return service
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al generar PDF de ProInvierte para project_id={project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al generar el PDF del proyecto: {str(e)}"
        )

@router.get("/project/pdf-download/{project_id}")
def download_local_pdf(project_id: int):
    from fastapi.responses import Response
    from src.bim.repository import get_content_pdf

    local_path = f"local_pdfs/plane_{project_id}.pdf"
    if os.path.exists(local_path):
        return FileResponse(
            local_path, 
            media_type="application/pdf", 
            filename=f"plane_{project_id}.pdf"
        )

    try:
        pdf_binary = get_content_pdf(project_id)
        if pdf_binary:
            return Response(
                content=pdf_binary,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=plane_{project_id}.pdf"}
            )
    except Exception as e:
        logger.warning(f"No se pudo leer content_pdf de DB para proyecto {project_id}: {e}")

    raise HTTPException(
        status_code=404,
        detail=f"El PDF del proyecto {project_id} no está disponible. Ve a 'Enviar a ProInviert' para generarlo nuevamente."
    )

@router.get("/projects", status_code=status.HTTP_200_OK)
def get_allproject():
    project_data = get_all_project()

    return {"status": "success", "data": project_data}

@router.get("/debug-logs")
def get_debug_logs(lines: int = 150):
    try:
        log_paths = [
            "logs/app.log",
            "worker.log",
            "backend.log"
        ]
        results = {}
        for path in log_paths:
            if os.path.exists(path):
                for encoding in ["utf-8", "utf-16", "latin-1"]:
                    try:
                        with open(path, "r", encoding=encoding) as f:
                            content_lines = f.readlines()
                            last_lines = content_lines[-lines:]
                            results[path] = "".join(last_lines)
                        break
                    except Exception:
                        continue
            else:
                results[path] = "File not found"
        return results
    except Exception as e:
        return {"error": str(e)}







