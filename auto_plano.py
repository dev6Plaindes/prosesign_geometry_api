import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from utils.max_rectangle import find_max_rect_for_angle_fast, maximal_rectangle

utm_coords = [
    (298249.88, 8944243.21), (298239.13, 8944216.23), (298246.52, 8944212.73),
    (298237.24, 8944196.27), (298221.97, 8944175.47), (298201.99, 8944147.67),
    (298116.28, 8944120.74), (298110.09, 8944126.65), (298107.6, 8944132.77),
    (298085.62, 8944173.45), (298075.83, 8944178.85), (298068.85, 8944182.38),
    (298060.01, 8944203.73), (298061.33, 8944209.77), (298060.91, 8944217.03),
    (298060.56, 8944227.91), (298069.0, 8944246.04), (298077.7, 8944263.87),
    (298103.82, 8944243.79), (298130.34, 8944225.56), (298137.17, 8944238.64),
    (298144.82, 8944253.99), (298148.72, 8944261.79), (298157.79, 8944256.8),
    (298168.41, 8944251.53), (298173.46, 8944261.73), (298177.03, 8944269.84),
    (298179.89, 8944276.41), (298213.04, 8944258.67), (298236.1, 8944248.56),
    (298249.88, 8944243.21)
]

# Convertimos a una matriz de NumPy
coords_matrix = np.array(utm_coords)

# Separamos las columnas
x_utm = coords_matrix[:, 0]
y_utm = coords_matrix[:, 1]


# 1. Trasladar al origen (Normalización)
x0, y0 = x_utm.min(), y_utm.min()
x = x_utm - x0
y = y_utm - y0

# 2. Crear el objeto Polygon
# Nota: Shapely cierra el polígono automáticamente si pasas la lista de puntos
coords = list(zip(x, y))
poly = Polygon(coords)

# 3. Obtener propiedades
area_poly = poly.area
perimetro = poly.length
centroide = poly.centroid

px, py = poly.exterior.xy
plt.figure(figsize=(6,6))
plt.plot(px, py, marker='o')
plt.fill(px, py, alpha=0.3, label=f"Polígono ({area_poly:.2f} m²)")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()

# --- BUCLE PRINCIPAL OPTIMIZADO ---
polygon = Polygon(utm_coords)
angles = np.arange(0, 180, 5)
best_rect, best_area, best_angle = None, 0, 0

for angle in angles:
    rect, area, _ = find_max_rect_for_angle_fast(polygon, angle, cell_size=0.5)
    if rect and area > best_area:
        best_rect, best_area, best_angle = rect, area, angle

print(f"Mejor área: {best_area:.2f} m² en ángulo {best_angle}°")