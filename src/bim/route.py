import base64
import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from bim.adapters.shapely_to_cq import obtener_referencia_cuadrante
from bim.max_cuadrante import find_best_rectangle, find_top_3_rectangles, normalizar_polygon
from bim.render import save_render_image
from src.bim.pipeline.project_school.costos.main_pipeline import (
    calculate_costos_pipeline,
)
from src.bim.schemas.project_schema import ProjectRequest, ProjectRequestMaxCuad, TerrenoRequest
from src.bim.schemas.schema_dto import ProjectDataForCostos
from src.bim.schemas.schema_request import CostosRequest
from src.bim.services import (
    service_generate_costos_infraestructue,
    service_generate_pdf_project,
    service_generate_project,
    service_get_job,
)
from src.bim.schemas.schema_response import (
    ProjectPDFResponse,
    ResponseGenerateProject,
    ResponseGetJob,
)
from bim.render_2d import (
    render_2d_shapely_automatico_regex,
)
from bim.render_3d import render_3d
from bim.render_wrap import wrap_plotly_figure_in_html
from bim.utils.step_to_json import datos_to_shapely, polygon_a_mesh_array
from src.bim.adapters.gemini_nanobanana import GeminiNanoBananaService
from src.bim.repository import (
    get_all_project,
    get_all_project_by_user,
    get_data_calculo_costos_project,
    get_project_by_id,
)
from fastapi import APIRouter, HTTPException, status
import os

router = APIRouter()

def poly_to_list(poly):
    return [[float(x), float(y)] for x, y in poly.exterior.coords]

@router.post("/generate-project", response_model=ResponseGenerateProject)
def generate_project(data: ProjectRequestMaxCuad):  # OK
    service = service_generate_project(data)
    return service

@router.post("/generate-max-cuadrante")
def generate_max_cuadrante(data : TerrenoRequest):
    vertices = data.vertices
    vertices_terreno = [[punto["x"], punto["y"]] for punto in vertices]
    terreno_poly = normalizar_polygon(vertices_terreno)
    
    # 1. Obtenemos el top 3 de cuadrantes (lista de diccionarios con Shapely objects)
    maximos_cuadrantes = find_top_3_rectangles(terreno_poly)
    
    # 2. Mapeamos la lista para seguir la estructura requerida transformando la geometría
    respuesta = []
    for cuadrante in maximos_cuadrantes:
        respuesta.append({
            "angle_max_cuadrante": cuadrante["best_angle"],
            "area_m2": cuadrante["area_m2"],
            "vertices": {
                "terreno": poly_to_list(terreno_poly),
                "maximo_cuadrante": poly_to_list(cuadrante["geometria"])
            }
        })
        
    # Retorna el array/lista con la estructura exacta por cada cuadrante encontrado
    return respuesta

@router.get("/jobs/{job_id}", response_model=ResponseGetJob)  # OK
def get_job(job_id: str):
    service = service_get_job(job_id)
    return service


@router.get("/project/costos/{project_id}")  # OK
def get_costos_project(project_id: int):
    data = get_data_calculo_costos_project(project_id)

    return {"data": data}


@router.post("/project/costos/{project_id}")
def create_costos_project(project_id: int, data_req: CostosRequest):
    project_data = get_project_by_id(project_id)

    project_data["aforo"] = json.loads(project_data["aforo"])
    project_data["resumen_ambientes"] = json.loads(project_data["resumen_ambientes"])
    project_data_model = ProjectDataForCostos(**project_data)

    data = calculate_costos_pipeline(data_req=data_req, data_project=project_data_model)

    return {
        "data": {"data_calculo_costos": [json.loads(data)], "id_project": project_id}
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
    response_model=ProjectPDFResponse,
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

@router.get("/projects/user/{id_user}", status_code=status.HTTP_200_OK)
def get_allproject(id_user: int):
    project_data = get_all_project_by_user(id_user)

    return {
            "msg": "Proyectos obtenidos por User ID.",
            "proyectos": project_data
        }
