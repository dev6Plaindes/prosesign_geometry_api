import os

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException
from fastapi.responses import FileResponse
import numpy as np
import pandas as pd
from shapely import Polygon
from src.auto_plano.repository import actualizar_vectores_proyecto, obtener_proyecto_por_id
from src.auto_plano.service import exportar_unico_archivo_cad, find_max_rect_for_angle_fast, find_multiple_max_rectangles_optimized, local_a_mundo, procesar_distribucion_principal, procesar_excel_real, extraer_df_calculos, procesar_multiple_terrenos, procesar_rectangulo_recto_al_origen, procesar_segundo_cuadrante, procesar_geometria_utm, reconstruir_zonas, visualizar_distribucion_global
from utils.utils import preparar_df_para_api

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
    
    # procesar_geometria_utm(utm_coords)
    
    # --- AREA MAS GRANDE ---
    polygon = Polygon(utm_coords)
    angles = np.arange(0, 180, 5)
    best_rect, best_area, best_angle = None, 0, 0

    for angle in angles:
        rect, area, _ = find_max_rect_for_angle_fast(polygon, angle, cell_size=0.5)
        if rect and area > best_area:
            best_rect, best_area, best_angle = rect, area, angle

    print(f"Mejor área: {best_area:.2f} m² en ángulo {best_angle}°")
    
    # --- AREAS MAS GRANDES ---
    rects = find_multiple_max_rectangles_optimized(polygon, angles=np.arange(0, 180, 5), cell_size=0.5, max_rects=3)

    for i, (rect, area, angle) in enumerate(rects, start=1):
        print(f"Rectángulo {i}: área {area:.2f} m², ángulo {angle}°")
    
    # MOVER EL MAXIMO CUADRANTE A EJE X,Y (0,0)
    df_cuadrante_max = procesar_rectangulo_recto_al_origen(best_rect, best_angle)
    
    # Procesar en el excel
    procesar_excel_real(aforo, archivo)
    
    # Extraer data en DF del excel
    df_ambientes = extraer_df_calculos(archivo)
    
    terreno_principal = procesar_distribucion_principal(df_ambientes, df_cuadrante_max, False)
    
    # zonas_dict, df_vectores_generados = reconstruir_zonas(terreno_principal["terreno"])
    
    df_global = procesar_multiple_terrenos([(terreno_principal["terreno"], best_rect, best_angle)], utm_coords)
    
    # visualizar_distribucion_global(df_global)
    
    exist_2do_cuad = False
    
    # # Suponiendo que ya tienes df_calculos y los rectángulos detectados:
    # if exist_2do_cuad:
    #     resultado_q2 = procesar_segundo_cuadrante(
    #         df_calculos=df_resultados, 
    #         rects=rects, 
    #         datos_finales_2do_cuad=df_resultados
    #     )
        
    # Ahora puedes acceder a las zonas procesadas:
    # mis_zonas = resultado_q2["zonas"]
    respuesta_serializable = preparar_df_para_api(df_global)
    
    url_bd = "mysql+mysqlconnector://usuario_lima:password@localhost/prodesign_db"
    actualizar_vectores_proyecto(proyecto_id, respuesta_serializable)
    
    return {
        "ambientes" : df_ambientes.to_dict(orient="records"),
        "vertices" :respuesta_serializable
    }
    
@router.get("/project/{item_id}")
async def read_item(item_id: int):
    project = obtener_proyecto_por_id(item_id)
    
    return {"data" : project}

    
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