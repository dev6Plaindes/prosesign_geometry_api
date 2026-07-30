import json
import streamlit as st
import pandas as pd
import numpy as np

from bim.render_2d import render_2d_shapely_automatico_regex
from bim.utils.step_to_json import datos_to_shapely
from data_test import data_test, ambientes_test
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.bim.pipeline.project_school.create.stage_build_plane import stage_build_plane
from src.bim.pipeline.project_school.create.stage_classifer_region import stage_classifier_region
from src.bim.pipeline.project_school.create.stage_convert_plane_and_save import stage_convert_plane_and_save
from src.bim.pipeline.project_school.create.stage_get_ambientes import stage_get_ambientes_test
from src.bim.pipeline.project_school.create.stage_update_data_project import stage_update_data_project
from src.bim.repository import get_project_by_id
from src.bim.schemas.project_schema import ProjectRequest

st.set_page_config(
    page_title="Dev",
    page_icon="📊",
    layout="wide"
)

request_data = ProjectRequest(**data_test)
item_id = 906
ctx_data = PipelineContext(request=request_data, id_project=905, id_version_project=item_id)

ctx_data.ambientes = ambientes_test

# --- PIPELINE DE PROCESAMIENTO ---
stage_classifier_region(ctx_data)
stage_get_ambientes_test(ctx_data)
stage_build_plane(ctx_data)
stage_convert_plane_and_save(ctx_data)
stage_update_data_project(ctx_data)

# --- OBTENER DATOS DE LA BASE DE DATOS ---
project_data = get_project_by_id(item_id)
vertices = project_data.get("vertices", [])
vertices = json.loads(vertices) if isinstance(vertices, str) else vertices
render = "2d"

# --- VISUALIZACIÓN CON PLOTLY NATIVO ---
if render == "2d":
    vertices = datos_to_shapely(vertices)
    # vertices_for_nivel es un diccionario: { "Nivel 1": fig_plotly, "Nivel 2": fig_plotly, ... }
    vertices_for_nivel = render_2d_shapely_automatico_regex(vertices)

    if vertices_for_nivel:
        st.subheader("Visualización del Plano 2D (Interactivo)")
        
        # Creamos una pestaña para cada nivel
        nombres_niveles = list(vertices_for_nivel.keys())
        tabs = st.tabs([f"Nivel {nivel}" for nivel in nombres_niveles])
        
        # Iteramos sobre las pestañas y los gráficos correspondientes
        for tab, (nivel, grafico) in zip(tabs, vertices_for_nivel.items()):
            with tab:
                st.write(f"### Vista - {nivel}")
                
                # Renderizador nativo de Plotly en Streamlit
                st.plotly_chart(
                    grafico, 
                    use_container_width=True, # Ajusta automáticamente al tamaño de la pestaña
                    theme="streamlit"         # Aplica el diseño limpio de Streamlit al gráfico
                )
    else:
        st.warning("No se encontraron niveles en el proyecto para graficar.")