import os

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Query
from fastapi.responses import FileResponse
import numpy as np
import pandas as pd
from shapely import Polygon
from src.motor.render import Render
from src.motor.process_motor import process_ambientes_motor_to_dict, transformar_df_con_referencia
from src.auto_plano.generate_2d import dibujar_geometrias, dibujar_geometrias_por_piso
from src.auto_plano.generate_vertices import generate_geometry
from src.auto_plano.repository import actualizar_vectores_proyecto, obtener_proyecto_por_id
# from src.auto_plano.service import exportar_unico_archivo_cad, find_max_rect_for_angle_fast, find_multiple_max_rectangles_optimized, get_maximal_rectangle_dataframe, local_a_mundo, procesar_distribucion_principal, procesar_excel_real, procesar_y_extraer_sheets, extraer_df_calculos, procesar_multiple_terrenos, procesar_rectangulo_recto_al_origen, procesar_segundo_cuadrante, procesar_geometria_utm, reconstruir_zonas, visualizar_distribucion_global
from utils.utils import preparar_df_para_api, restaurar_plano, vertices_a_dataframe
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
import numpy as np

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

    cuadrante_ancho = max_cuadrante.iloc[0]["ancho"]
    cuadrante_largo = max_cuadrante.iloc[0]["largo"]
    
    # Generar plano
    df_data_motor =  process_ambientes_motor_to_dict(df_excel,cuadrante_ancho, cuadrante_largo)
    
    # Mover plano al cuadrante del terreno
    data_transformada = transformar_df_con_referencia(df_data_motor, max_cuadrante, angle)
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
    render_api = Render(geometrias, pisos=3)
    print(render)
    
    if render=="2d":
        html_fig = render_api.render_2d()
        return HTMLResponse(content=html_fig)
    
    elif render=="3d":
        fig = render_api.render_3d()
        html_fig = fig.to_html(full_html=False, include_plotlyjs="cdn")  # CDN asegura que se cargue Plotly.js
        return HTMLResponse(content=html_fig)
                
    # return {"data" : project}


    