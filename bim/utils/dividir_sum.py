from shapely.geometry import LineString, Polygon
from shapely.ops import split

from shapely.geometry import LineString, Polygon
from shapely.ops import split


def ajustar_dividir_sum(
    space_sum: Polygon,
    sum_ambiente: Polygon,
    largo_orig: float,
    ancho_orig: float,
    min_ancho_viable: float = 2.0,  # Ningún ambiente puede medir menos de 2 metros
    max_divisiones: int = 5,
) -> list[tuple[Polygon, float, float]]:
    """Devuelve una lista de tuplas: (sub_polygon, nuevo_largo, nuevo_ancho) Si

    un pedazo no cabe o mide menos de min_ancho_viable, no se incluye.
    """
    por_procesar = [(sum_ambiente, largo_orig, ancho_orig)]
    resultado_final = []
    intento = 0

    while por_procesar and intento < max_divisiones:
        intento += 1
        siguiente_ronda = []

        for poly, l_curr, a_curr in por_procesar:
            # 1. Si cabe perfectamente en el contenedor
            if poly.within(space_sum):
                resultado_final.append((poly, l_curr, a_curr))
            else:
                # 2. Cortar a la mitad por el lado más largo
                minx, miny, maxx, maxy = poly.bounds
                ancho_geom = maxx - minx
                alto_geom = maxy - miny

                if alto_geom >= ancho_geom:
                    # Corte horizontal -> divide el Largo a la mitad
                    mid_y = (miny + maxy) / 2.0
                    linea_corte = LineString(
                        [(minx - 1, mid_y), (maxx + 1, mid_y)]
                    )
                    nuevo_largo = l_curr / 2.0
                    nuevo_ancho = a_curr
                else:
                    # Corte vertical -> divide el Ancho a la mitad
                    mid_x = (minx + maxx) / 2.0
                    linea_corte = LineString(
                        [(mid_x, miny - 1), (mid_x, maxy + 1)]
                    )
                    nuevo_largo = l_curr
                    nuevo_ancho = a_curr / 2.0

                geometrias = split(poly, linea_corte)
                partes = [
                    g for g in geometrias.geoms if isinstance(g, Polygon)
                ]

                if len(partes) <= 1:
                    resultado_final.append((poly, l_curr, a_curr))
                else:
                    for p in partes:
                        siguiente_ronda.append((p, nuevo_largo, nuevo_ancho))

        por_procesar = siguiente_ronda

    resultado_final.extend(por_procesar)

    # 3. FILTRO RIGUROSO DE SEGURIDAD
    # Solo conservar fragmentos que estén dentro de space_sum y cumplan dimensiones mínimas
    validos = []
    for p, l, a in resultado_final:
        minx_p, miny_p, maxx_p, maxy_p = p.bounds
        ancho_real = maxx_p - minx_p
        alto_real = maxy_p - miny_p

        # Descarta piezas que no entran o que miden menos de min_ancho_viable (ej. franjas de 0.32m)
        if (
            p.within(space_sum)
            and ancho_real >= min_ancho_viable
            and alto_real >= min_ancho_viable
        ):
            validos.append((p, l, a))

    return validos
