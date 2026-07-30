import cadquery as cq

# =====================================================================
# 1. FUNCIÓN DE NORMALIZACIÓN GENERAL
# =====================================================================
def normalizar_datos_terreno(cuadrante_raw, terreno_raw):
    """
    Normaliza el cuadrante para que su esquina inferior izquierda sea (0, 0).
    Aplica ese mismo origen al terreno real.
    """
    # 1. El Punto Cero se calcula SOLAMENTE con el cuadrante máximo
    xs_cuadrante = [v[0] for v in cuadrante_raw]
    ys_cuadrante = [v[1] for v in cuadrante_raw]
    
    origen_x = min(xs_cuadrante)
    origen_y = min(ys_cuadrante)

    # 2. Normalizar el cuadrante (empezará exactamente en 0, 0)
    cuadrante_normalizado = [
        (x - origen_x, y - origen_y) for x, y in cuadrante_raw
    ]

    # 3. Normalizar el terreno usando el mismo origen del cuadrante
    # Si algún vértice es menor al mínimo del cuadrante, dará un valor negativo (ej. -14.2)
    terreno_normalizado = [
        (v["x"] - origen_x, v["y"] - origen_y) for v in terreno_raw
    ]

    return cuadrante_normalizado, terreno_normalizado, (origen_x, origen_y)