# [DOCUMENTACIÓN] Se creó el archivo de pruebas test_renders.py para validar la correcta generación, optimización e integración de los módulos de renderizado y diseño geométrico.

import os
import pytest
import numpy as np
import plotly.graph_objects as go
from shapely.geometry import Polygon

# Imports del backend
from bim.cuadrante_1 import cuadrante_1
from bim.cuadrante_2do import build_2do_cuad
from bim.creations.escaleras import get_stair_dimensions
from bim.capas import FactoryCapas
import cadquery as cq

from bim.get_zona_prov import get_zona_provincia
from bim.max_cuadrante import maximal_rectangle, get_candidate_angles, find_best_rectangle
from bim.render_wrap import wrap_plotly_figure_in_html
from bim.render import save_render_image
from bim.render_2d import render_2d, render_2d_shapely, render_2d_shapely_automatico_regex
from bim.render_3d import render_3d
from bim.utils.step_to_json import datos_to_shapely, ensamblaje_to_array

# Datos de prueba autocontenidos
MOCK_VERTICES = [
    [0.0, 0.0],
    [65.0, 0.0],
    [65.0, 50.0],
    [0.0, 50.0]
]

MOCK_AMBIENTES = [
    {
        "Ambientes": "Aulas Primaria",
        "Metros_cuadrados": 120,
        "Cantidad": 2,
        "Unitario": 60,
        "Ancho": 7.5,
        "Largo": 8,
        "Tipo": "Fijo",
        "Pabellon": "Izquierda",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Escalera Prim",
        "Metros_cuadrados": 8.64,
        "Cantidad": 1,
        "Unitario": 8.64,
        "Ancho": 7.5,
        "Largo": 2.5,
        "Tipo": "Fijo",
        "Pabellon": "Izquierda",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Aulas Secundaria",
        "Metros_cuadrados": 120,
        "Cantidad": 2,
        "Unitario": 60,
        "Ancho": 7.5,
        "Largo": 8,
        "Tipo": "Fijo",
        "Pabellon": "Derecha",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Escalera Sec",
        "Metros_cuadrados": 8.64,
        "Cantidad": 1,
        "Unitario": 8.64,
        "Ancho": 7.5,
        "Largo": 2.5,
        "Tipo": "Fijo",
        "Pabellon": "Derecha",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Aulas Ciclo II",
        "Metros_cuadrados": 120,
        "Cantidad": 2,
        "Unitario": 60,
        "Ancho": 8.0,
        "Largo": 7.5,
        "Tipo": "Fijo",
        "Pabellon": "Inferior",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Direccion Adm.",
        "Metros_cuadrados": 30,
        "Cantidad": 1,
        "Unitario": 30,
        "Ancho": 2.0,
        "Largo": 5.0,
        "Tipo": "Variable",
        "Pabellon": "Superior",
        "Piso_de_preferencia": "1 y 2"
    },
    {
        "Ambientes": "Patio Inicial",
        "Metros_cuadrados": 150,
        "Cantidad": 1,
        "Unitario": 150,
        "Ancho": 7.5,
        "Largo": 20.0,
        "Tipo": "Variable",
        "Pabellon": "Medio",
        "Piso_de_preferencia": "1"
    },
    {
        "Ambientes": "Losa Deportiva",
        "Metros_cuadrados": 420,
        "Cantidad": 1,
        "Unitario": 420,
        "Ancho": 15,
        "Largo": 28,
        "Tipo": "Fijo",
        "Pabellon": "Medio",
        "Piso_de_preferencia": "1"
    },
    {
        "Ambientes": "SUM",
        "Metros_cuadrados": 345,
        "Cantidad": 1,
        "Unitario": 345,
        "Ancho": 16,
        "Largo": 21.6,
        "Tipo": "Fijo",
        "Pabellon": "Medio",
        "Piso_de_preferencia": "1"
    }
]


def test_get_zona_provincia():
    """Verifica que get_zona_provincia retorne las zonas y techos correctos."""
    # Test zona 1
    zona, techo = get_zona_provincia("Casma")
    assert zona == "zona_1"
    assert techo == "techo concreto"

    # Test zona 3
    zona, techo = get_zona_provincia("Castilla")
    assert zona == "zona_3"
    assert techo == "teja andina"

    # Test ignorar mayúsculas y espacios
    zona, techo = get_zona_provincia("  PaIta  ")
    assert zona == "zona_2"
    assert techo == "techo concreto"

    # Test caso desconocido
    zona, techo = get_zona_provincia("InexistenteProvincia")
    assert zona == "Zona desconocida"
    assert techo == "Tipo de techo desconocido"


def test_max_cuadrante_maximal_rectangle():
    """Valida el cálculo del rectángulo máximo en una matriz binaria."""
    matrix = np.array([
        [0, 1, 1, 0],
        [1, 1, 1, 1],
        [1, 1, 1, 1],
        [0, 0, 1, 0]
    ], dtype=np.uint8)

    area, rect = maximal_rectangle(matrix)
    # El rectángulo máximo de 1s es de 2x4 (filas 1 y 2, columnas 0 a 3) = área 8
    assert area == 8
    # rect tiene el formato (top_left_i, top_left_j, height, width)
    assert rect == (1, 0, 2, 4)


def test_max_cuadrante_candidate_angles():
    """Valida los ángulos candidatos de un polígono."""
    poly = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
    angles = get_candidate_angles(poly)
    # Los lados paralelos a los ejes generan ángulos de 0° y 90°
    assert 0.0 in angles
    assert 90.0 in angles


def test_max_cuadrante_find_best_rectangle():
    """Valida la detección del cuadrante máximo dentro de un polígono."""
    poly = Polygon([(0, 0), (50, 0), (50, 40), (0, 40)])
    best_rect, area, angle = find_best_rectangle(poly)
    assert best_rect is not None
    assert area > 0
    # Al ser un rectángulo perfecto alineado, el ángulo óptimo debe ser cercano a 0
    assert abs(angle) < 0.1 or abs(angle - 90.0) < 0.1 or abs(angle - 180.0) < 0.1


def test_render_wrap_plotly_html():
    """Verifica que wrap_plotly_figure_in_html envuelva correctamente una figura."""
    fig = go.Figure(go.Scatter(x=[1, 2], y=[1, 2]))
    html = wrap_plotly_figure_in_html(fig)
    assert "plotly" in html.lower()
    assert "<div" in html
    assert "width: 75vw" in html


# [DOCUMENTACIÓN] [MOCK_SAVE_IMAGE] Se añadió mockeo para la exportación de imágenes con write_image para evitar dependencia externa de kaleido en las pruebas unitarias.
def test_render_save_image(tmp_path):
    """Verifica la generación y guardado correcto de imágenes png."""
    from unittest.mock import patch
    fig = go.Figure(go.Scatter(x=[1, 2], y=[3, 4]))
    
    def mock_write_image(path, *args, **kwargs):
        with open(path, "wb") as f:
            f.write(b"dummy image data")

    with patch.object(go.Figure, "write_image", side_effect=mock_write_image) as mock_write:
        # Probar guardado tipo 3D
        filename_3d = "test_image.png"
        saved_path_3d = save_render_image(fig, filename=filename_3d, folder=str(tmp_path), tipo="3d")
        assert os.path.exists(saved_path_3d)
        assert saved_path_3d.endswith("3d_test_image.png")
        
        # Probar guardado tipo 2D
        filename_2d = "test_image.png"
        saved_path_2d = save_render_image(fig, filename=filename_2d, folder=str(tmp_path), tipo="2d")
        assert os.path.exists(saved_path_2d)
        assert saved_path_2d.endswith("2d_test_image.png")
        
        assert mock_write.call_count == 2



def test_integration_geometry_and_renders():
    """Genera la geometría real usando los cuadrantes y verifica que todos los renders se generen correctamente."""
    # 1. Generación de geometría con Cuadrante 1 (esto internamente prueba base_structure, escaleras, balcony)
    data_builded, assembly, factory_capas, RESUMEN_AREAS = cuadrante_1(MOCK_VERTICES, MOCK_AMBIENTES)
    
    assert isinstance(assembly, cq.Assembly)
    assert len(data_builded) > 0
    
    # 2. Generación de geometría con Cuadrante 2
    cuadrante_poly = Polygon([(0.0, 0.0), (65.0, 0.0), (65.0, 50.0), (0.0, 50.0)])
    assembly_c2 = build_2do_cuad(
        data_dict_ambientes=MOCK_AMBIENTES,
        cuadrante=cuadrante_poly,
        factory_capas=FactoryCapas(
            ensamblaje=cq.Assembly(),
            degree_referencia=0,
            x_referencia=0,
            y_referencia=0
        )
    )
    # [DOCUMENTACIÓN] [CORRECCIÓN SINTAXIS] Se restauró el paréntesis de cierre del llamado a build_2do_cuad.
    assert isinstance(assembly_c2, list)
    
    
    # 3. Test de render_3d.py
    fig_3d = render_3d(data_builded)
    assert isinstance(fig_3d, go.Figure)
    
    # 4. Test de render_2d.py usando diccionario
    # Convertimos los datos generados a diccionario para render_2d tradicional
    escena_dict = {}
    for pieza in data_builded:
        escena_dict[pieza["name"]] = {
            "vertices": pieza["vertices"],
            "faces": pieza["faces"]
        }
    fig_2d = render_2d(escena_dict)
    assert isinstance(fig_2d, go.Figure)
    
    # 5. Test de render_2d_shapely.py y render_2d_shapely_automatico_regex
    escena_shapely = datos_to_shapely(data_builded)
    assert isinstance(escena_shapely, dict)
    
    fig_2d_shapely = render_2d_shapely(escena_shapely)
    assert isinstance(fig_2d_shapely, go.Figure)
    
    graficos_por_nivel = render_2d_shapely_automatico_regex(escena_shapely)
    assert isinstance(graficos_por_nivel, dict)
    for nivel, fig_nivel in graficos_por_nivel.items():
        assert isinstance(fig_nivel, go.Figure)
