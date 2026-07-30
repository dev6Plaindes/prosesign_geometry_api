def obtener_dimensiones_cuadrante(cuadrante_normalizado):
    """
    Toma los vértices del cuadrante ya normalizados y calcula su largo (X) y ancho (Y).
    Asume que el cuadrante inicia en (0, 0).
    """
    xs = [v[0] for v in cuadrante_normalizado]
    ys = [v[1] for v in cuadrante_normalizado]
    
    # Al estar normalizado en (0,0), el valor máximo es directamente la longitud del lado
    largo = max(xs) - min(xs)
    ancho = max(ys) - min(ys)
    
    return largo, ancho