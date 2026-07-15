import cadquery as cq

def build_pupitre_silla():
    """Genera un pupitre combinado con una silla en orientación local facing +Y."""
    # Mesa
    mesa = cq.Workplane("XY").box(0.8, 0.5, 0.03).translate((0, 0, 0.7))
    # Patas de mesa
    for dx in [-0.36, 0.36]:
        for dy in [-0.22, 0.22]:
            pata = cq.Workplane("XY").cylinder(0.7, 0.02).translate((dx, dy, 0.35))
            mesa = mesa.union(pata)
    
    # Silla asiento (detrás de la mesa, mirando hacia ella)
    asiento = cq.Workplane("XY").box(0.35, 0.35, 0.03).translate((0, -0.45, 0.42))
    # Patas de silla
    for dx in [-0.15, 0.15]:
        for dy in [-0.60, -0.30]:
            pata_s = cq.Workplane("XY").cylinder(0.42, 0.015).translate((dx, dy, 0.21))
            asiento = asiento.union(pata_s)
    
    # Respaldo de silla
    respaldo = cq.Workplane("XY").box(0.35, 0.03, 0.35).translate((0, -0.61, 0.6))
    
    # Combinar todo en un solo compuesto
    pupitre_silla = mesa.union(asiento).union(respaldo)
    return pupitre_silla

def build_pizarra():
    """Genera una pizarra para colocar en la pared del aula."""
    return cq.Workplane("XY").box(3.0, 0.02, 1.2).translate((0, 0, 1.4))

def build_profesor_desk():
    """Genera el escritorio del docente."""
    mesa = cq.Workplane("XY").box(1.2, 0.6, 0.03).translate((0, 0, 0.75))
    for dx in [-0.55, 0.55]:
        for dy in [-0.25, 0.25]:
            pata = cq.Workplane("XY").cylinder(0.75, 0.025).translate((dx, dy, 0.375))
            mesa = mesa.union(pata)
    return mesa

def inyectar_mobiliario_aulas(
    ensamblaje,
    centro_x: float,
    centro_y: float,
    l_hab: float,
    ancho_interior: float,
    desfase_z: float,
    nivel: int,
    orientacion: str,
    desplazamiento_x: float,
    desplazamiento_y: float,
    sufijo_nombre: str,
    idx_aula: int,
    factory_capas=None
):
    """
    Distribuye pupitres de estudiantes, pizarra y mesa del docente en una cuadrícula.
    Alinea y rota el mobiliario adecuadamente según la orientación del bloque.
    """
    # Generar compuestos de mobiliario local
    pupitre_comp = build_pupitre_silla()
    pizarra_comp = build_pizarra()
    profesor_comp = build_profesor_desk()
    
    puntos_mobiliario = []
    
    # 1. Pizarra en la pared del fondo (frente a las carpetas, a +Y local)
    pos_pizarra = pizarra_comp.translate((
        centro_x, 
        centro_y + (ancho_interior / 2) - 0.05, 
        desfase_z
    ))
    puntos_mobiliario.append((pos_pizarra, f"Mobiliario Pizarra - {sufijo_nombre} - Aula {idx_aula} - Nivel {nivel}"))

    # 2. Escritorio del profesor al frente
    pos_profe = profesor_comp.translate((
        centro_x, 
        centro_y + (ancho_interior / 2) - 1.2, 
        desfase_z
    ))
    puntos_mobiliario.append((pos_profe, f"Mobiliario Escritorio Profesor - {sufijo_nombre} - Aula {idx_aula} - Nivel {nivel}"))

    # 3. Cuadrícula de carpetas de alumnos
    # Espacio útil para alumnos: descontando la zona de circulación del docente al frente
    espacio_x_util = l_hab - 1.0
    espacio_y_util = ancho_interior - 2.0
    
    num_cols = max(1, int(espacio_x_util / 1.3))
    num_rows = max(1, int(espacio_y_util / 1.4))
    
    for r in range(num_rows):
        for c in range(num_cols):
            # Centrado en X
            x_loc = (c - (num_cols - 1) / 2.0) * 1.3
            # Distribución en Y desde atrás hacia adelante
            y_loc = -(ancho_interior / 2.0) + 0.8 + (r * 1.4)
            
            # Trasladar pupitre a su coordenada global
            pupitre_instancia = pupitre_comp.translate((
                centro_x + x_loc,
                centro_y + y_loc,
                desfase_z
            ))
            puntos_mobiliario.append((
                pupitre_instancia, 
                f"Mobiliario Pupitre C{c}R{r} - {sufijo_nombre} - Aula {idx_aula} - Nivel {nivel}"
            ))

    # 4. Aplicar transformaciones de rotación si la orientación es vertical
    for solido, nombre in puntos_mobiliario:
        if orientacion.lower() == "vertical":
            pivote = (desplazamiento_x, desplazamiento_y, 0)
            solido = solido.rotate(pivote, (desplazamiento_x, desplazamiento_y, 1), 90)
            
        # Añadir al ensamblaje raíz
        ensamblaje.add(solido, name=nombre)
        
        # Añadir a la capa para que sea exportado al GLTF
        if factory_capas:
            factory_capas.add_in_capa_auto(
                workplane=solido,
                nivel=nivel,
                name=nombre
            )
