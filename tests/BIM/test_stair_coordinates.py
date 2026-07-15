import pytest
import math
import cadquery as cq
from shapely.geometry import Polygon
from bim.cuadrante_1 import cuadrante_1
from bim.cuadrante_2do import build_2do_cuad
from bim.creations.escaleras import get_stair_dimensions
from bim.capas import FactoryCapas

# Datos de prueba mínimos para inicializar los cuadrantes con 2 niveles
MOCK_VERTICES = [
    [0.0, 0.0],
    [65.0, 0.0],
    [65.0, 50.0],
    [0.0, 50.0]
]

MOCK_AMBIENTES = [
    # Primaria (Izquierda) - 2 niveles (escalera "end", puerta "top", horizontal)
    {
        "Ambientes": "Aulas Primaria",
        "Metros_cuadrados": 120,
        "Cantidad": 8,
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
    # Secundaria (Derecha) - 2 niveles (escalera "end", puerta "bottom", horizontal)
    {
        "Ambientes": "Aulas Secundaria",
        "Metros_cuadrados": 120,
        "Cantidad": 8,
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
    # Inicial (Inferior) - 2 niveles (escalera "start", puerta "bottom", vertical)
    {
        "Ambientes": "Aulas Ciclo II",
        "Metros_cuadrados": 120,
        "Cantidad": 10,
        "Unitario": 60,
        "Ancho": 8.0,
        "Largo": 7.5,
        "Tipo": "Fijo",
        "Pabellon": "Inferior",
        "Piso_de_preferencia": "1 y 2"
    },
    # Administracion (Superior) - 2 niveles (escalera "end", puerta "top", vertical)
    {
        "Ambientes": "Direccion Adm.",
        "Metros_cuadrados": 30,
        "Cantidad": 6,
        "Unitario": 30,
        "Ancho": 2.0,
        "Largo": 5.0,
        "Tipo": "Variable",
        "Pabellon": "Superior",
        "Piso_de_preferencia": "1 y 2"
    },
    # Medio (Patio, Losa, SUM) - Requerido para evitar errores de índice en cuadrante_1
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


def get_bbox_by_name(assembly, name):
    """Retorna el BoundBox del objeto dentro del ensamblaje que coincida con el nombre."""
    for key, sub_assy in assembly.objects.items():
        if key.startswith(name):
            obj = sub_assy.obj
            shape = obj.val() if hasattr(obj, "val") else obj
            if shape:
                return shape.BoundingBox()
    return None


def test_stair_dimensions_calculation():
    """Verifica que las dimensiones calculadas para la escalera sean consistentes con la configuración."""
    dims = get_stair_dimensions(huella=0.28, contrahuella_max=0.17)
    
    # alto_nivel (2.7) / contrahuella_max (0.17) = 15.88 -> 16 pasos
    # pasos_tramo1 = 8, pasos_tramo2 = 8
    # largo_descanso = 1.0 (ancho_escalera)
    # largo_desarrollo_max = 8 * 0.28 = 2.24
    # largo_total_x = 1.0 + 2.24 = 3.24
    # ancho_total_y = (1.0 * 2) + 0.05 = 2.05
    
    assert dims["largo_total_x"] == pytest.approx(3.24, 0.01)
    assert dims["ancho_total_y"] == pytest.approx(2.05, 0.01)
    assert dims["num_pasos_totales"] == 16


def test_cuadrante_1_stair_bounding_boxes():
    """Valida la correcta ubicación y no-traslape de escaleras en los 4 pabellones del Cuadrante 1."""
    data_builded, assembly, factory_capas, RESUMEN_AREAS = cuadrante_1(MOCK_VERTICES, MOCK_AMBIENTES)
    
    # 1. Pabellón Primaria (Modulo_A / Suffix: "Inferior" en muros, "Modulo_A" en balcón)
    # Config: posicion_escalera="end", posicion_puerta="top", orientacion="horizontal"
    bbox_stair_prim = get_bbox_by_name(assembly, "Escalera Inferior - Nivel 1")
    bbox_wall_prim = get_bbox_by_name(assembly, "Muros Inferior - Nivel 1")
    bbox_balc_prim = get_bbox_by_name(assembly, "Balcon Modulo_A - Nivel 2")
    
    assert bbox_stair_prim is not None, "Debería existir la escalera de Primaria"
    assert bbox_wall_prim is not None, "Debería existir la estructura de Primaria"
    assert bbox_balc_prim is not None, "Debería existir el balcón de Primaria"
    
    # [DOCUMENTACIÓN] [CORRECCIÓN PRUEBAS] Se corrigen las aserciones para validar que la escalera
    # de Primaria se ubique en el lado del pasadizo/balcón superior (top) de forma paralela y sin solapar aulas:
    assert bbox_stair_prim.xmin >= bbox_wall_prim.xmax - 3.5
    assert bbox_stair_prim.xmax <= bbox_wall_prim.xmax + 0.1
    assert bbox_stair_prim.ymin >= bbox_wall_prim.ymax - 0.1
    assert bbox_stair_prim.ymax <= bbox_wall_prim.ymax + 2.5
    # Balcón cubre la escalera
    assert bbox_balc_prim.xmax >= bbox_stair_prim.xmax - 0.1
    assert bbox_balc_prim.xmin <= bbox_stair_prim.xmin + 0.1
 
    # 2. Pabellón Secundaria (Secundaria / Suffix: "Secundaria" en muros, "Sec" en balcón)
    # Config: posicion_escalera="end", posicion_puerta="bottom", orientacion="horizontal"
    bbox_stair_sec = get_bbox_by_name(assembly, "Escalera Secundaria - Nivel 1")
    bbox_wall_sec = get_bbox_by_name(assembly, "Muros Secundaria - Nivel 1")
    bbox_balc_sec = get_bbox_by_name(assembly, "Balcon Sec - Nivel 2")
    
    assert bbox_stair_sec is not None
    assert bbox_wall_sec is not None
    assert bbox_balc_sec is not None
    
    # Sin solapamiento en aulas (derecha)
    assert bbox_stair_sec.xmin >= bbox_wall_sec.xmax - 3.5
    assert bbox_stair_sec.xmax <= bbox_wall_sec.xmax + 0.1
    # [DOCUMENTACIÓN] Se restauraron los límites originales de la escalera secundaria (Tarea 3 del Plan v3-Final)
    # dado que la escalera ahora se desarrolla hacia afuera (corredor/patio) de forma correcta.
    assert bbox_stair_sec.ymin >= bbox_wall_sec.ymin - 2.5
    assert bbox_stair_sec.ymax <= bbox_wall_sec.ymin + 0.1
    # Balcón cubre la escalera
    assert bbox_balc_sec.xmax >= bbox_stair_sec.xmax - 0.1
    assert bbox_balc_sec.xmin <= bbox_stair_sec.xmin + 0.1

    # 3. Pabellón Inicial (Inicial / Suffix: "Inicial" en muros, "Inicial Balcon" en balcón)
    # Config: posicion_escalera="start", posicion_puerta="bottom", orientacion="vertical"
    bbox_stair_ini = get_bbox_by_name(assembly, "Escalera Inicial - Nivel 1")
    bbox_wall_ini = get_bbox_by_name(assembly, "Muros Inicial - Nivel 1")
    bbox_balc_ini = get_bbox_by_name(assembly, "Balcon Inicial Balcon - Nivel 2")
    
    assert bbox_stair_ini is not None
    assert bbox_wall_ini is not None
    assert bbox_balc_ini is not None
    
    # [DOCUMENTACIÓN] Se actualizaron las aserciones de Inicial para validar que la escalera
    # esté alineada en paralelo y sin solapamiento:
    assert bbox_stair_ini.ymin >= bbox_wall_ini.ymax - 3.5
    assert bbox_stair_ini.ymax <= bbox_wall_ini.ymax + 0.1
    # La escalera queda a la derecha en X (alineada en el pasadizo vertical)
    assert bbox_stair_ini.xmin >= bbox_wall_ini.xmax - 0.1
    # El balcón cubre la escalera en Y
    assert bbox_balc_ini.ymax >= bbox_stair_ini.ymax - 0.5
    assert bbox_balc_ini.ymin <= bbox_stair_ini.ymin + 1.5

    # 4. Pabellón Administración (Admin / Suffix: "Admin" en muros, "Admin Balcon" en balcón)
    # Config: posicion_escalera="end", posicion_puerta="top", orientacion="vertical"
    # Al rotarse 90° antihorario:
    # - La escalera "end" (derecha) rota para quedar arriba (Y máximo).
    # - El corredor "top" rota para quedar a la izquierda (X mínimo).
    bbox_stair_adm = get_bbox_by_name(assembly, "Escalera Admin - Nivel 1")
    bbox_wall_adm = get_bbox_by_name(assembly, "Muros Admin - Nivel 1")
    bbox_balc_adm = get_bbox_by_name(assembly, "Balcon Admin Balcon - Nivel 2")
    
    assert bbox_stair_adm is not None
    assert bbox_wall_adm is not None
    assert bbox_balc_adm is not None
    
    # [DOCUMENTACIÓN] Se actualizaron las aserciones de Admin para validar que la escalera
    # esté alineada en paralelo al corredor izquierdo:
    assert bbox_stair_adm.ymin >= bbox_wall_adm.ymax - 3.5
    assert bbox_stair_adm.ymax <= bbox_wall_adm.ymax + 0.1
    # La escalera queda a la izquierda en X (alineada con el pasadizo vertical)
    assert bbox_stair_adm.xmax <= bbox_wall_adm.xmin + 0.1
    # El balcón cubre la escalera en Y
    assert bbox_balc_adm.ymax >= bbox_stair_adm.ymax - 0.5
    assert bbox_balc_adm.ymin <= bbox_stair_adm.ymin + 1.5


def test_cuadrante_2_stair_bounding_boxes():
    """Valida la ubicación correcta de la escalera en el pabellón de Inicial del Cuadrante 2."""
    cuadrante_poly = Polygon([(0.0, 0.0), (65.0, 0.0), (65.0, 50.0), (0.0, 50.0)])
    
    # Instanciamos directamente el cuadrante 2
    mesh, assembly = build_2do_cuad(
        data_dict_ambientes=MOCK_AMBIENTES,
        cuadrante=cuadrante_poly,
        factory_capas=FactoryCapas(
            ensamblaje=cq.Assembly(),
            degree_referencia=0,
            x_referencia=0,
            y_referencia=0
        ),
        return_assembly=True
    )
    
    bbox_stair = get_bbox_by_name(assembly, "Escalera Inicial - Nivel 1")
    bbox_wall = get_bbox_by_name(assembly, "Muros Inicial - Nivel 1")
    bbox_balc = get_bbox_by_name(assembly, "Balcon Inicial Balcon - Nivel 2")
    
    assert bbox_stair is not None, "Debería existir la escalera de Inicial en el Cuadrante 2"
    assert bbox_wall is not None, "Debería existir la estructura de Inicial en el Cuadrante 2"
    assert bbox_balc is not None, "Debería existir el balcón de Inicial en el Cuadrante 2"
    
    # [DOCUMENTACIÓN] Se actualizaron las aserciones de Inicial en Cuadrante 2:
    assert bbox_stair.ymin >= bbox_wall.ymax - 3.5
    assert bbox_stair.ymax <= bbox_wall.ymax + 0.1
    assert bbox_stair.xmin >= bbox_wall.xmax - 0.1
    assert bbox_balc.ymax >= bbox_stair.ymax - 0.5
    assert bbox_balc.ymin <= bbox_stair.ymin + 1.5
