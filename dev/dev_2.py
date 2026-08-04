import cadquery as cq
from ocp_vscode import show
from dev.data_test import data_test, ambientes_test
from bim.v2.cuadrante_1_v2 import cuadrante_1_v2

# 1. Obtener datos de prueba
vertices_cuadrante = data_test["vertices_rectangle"]
vertices_terreno = data_test["vertices"]
ambientes = ambientes_test
id_project = 999 # ID de prueba

# 2. Llamar a la función principal que encapsula toda la lógica de construcción
mi_modelo, factory_capas, resumen_areas = cuadrante_1_v2(
    vertices_terreno=vertices_terreno,
    vertices_cuadrante=vertices_cuadrante,
    ambientes=ambientes,
    id_project=id_project
)

# 3. Guardar el modelo 3D resultante en un archivo GLB
mi_modelo.save("pabellon.glb")

# 4. Visualizar el modelo en el visor OCP de VSCode
show(
    mi_modelo,
    alphas=[0.6]
)
