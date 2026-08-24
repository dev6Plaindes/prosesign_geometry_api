from typing import List, Optional, Tuple
import math

from shapely.geometry import Polygon
from shapely import affinity


def distribuir_ambientes(
    polygon: Polygon,
    largos_habitaciones: List[float],
    anchos_habitaciones: Optional[List[float]] = None,
    names_ambientes: Optional[List[str]] = None,
    e_muro: float = 0.0,
) -> List[Tuple[Polygon, str]]:
    """
    Distribuye ambientes dentro de un Polygon y retorna cada geometría
    junto con su nombre.

    El polígono puede estar rotado. La distribución se realiza en un
    sistema local alineado con sus ejes y luego se devuelve a su posición
    original.
    """

    # =========================================================
    # 1. VALIDACIONES
    # =========================================================

    if polygon is None or polygon.is_empty:
        return []

    if not polygon.is_valid:
        raise ValueError("El polygon recibido no es válido.")

    if not largos_habitaciones:
        return []

    if any(largo <= 0 for largo in largos_habitaciones):
        raise ValueError(
            "Todos los largos_habitaciones deben ser mayores que cero."
        )

    if anchos_habitaciones is not None:
        if len(anchos_habitaciones) != len(largos_habitaciones):
            raise ValueError(
                "largos_habitaciones y anchos_habitaciones deben tener "
                "la misma cantidad de elementos."
            )

        if any(ancho <= 0 for ancho in anchos_habitaciones):
            raise ValueError(
                "Todos los anchos_habitaciones deben ser mayores que cero."
            )

    if names_ambientes is not None:
        if len(names_ambientes) != len(largos_habitaciones):
            raise ValueError(
                "names_ambientes y largos_habitaciones deben tener "
                "la misma cantidad de elementos."
            )

    if e_muro < 0:
        raise ValueError("e_muro no puede ser negativo.")

    # =========================================================
    # 2. OBTENER ORIENTACIÓN DEL POLÍGONO
    # =========================================================

    rect = polygon.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)

    lados = []

    for i in range(4):
        p1 = coords[i]
        p2 = coords[i + 1]

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        lados.append({
            "longitud": math.hypot(dx, dy),
            "angulo": math.degrees(math.atan2(dy, dx)),
        })

    eje_1 = lados[0]
    eje_2 = lados[1]

    dim_1 = eje_1["longitud"]
    dim_2 = eje_2["longitud"]

    # =========================================================
    # 3. DETERMINAR ORIENTACIÓN LONGITUDINAL
    # =========================================================

    suma_largos = sum(largos_habitaciones)

    espacio_muross = (
        max(0, len(largos_habitaciones) - 1) * e_muro
    )

    largo_requerido = suma_largos + espacio_muross

    max_ancho = (
        max(anchos_habitaciones)
        if anchos_habitaciones is not None
        else min(dim_1, dim_2)
    )

    orientacion_a = (
        dim_1 >= largo_requerido - 1e-9
        and dim_2 >= max_ancho - 1e-9
    )

    orientacion_b = (
        dim_2 >= largo_requerido - 1e-9
        and dim_1 >= max_ancho - 1e-9
    )

    if not orientacion_a and not orientacion_b:
        raise ValueError(
            f"No es posible distribuir los ambientes.\n"
            f"Largo requerido: {largo_requerido:.2f} m\n"
            f"Ancho requerido: {max_ancho:.2f} m\n"
            f"Dimensiones disponibles: "
            f"{dim_1:.2f} × {dim_2:.2f} m"
        )

    if orientacion_a:
        angulo_local = eje_1["angulo"]
    else:
        angulo_local = eje_2["angulo"]

    # =========================================================
    # 4. TRANSFORMAR A SISTEMA LOCAL
    # =========================================================

    centro = polygon.centroid

    polygon_local = affinity.rotate(
        polygon,
        -angulo_local,
        origin=centro,
    )

    min_x, min_y, max_x, max_y = polygon_local.bounds

    largo_disponible = max_x - min_x
    ancho_disponible = max_y - min_y

    # =========================================================
    # 5. CREAR AMBIENTES
    # =========================================================

    ambientes_locales = []

    cursor_x = min_x

    for idx, largo in enumerate(largos_habitaciones):

        if anchos_habitaciones is None:
            ancho = ancho_disponible
        else:
            ancho = anchos_habitaciones[idx]

        if ancho > ancho_disponible + 1e-9:
            raise ValueError(
                f"El ancho del ambiente {idx + 1} "
                f"({ancho:.2f} m) supera el ancho disponible "
                f"({ancho_disponible:.2f} m)."
            )

        offset_y = (ancho_disponible - ancho) / 2

        y0 = min_y + offset_y
        y1 = y0 + ancho

        ambiente = Polygon([
            (cursor_x, y0),
            (cursor_x + largo, y0),
            (cursor_x + largo, y1),
            (cursor_x, y1),
        ])

        if names_ambientes is not None:
            nombre = names_ambientes[idx]
        else:
            nombre = f"Ambiente_{idx + 1}"

        ambientes_locales.append(
            (ambiente, nombre)
        )

        cursor_x += largo

        if idx < len(largos_habitaciones) - 1:
            cursor_x += e_muro

    # =========================================================
    # 6. RESTAURAR ORIENTACIÓN ORIGINAL
    # =========================================================

    ambientes = []

    for ambiente_local, nombre in ambientes_locales:

        ambiente = affinity.rotate(
            ambiente_local,
            angulo_local,
            origin=centro,
        )

        ambientes.append(
            (ambiente, nombre)
        )

    return ambientes