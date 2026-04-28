from fastapi import APIRouter, Body
import pandas as pd
from src.motor.export_xdf import get_max_pisos
from src.motor.render import Render
from src.motor.process_motor import process_ambientes_motor_to_dict, transformar_df_con_referencia
from src.auto_plano.repository import actualizar_vectores_proyecto, obtener_proyecto_por_id
from fastapi.responses import HTMLResponse
import numpy as np
from scipy.spatial.distance import euclidean

from src.motor.max_cuadrante import find_best_rectangle, normalizar_polygon, polygon_get_data, df_geom_to_dict
from src.motor.calculadora_sheets import procesar_y_extraer_sheets

router = APIRouter()

@router.post("/generate-project")
async def motor_project(data: dict = Body(...)):
    
    vertices = data["vertices"]
    aforo_api = data["aforo"]
    proyecto_id = data["id"]
    
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
    
    # Generar plano
    df_data_motor, angulo_final =  process_ambientes_motor_to_dict(df_excel,cuadrante_ancho, cuadrante_largo, angle)
    
    # Mover plano al cuadrante del terreno
    data_transformada = transformar_df_con_referencia(df_data_motor, max_cuadrante)
    data_dict_transformada = df_geom_to_dict(data_transformada)
    
    # Unir todas las geometrias y vertices del terreno
    data_complete = terreno_poly_dict + data_dict_transformada
    
    # Guardar en la base de datos
    actualizar_vectores_proyecto(proyecto_id, data_complete)
        
    return {
        "ambientes" : max_cuad_dict,
        "data": data_complete
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
    print(render)
    
    if render=="2d":
        html_fig = render_api.render_2d()
        return HTMLResponse(content=html_fig)
    
    elif render=="3d":
        fig = render_api.render_3d()
        html_fig = fig.to_html(full_html=False, include_plotlyjs="cdn")  # CDN asegura que se cargue Plotly.js
        return HTMLResponse(content=html_fig)
                
    # return {"data" : project}


    