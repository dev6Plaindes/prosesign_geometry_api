import numpy as np
from shapely.geometry import box, Polygon
from shapely import affinity
from rasterio import features
from affine import Affine

def maximal_rectangle(matrix):
    if not matrix.any():
        return 0, (0, 0, 0, 0)

    max_area = 0
    max_rect = (0, 0, 0, 0)
    dp = [0] * len(matrix[0])

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            dp[j] = dp[j] + 1 if matrix[i][j] == 1 else 0

        stack = []
        for j in range(len(dp) + 1):
            while stack and (j == len(dp) or dp[j] < dp[stack[-1]]):
                height = dp[stack.pop()]
                width = j if not stack else j - stack[-1] - 1
                area = height * width
                if area > max_area:
                    max_area = area
                    top_left_j = stack[-1] + 1 if stack else 0
                    top_left_i = i - height + 1
                    max_rect = (top_left_i, top_left_j, height, width)
            stack.append(j)
    return max_area, max_rect

def find_max_rect_for_angle_fast(polygon, angle_deg, cell_size=1.0):
    # 1. Definir el centro para la rotación
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    origin = ((minx + maxx) / 2, (miny + maxy) / 2)

    # 2. Rotar el POLÍGONO completo (operación única)
    # Aplicamos un buffer negativo pequeño (-0.01) para asegurar que el
    # rectángulo final esté 100% dentro y no sobrepase por errores decimales.
    poly_rotated = affinity.rotate(polygon.buffer(-0.01), -angle_deg, origin=origin)

    # 3. Preparar la rasterización
    rminx, rminy, rmaxx, rmaxy = poly_rotated.bounds
    width = int(np.ceil((rmaxx - rminx) / cell_size))
    height = int(np.ceil((rmaxy - rminy) / cell_size))

    if width <= 0 or height <= 0:
        return None, 0, angle_deg

    # Transformación Affine para mapear coordenadas a la matriz
    transform = Affine.translation(rminx, rminy) * Affine.scale(cell_size, cell_size)

    # RASTERIZACIÓN VECTORIZADA (Sustituye tus bucles for i, for j)
    grid = features.rasterize(
        [poly_rotated],
        out_shape=(height, width),
        transform=transform,
        fill=0,
        default_value=1,
        dtype=np.uint8
    )

    # 4. Usar tu función maximal_rectangle (que ya es eficiente)
    area_px, (i_start, j_start, h_px, w_px) = maximal_rectangle(grid)

    if area_px == 0:
        return None, 0, angle_deg

    # 5. Reconstruir el rectángulo en el plano rotado
    x0 = j_start * cell_size + rminx
    x1 = (j_start + w_px) * cell_size + rminx
    y0 = i_start * cell_size + rminy
    y1 = (i_start + h_px) * cell_size + rminy

    rect_unrotated = box(x0, y0, x1, y1)

    # 6. Rotar el rectángulo de vuelta a la orientación original
    rect_final = affinity.rotate(rect_unrotated, angle_deg, origin=origin)

    # El área real es proporcional al tamaño de celda
    area_m2 = area_px * (cell_size ** 2)

    return rect_final, area_m2, angle_deg
