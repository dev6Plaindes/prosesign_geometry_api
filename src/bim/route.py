import base64
import json
from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse
from src.bim.services import service_generate_costos_infraestructue, service_generate_pdf_project, service_generate_project, service_get_job
from src.bim.schemas.schema_response import ProjectPDFResponse, ResponseGenerateProject, ResponseGetJob
from bim.render_2d import (
    render_2d_shapely_automatico_regex,
)
from bim.render_3d import render_3d
from bim.render_wrap import wrap_plotly_figure_in_html
from bim.utils.step_to_json import datos_to_shapely
from src.motor.services.gemini_nanobanana import GeminiNanoBananaService
from src.motor.render import save_render_image
from src.bim.repository import (
    get_all_project,
    get_project_by_id,
)
from fastapi import APIRouter, HTTPException, status
import os

router = APIRouter()

@router.post("/generate-costos-project/{id_project}")
def generate_costos_project(id_project : int):
    service = service_generate_costos_infraestructue(id_project)
    return service

@router.post("/generate-project", response_model=ResponseGenerateProject)
def generate_project(data: dict = Body(...)):
    service = service_generate_project(data)
    return service

@router.get("/jobs/{job_id}", response_model=ResponseGetJob)
def get_job(job_id: int):
    service = service_get_job(job_id)
    return service

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
        fig_3d = render_3d(vertices)
        ruta_3d = save_render_image(fig_3d, tipo="3d")
        print(f"Render 3D guardado en: {ruta_3d}")

        service = GeminiNanoBananaService(api_key=os.getenv("GEMINI_API_KEY"))

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

    return {"status": "success", "data": vertices}

@router.get(
    "/project/generate-proinvierte/{project_id}", 
    status_code=status.HTTP_200_OK,
    # response_model=GenerateProjectPDFResponse
)
def generate_pdf_for_proinvierte(project_id: int):
    service = service_generate_pdf_project(project_id)
    return service

@router.get("/projects", status_code=status.HTTP_200_OK)
def get_allproject():
    project_data = get_all_project()

    return {"status": "success", "data": project_data}
