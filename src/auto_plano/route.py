import os

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Query
from fastapi.responses import FileResponse
import numpy as np
import pandas as pd
from shapely import Polygon
from src.auto_plano.generate_2d import dibujar_geometrias, dibujar_geometrias_por_piso
from src.auto_plano.generate_vertices import generate_geometry
from src.auto_plano.repository import actualizar_vectores_proyecto, obtener_proyecto_por_id
from src.auto_plano.service import exportar_unico_archivo_cad, find_max_rect_for_angle_fast, find_multiple_max_rectangles_optimized, local_a_mundo, procesar_distribucion_principal, procesar_excel_real, extraer_df_calculos, procesar_multiple_terrenos, procesar_rectangulo_recto_al_origen, procesar_segundo_cuadrante, procesar_geometria_utm, reconstruir_zonas, visualizar_distribucion_global
from utils.utils import preparar_df_para_api, restaurar_plano, vertices_a_dataframe
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go
import numpy as np
router = APIRouter()

@router.post("/generate-project")
async def read_item(data: dict = Body(...)):
    proyecto_id = data["id"]
    # data_aforo ya es un diccionario con tu JSON
    archivo = "plantilla.xlsx"
    
    aforo = data["aforo"]
    vertices = data["vertices"]
    
    # Conversión a lista de tuplas
    utm_coords = [tuple(v) for v in vertices]
    
    # Convertimos a una matriz de NumPy
    coords_matrix = np.array(utm_coords)

    # Separamos las columnas
    x_utm = coords_matrix[:, 0]
    y_utm = coords_matrix[:, 1]

    # 1. Trasladar al origen (Normalización)
    x0, y0 = x_utm.min(), y_utm.min()
    x = x_utm - x0
    y = y_utm - y0
    
    coords = list(zip(x, y))
    poly = Polygon(coords)

    # 3. Obtener propiedades
    area_poly = poly.area
    perimetro = poly.length
    centroide = poly.centroid
    
    df_vertices_terreno = pd.DataFrame([{
        "tipo": "Terreno",
        "geometria": poly,
        "x": poly.centroid.x,
        "y": poly.centroid.y,
        "nombre": "Vertices Terreno"
    }])
    
    # --- AREA MAS GRANDE ---
    angles = np.arange(0, 180, 5)
    best_rect, best_area, best_angle = None, 0, 0
    
    coords = np.array(utm_coords)

    x0 = coords[:,0].min()
    y0 = coords[:,1].min()

    coords_norm = coords - [x0, y0]

    polygon = Polygon(coords_norm)

    angles = np.arange(0, 180, 5)
    best_rect, best_area, best_angle = None, 0, 0

    for angle in angles:
        rect, area, _ = find_max_rect_for_angle_fast(polygon, angle, cell_size=0.5)
        if rect and area > best_area:
            best_rect, best_area, best_angle = rect, area, angle

    print(f"Mejor área: {best_area:.2f} m² en ángulo {best_angle}°")

    coords = list(best_rect.exterior.coords)

    lado1 = np.linalg.norm(np.array(coords[0]) - np.array(coords[1]))
    lado2 = np.linalg.norm(np.array(coords[1]) - np.array(coords[2]))

    largo_max_cuadrante = max(lado1, lado2)
    ancho_max_cuadrante = min(lado1, lado2)

    df_cuadrante_max = pd.DataFrame([{
        "tipo": "Cuadrante",
        "geometria": best_rect,
        "x": best_rect.centroid.x,
        "y": best_rect.centroid.y,
        "nombre": "Cuadrante Maximo",
        "largo" : largo_max_cuadrante,
        "ancho" : ancho_max_cuadrante,
        "area_m2" : largo_max_cuadrante * ancho_max_cuadrante
    }])


    
    # Procesar en el excel
    procesar_excel_real(aforo, archivo)
    
    # Extraer data en DF del excel
    df_ambientes = extraer_df_calculos(archivo)
    df_excel = df_ambientes
    
    # Pabellones
    plano_generado = generate_geometry(df_excel, df_cuadrante_max)
    
    df_plano_restaurado = restaurar_plano(plano_generado, df_cuadrante_max, best_angle)
    
    df_total_geometrias = pd.concat([df_vertices_terreno, df_plano_restaurado])

    respuesta_serializable = preparar_df_para_api(df_total_geometrias)
    
    actualizar_vectores_proyecto(proyecto_id, respuesta_serializable)
    
    return {
        "ambientes" : df_ambientes.to_dict(orient="records"),
        "vertices" :respuesta_serializable
    }
    
@router.get("/project/{item_id}")
async def read_item(item_id: int):
    project = obtener_proyecto_por_id(item_id)
    
    return {"data" : project}



@router.get("/project-plane2d/{item_id}", response_class=HTMLResponse)
async def read_item(item_id: int, piso: int = Query(1, description="Número de piso a mostrar")):
    project = obtener_proyecto_por_id(item_id)
    vertices_json = project["vertices_generadas"]
    df_render =  vertices_a_dataframe(vertices_json)
    fig = dibujar_geometrias(df_render)

    # 🔁 convertir a HTML completo
    fig.update_layout(
        width=900,
        height=580,
        autosize=True,
    )
    html = fig.to_html(full_html=False, include_plotlyjs="cdn")  # CDN asegura que se cargue Plotly.js

    return HTMLResponse(content=html)

    
@router.get("/project-export/{item_id}")
async def export_project_dxf(item_id: int, background_tasks: BackgroundTasks):
    # 1. Obtener datos del proyecto
    project = obtener_proyecto_por_id(item_id)
    if not project or "vertices_generadas" not in project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado o sin datos.")

    vertices = project["vertices_generadas"]
    df = pd.DataFrame(vertices)

    if df.empty:
        raise HTTPException(status_code=400, detail="El proyecto no tiene geometrías para exportar.")

    # --- PASO CRUCIAL: Conversión a Objetos Shapely ---
    # Sin esto, la función de exportación fallará al intentar calcular centroides
    try:
        df['geometria_mundo'] = df['geometria_mundo'].apply(
            lambda coords: Polygon(coords) if isinstance(coords, list) and len(coords) >= 3 else None
        )
    except Exception as e:
        print(f"❌ Error convirtiendo coordenadas: {e}")
        raise HTTPException(status_code=500, detail="Error en el formato de coordenadas.")

    # 3. Generar el archivo físico temporalmente
    filename = f"plano_{item_id}.dxf"
    
    try:
        exportar_unico_archivo_cad(df, filename=filename)
    except Exception as e:
        print(f"❌ Error generando DXF: {e}")
        raise HTTPException(status_code=500, detail="Error interno al generar el archivo CAD.")

    # 4. Tarea de limpieza (borrar archivo después de enviar)
    def remove_file(path: str):
        if os.path.exists(path):
            os.remove(path)
    
    background_tasks.add_task(remove_file, filename)

    # 5. Retornar el archivo
    return FileResponse(
        path=filename, 
        filename=f"proyecto_{item_id}.dxf", 
        media_type='application/dxf',
        headers={"Content-Disposition": f"attachment; filename=proyecto_{item_id}.dxf"}
    )