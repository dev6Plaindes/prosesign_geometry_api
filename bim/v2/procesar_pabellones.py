from dev.build.block import new_block
from dev.utils.tools import div_logic


def _procesar_layout_multiples_pabellones(
    cuadrante_shapely, eje_principal, eje_secundario, ancho_aula, ancho_pasadiso, mi_modelo, factory_capas
):
    """
    Procesa la división en cruz para 3 o más pabellones.
    """
    print("📐 Aplicando división estándar en cruz para 3 o más pabellones.")
    medidas_5_tramos = [ancho_aula, ancho_pasadiso, "auto", ancho_pasadiso, ancho_aula]

    # División en eje principal (Lados: Izquierda a Derecha)
    tramos_poligonos = div_logic(
        medidas_5_tramos, cuadrante_shapely, eje_div=eje_principal
    )

    print("EJESS", "PRINCIPAL:", eje_principal)
    print("ANCHO AULA", ancho_aula)
    print("ANCHO PASADISO", ancho_pasadiso)

    # Izquierda -> Primaria | Derecha -> Secundaria
    primaria, pasadizo_primaria, space_centro_1, pasadizo_secundaria, secundaria = (
        tramos_poligonos
    )

    # División en eje secundario (Extremos: Arriba a Abajo)
    tramos_poligonos_2 = div_logic(
        medidas_5_tramos, space_centro_1, eje_div=eje_secundario
    )

    if len(tramos_poligonos_2) == 5:
        # Arriba (0) -> Admin | Abajo (4) -> Inicial
        admin, pasadizo_admin, space_centro_2, pasadizo_inicial, inicial = (
            tramos_poligonos_2
        )

    else:
        admin, pasadizo_admin, space_centro_2, pasadizo_inicial, inicial = (
            None,
            None,
            space_centro_1,
            None,
            None,
        )

    slots = {
        "lateral_1": {
            "polygon": primaria,
            "pasadizo": pasadizo_primaria,
        },  # Izquierda (Primaria)
        "lateral_2": {
            "polygon": secundaria,
            "pasadizo": pasadizo_secundaria,
        },  # Derecha (Secundaria)
        "extremo_1": {"polygon": admin, "pasadizo": pasadizo_admin},  # Superior (Admin)
        "extremo_2": {
            "polygon": inicial,
            "pasadizo": pasadizo_inicial,
        },  # Inferior (Inicial)
    }

    return slots, space_centro_2
