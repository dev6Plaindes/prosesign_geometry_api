import pandas as pd
from bim.render_2d import render_2d_shapely, render_2d_shapely_automatico_regex
from bim.render_3d import render_3d
from bim.utils.step_to_json import datos_to_shapely, ensamblaje_to_array
from refactor.cuadrante_1 import cuadrante_1
import cadquery as cq
import streamlit as st

vertices_terreno = [
    [272100.00, 8692200.00],
    [272100.00, 8692235.00],
    [272140.00, 8692250.00],
    [272140.00, 8692290.00],
    [272190.00, 8692290.00],
    [272190.00, 8692255.00],
    [272150.00, 8692240.00],
    [272150.00, 8692200.00],
]

df_excel = pd.read_csv("./data_ambiente.csv")
cuadrante_max_and_terreno, ensamblaje, factory_capas = cuadrante_1(vertices_terreno, df_excel)

datos = ensamblaje_to_array(ensamblaje)

st.dataframe(datos)

data_cuadrante_max_and_terreno_2d = datos_to_shapely(cuadrante_max_and_terreno)

fig_3d = render_3d(cuadrante_max_and_terreno)

st.plotly_chart(fig_3d)
