from shapely.geometry import MultiPoint, Point
from shapely import affinity
import math
import copy

def transformar_escena_con_referencia(data, data_cuadrante_real):
    """
    Ubica, traslada y alinea milimétricamente todas las piezas de 'data' 
    en la posición y orientación exacta del cuadrante real de destino.
    """
    # 1. Crear una copia profunda para proteger los datos de entrada
    escena_resultado = copy.deepcopy(data)

    # ==========================================
    # 2. CONSTRUCCIÓN DE POLÍGONOS DE REFERENCIA EN PLANTA
    # ==========================================
    pts_real_2d = [Point(v[0], v[1]) for v in data_cuadrante_real[0]["vertices"]]
    g_real = MultiPoint(pts_real_2d).convex_hull

    # Buscamos la Losa o cuadrante local guía en la data entrante
    pieza_render_local = None
    for pieza in data:
        if "Losa" in pieza["name"] or "cuadrante" in pieza["name"].lower():
            pieza_render_local = pieza
            break

    if pieza_render_local is None:
        pieza_render_local = data[0]

    pts_local_2d = [Point(v[0], v[1]) for v in pieza_render_local["vertices"]]
    g_render_local = MultiPoint(pts_local_2d).convex_hull

    # ==========================================
    # 3. CÁLCULO PRECISO Y ESTABLE DEL ÁNGULO DE ROTACIÓN
    # ==========================================
    def obtener_angulo_orientacion_stable(polygon):
        if hasattr(polygon, "minimum_rotated_polygon"):
            rect_orientado = polygon.minimum_rotated_polygon
        else:
            rect_orientado = polygon.minimum_rotated_rectangle
            
        coords = list(rect_orientado.exterior.coords)[:-1] # Excluimos el punto de cierre
        
        if len(coords) < 4:
            return 0.0
            
        # Para evitar el salto de 90° de Shapely, calculamos el ángulo del lado MÁS LARGO
        # de manera que siempre comparemos magnitudes equivalentes.
        lados = []
        for i in range(4):
            p1 = coords[i]
            p2 = coords[(i + 1) % 4]
            dist = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            ang = math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))
            lados.append((dist, ang))
            
        # Ordenamos por longitud de lado de mayor a menor
        lados.sort(key=lambda x: x[0], reverse=True)
        
        # Devolvemos el ángulo del lado más largo (normalizado entre -90 y 90)
        ang_principal = lados[0][1]
        if ang_principal > 90: ang_principal -= 180
        if ang_principal <= -90: ang_principal += 180
        return ang_principal
    
    ang_real = obtener_angulo_orientacion_stable(g_real)
    ang_local = obtener_angulo_orientacion_stable(g_render_local)
    
    # Restamos las orientaciones para hallar el desfase angular neto
    angulo_necesario = ang_real - ang_local

    # ==========================================
    # 4. PUNTOS DE ANCLAJE (CENTROIDES REALES EN PLANTA)
    # ==========================================
    dest_x, dest_y = g_real.centroid.x, g_real.centroid.y
    orig_x, orig_y = g_render_local.centroid.x, g_render_local.centroid.y

    # El vector de traslación se aplicará DESPUÉS de la rotación
    x_offset = dest_x - orig_x
    y_offset = dest_y - orig_y

    # ==========================================
    # 5. TRANSFORMACIÓN GEOMÉTRICA (3D)
    # ==========================================
    for pieza in escena_resultado:
        
        # --- A. Transformación de la lista de vértices globales ---
        nuevos_vertices = []
        for v in pieza["vertices"]:
            punto = Point(v[0], v[1])
            
            # PASO 1: Rotar en el origen (usando el centroide LOCAL como pivote)
            punto_rotado = affinity.rotate(punto, angulo_necesario, origin=(orig_x, orig_y))
            # PASO 2: Trasladar la pieza ya rotada al destino final
            punto_final = affinity.translate(punto_rotado, xoff=x_offset, yoff=y_offset)
            
            nuevos_vertices.append((round(punto_final.x, 4), round(punto_final.y, 4), v[2]))
        
        pieza["vertices"] = nuevos_vertices

        # --- B. Transformación de la estructura de caras (Faces) ---
        nuevas_caras = []
        for cara in pieza["faces"]:
            nueva_cara = []
            for pt in cara:
                punto = Point(pt[0], pt[1])
                
                # Ejecutamos la misma secuencia matemática correcta: Rotar en Local -> Trasladar
                punto_rotado = affinity.rotate(punto, angulo_necesario, origin=(orig_x, orig_y))
                punto_final = affinity.translate(punto_rotado, xoff=x_offset, yoff=y_offset)
                
                nueva_cara.append((round(punto_final.x, 4), round(punto_final.y, 4), pt[2]))
            nuevas_caras.append(nueva_cara)
            
        pieza["faces"] = nuevas_caras

    return escena_resultado
