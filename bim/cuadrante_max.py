import numpy as np
from shapely.geometry import Polygon


def get_candidate_angles(polygon):
    """Extrae los ángulos de los linderos del terreno para usarlos como base."""
    coords = list(polygon.exterior.coords)
    angles = []
    for i in range(len(coords) - 1):
        p1 = coords[i]
        p2 = coords[i + 1]
        # Calcular ángulo en grados
        angle = np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
        angles.append(angle % 90)  # Simplificar a cuadrante de 90°
    return list(set(angles))


def find_max_rect_for_angle(polygon, angle, cell_size):
    """Calcula el rectángulo máximo posible dentro del polígono para un ángulo dado."""
    # Rotar el polígono para alinearlo con los ejes X e Y
    rotated_poly = shapely.affinity.rotate(polygon, -angle, origin="center")

    # Obtener la caja contenedora del polígono rotado
    minx, miny, maxx, maxy = rotated_poly.bounds

    # Crear una grilla de puntos dentro de la caja contenedora
    x_coords = np.arange(minx, maxx, cell_size)
    y_coords = np.arange(miny, maxy, cell_size)

    best_area = 0
    best_rect = None

    # Buscamos combinaciones de esquinas válidas que estén CIENTOS por CIENTO dentro del polígono
    # Nota: Este enfoque de grilla busca el mayor rectángulo alineado a los ejes
    for i, x1 in enumerate(x_coords):
        for x2 in x_coords[i + 1 :]:
            for j, y1 in enumerate(y_coords):
                for y2 in y_coords[j + 1 :]:
                    # Crear el rectángulo candidato
                    rect_candidate = Polygon(
                        [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                    )

                    # Validar si cabe por completo dentro del terreno irregular
                    if rotated_poly.contains(rect_candidate):
                        area = rect_candidate.area
                        if area > best_area:
                            best_area = area
                            best_rect = rect_candidate

    # Si encontramos uno, lo rotamos de vuelta a la posición original del terreno
    if best_rect:
        original_rect = shapely.affinity.rotate(
            best_rect, angle, origin="center"
        )
        return list(original_rect.exterior.coords)[:4], best_area

    return None, 0


import shapely.affinity


def find_best_rectangle(polygon, cell_size_coarse=0.5, cell_size_fine=0.2):
    best_rect = None
    best_area = 0
    best_angle = 0

    # 🔥 ángulos inteligentes
    base_angles = get_candidate_angles(polygon)

    # 🔥 refinamiento fino
    angles = []
    for a in base_angles:
        angles.extend([a + d for d in np.linspace(-3, 3, 7)])

    # --- PRIMERA PASADA (rápida) ---
    for angle in angles:
        rect, area = find_max_rect_for_angle(polygon, angle, cell_size_coarse)

        if rect and area > best_area:
            best_rect = rect
            best_area = area
            best_angle = angle

    # --- SEGUNDA PASADA (precisa 🔥) ---
    fine_angles = [best_angle + d for d in np.linspace(-1, 1, 5)]

    for angle in fine_angles:
        rect, area = find_max_rect_for_angle(polygon, angle, cell_size_fine)

        if rect and area > best_area:
            best_rect = rect
            best_area = area
            best_angle = angle

    return best_rect, best_area, best_angle


