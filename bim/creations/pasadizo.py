from bim.capas import FactoryCapas
from bim.config_proyect import CONFIG_PROYECTO
import cadquery as cq

def create_corridor_slab(
    ensamblaje,
    pos_x: list,       # Rango [x_init, x_end] -> ej: [5, 12]
    pos_y: list,       # Rango [y_init, y_end] -> ej: [0, 2.4]
    sufijo_nombre: str,
    nivel: int = 1,
    factory_capas : FactoryCapas = None
):
    """
    Construye la losa de piso para un pasadizo basada en rangos absolutos [inicio, fin].
    Ubicada desde Z = 0 (relativo al nivel) con un grosor fijo de 0.10 metros.
    """
    altura_piso = CONFIG_PROYECTO['alto_nivel']

    # Grosor fijo solicitado para la base del piso
    grosor_losa = 0.10

    # Cálculo del desfase de altura por nivel:
    # Nivel 1: 0.0m | Nivel 2: 1 * altura_piso | etc.
    desfase_z = (nivel - 1) * altura_piso

    # 1. Calcular dimensiones netas en X e Y
    x_init, x_end = pos_x
    y_init, y_end = pos_y

    largo_pasadizo = abs(x_end - x_init)
    ancho_pasadizo = abs(y_end - y_init)

    # 2. Calcular los centros geométricos exactos
    centro_x = (x_init + x_end) / 2
    centro_y = (y_init + y_end) / 2

    # El centro en Z se posiciona para que la cara inferior de la losa toque el cero del nivel actual
    centro_z = (grosor_losa / 2) + desfase_z

    # 3. Crear el volumen sólido de la losa
    losa_pasadizo = (
        cq.Workplane("XY")
        .box(largo_pasadizo, ancho_pasadizo, grosor_losa)
        .translate((centro_x, centro_y, centro_z))
    )

    # 4. Agregar directamente al ensamblaje del proyecto
    name_e = f"Losa Pasadizo {sufijo_nombre} - Nivel {nivel}"
    ensamblaje.add(losa_pasadizo, name=name_e)
    factory_capas.add_in_capa_auto(losa_pasadizo, nivel=nivel, name=name_e)