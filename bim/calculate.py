def calcular_desplazamiento_x(largos_habitaciones: list, e_muro: float, largo_cuadrante: float, borde: str = "izquierdo") -> float:
    """
    Calcula el desplazamiento exacto en el eje X para posicionar un bloque
    en el extremo 'izquierdo' o 'derecho' dentro de una lógica no-centrada (origen en 0,0).
    """
    # 1. Calculamos el largo total real que ocupará el bloque con todos sus muros
    largo_total_bloque = sum(largos_habitaciones) + (e_muro * (len(largos_habitaciones) + 1))

    # 2. Aplicamos las fórmulas en base al cero absoluto de la esquina izquierda
    if borde.lower() == "izquierdo":
        # Arranca directo en el origen del cuadrante
        return 0.0
    elif borde.lower() == "derecho":
        # Se pega al extremo derecho restando el largo total del bloque
        return largo_cuadrante - largo_total_bloque
    else:
        raise ValueError("El parámetro 'borde' debe ser 'izquierdo' o 'derecho'")
    
def calcular_desplazamiento_y(ancho_hab: float, e_muro: float, ancho_cuadrante: float, borde: str = "inferior") -> float:
    """
    Calcula el desplazamiento exacto en el eje Y para posicionar un bloque
    en el extremo 'inferior' o 'superior' dentro de una lógica no-centrada (origen en 0,0).
    """
    # 1. Calculamos el ancho total real del bloque (habitación + sus 2 muros perimetrales)
    ancho_total_bloque = ancho_hab

    # 2. Aplicamos las fórmulas en base al cero absoluto de la esquina inferior-izquierda
    if borde.lower() == "inferior":
        # Arranca directo en la base del cuadrante
        return 0.0
    elif borde.lower() == "superior":
        # Se pega al techo restando el espacio que ocupa el bloque completo
        return ancho_cuadrante - ancho_total_bloque
    else:
        raise ValueError("El parámetro 'borde' debe ser 'inferior' o 'superior'")
    

def calcular_rango_centrado(rango_contenedor: list, largo_elemento: float) -> list:
    """
    Recibe un rango [inicio, fin] del contenedor y el largo del elemento a centrar.
    Retorna una lista con el nuevo [inicio, fin] del elemento perfectamente centrado.
    """
    init_contenedor, end_contenedor = rango_contenedor

    # 1. Calcular el espacio total disponible en el contenedor
    ancho_contenedor = abs(end_contenedor - init_contenedor)

    # 2. Calcular el margen que debe quedar a cada lado
    margen = (ancho_contenedor - largo_elemento) / 2

    # 3. El nuevo inicio es el inicio del contenedor más el margen
    nuevo_init = init_contenedor + margen

    # 4. El nuevo fin es el nuevo inicio más el largo del elemento
    nuevo_end = nuevo_init + largo_elemento

    return [round(nuevo_init, 2), round(nuevo_end, 2)]