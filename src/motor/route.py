import base64
import os

from fastapi import APIRouter, Body
import pandas as pd
from src.motor.utils.get_zona_prov import get_zona_provincia
from src.motor.export_xdf import get_max_pisos
from src.motor.render import Render
from src.motor.process_motor import process_ambientes_motor_to_dict, transformar_df_con_referencia
from src.auto_plano.repository import actualizar_vectores_proyecto, clean_for_json, geometry_to_json, obtener_proyecto_por_id
from fastapi.responses import HTMLResponse
import numpy as np
from scipy.spatial.distance import euclidean

from src.motor.max_cuadrante import find_best_rectangle, normalizar_polygon, polygon_get_data, df_geom_to_dict
from src.motor.calculadora_sheets import procesar_y_extraer_sheets

from src.motor.utils.get_zona_prov import get_zona_provincia
from src.motor.services.gemini_nanobanana import GeminiNanoBananaService
from src.motor.render import Render, save_render_image

router = APIRouter()

@router.post("/generate-project")
async def motor_project(data: dict = Body(...)):
    vertices = data["vertices"]
    aforo_api = data["aforo"]
    proyecto_id = data["id"]
    provincia = data["provincia"]
    
    df_aforo_api = pd.DataFrame({
        "nivel": ["Inicial", "Primaria", "Secundaria"],
        "aforo_grado": [aforo_api["aforoInicial"], aforo_api["aforoPrimaria"], aforo_api["aforoSecundaria"]],
        "cantidad_aulas": [aforo_api["aulaInicial"], aforo_api["aulaPrimaria"], aforo_api["aulaSecundaria"]]
    })
    
    # Procesar aforo y calcular
    df_excel = procesar_y_extraer_sheets(df_aforo_api.to_dict(orient="records"), "MARIATEGUI")
    
    # Terreno
    terreno_poly = normalizar_polygon(vertices)
    df_terreno_poly= polygon_get_data(terreno_poly)
    terreno_poly_dict = df_geom_to_dict(df_terreno_poly)
    
    # Cuadrante max
    rect, area, angle = find_best_rectangle(terreno_poly)
    max_cuadrante = polygon_get_data(rect)
    max_cuad_dict = df_geom_to_dict(max_cuadrante)

    puntos = list(rect.exterior.coords)

    lado_1 = euclidean(puntos[0], puntos[1])
    lado_2 = euclidean(puntos[1], puntos[2])

    cuadrante_largo = max(lado_1, lado_2)
    cuadrante_ancho = min(lado_1, lado_2)

    max_cuadrante = polygon_get_data(rect)
    max_cuad_dict = df_geom_to_dict(max_cuadrante)
    max_cuadrante.iloc[0]["ancho"] = cuadrante_ancho
    max_cuadrante.iloc[0]["largo"] = cuadrante_largo
    
    zona_project, _= get_zona_provincia(provincia)
    
    # Generar plano
    df_data_motor, angulo_final =  process_ambientes_motor_to_dict(df_excel,cuadrante_ancho, cuadrante_largo, angle, zona=zona_project)
    
    # Mover plano al cuadrante del terreno
    data_transformada = transformar_df_con_referencia(df_data_motor, max_cuadrante.to_dict(orient="records"))
    # data_dict_transformada = df_geom_to_dict(data_transformada)
    
    # Unir todas las geometrias y vertices del terreno
    data_complete = terreno_poly_dict + data_transformada
    
    # Guardar en la base de datos
    json_data = geometry_to_json(data_complete)
    json_data_response = clean_for_json(json_data)
    
    actualizar_vectores_proyecto(proyecto_id, json_data_response)
    
    return {
        "ambientes" : max_cuad_dict,
        "data": json_data_response
    }
    
@router.get("/project/{item_id}")
async def get_project_id(item_id: int):
    project = obtener_proyecto_por_id(item_id)
    return {"data" : project}

@router.get("/project-render/{item_id}", response_class=HTMLResponse)
async def render_project(item_id: int, render: str):
    project = obtener_proyecto_por_id(item_id)
    
    geometrias = project.get("vertices_generadas", [])
    max_piso = get_max_pisos(geometrias)
    render_api = Render(geometrias, pisos=max_piso)
    
    if render=="2d":
        html_fig = render_api.render_2d(html=True)
        return HTMLResponse(content=html_fig)
    
    elif render=="3d":
        # fig = render_api.render_3d()
        html_fig = render_api.render_3d(html=True)
        # html_fig = fig.to_html(full_html=False, include_plotlyjs="cdn")
        return HTMLResponse(content=html_fig)

    elif render=="render ia":
        fig_3d = render_api.render_3d()
        ruta_3d = save_render_image(fig_3d, tipo="3d")
        print(f"Render 3D guardado en: {ruta_3d}")
        
        service = GeminiNanoBananaService(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        print("Generando render con IA...")
        
        result = service.generate_architecture_render(
            images_path=[ruta_3d]
        )
        
        if result.get("success") and result.get("binary_image"):
            # Tomamos la primera imagen generada de la lista
            image_bytes = result["binary_image"]
            
            # Convertimos los bytes a una cadena Base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
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
        
