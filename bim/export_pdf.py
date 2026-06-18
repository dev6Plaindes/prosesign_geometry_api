import re
import cadquery as cq
from PIL import Image

def exportar_niveles_a_pdf(ruta_step="formato_prueba.step", pdf_salida="planos_por_nivel.pdf"):
    """
    Agrupa los componentes de un STEP por niveles, asegurando que los componentes 
    'Base Cuadrante' se repliquen e incluyan en todos los niveles generados.
    """
    # ==========================================
    # Cargar ensamblaje STEP
    # ==========================================
    assy_completo = cq.Assembly.importStep(ruta_step)

    # ==========================================
    # Primer paso: Recolectar bases cuadrante y componentes por nivel
    # ==========================================
    componentes_por_nivel = {}
    bases_cuadrante = []

    for ruta, componente in assy_completo.traverse():
        # Saltar nodo raíz
        if componente.obj is None:
            continue

        nombre_original = componente.name or ""
        nombre = nombre_original.lower()

        # Excluir techos
        if "techo" in nombre:
            # print(f"Componente excluido: {nombre_original}")
            continue

        # Si es una "Base Cuadrante", la guardamos para añadirla a todos los niveles después
        if "base cuadrante" in nombre:
            bases_cuadrante.append(componente)
            continue

        # Buscar "Nivel X"
        match = re.search(r"nivel\s+(\d+)", nombre)
        if not match:
            # print(f"Sin nivel detectado: {nombre_original}")
            continue

        nivel = match.group(1)

        if nivel not in componentes_por_nivel:
            componentes_por_nivel[nivel] = []
        
        componentes_por_nivel[nivel].append(componente)

    # ==========================================
    # Segundo paso: Construir los Assemblies finales de cada nivel
    # ==========================================
    niveles = {}

    for nivel, lista_componentes in componentes_por_nivel.items():
        niveles[nivel] = cq.Assembly(name=f"nivel_{nivel}")

        # 1. Agregar los componentes propios de este nivel
        for comp in lista_componentes:
            niveles[nivel].add(
                comp.obj,
                name=comp.name,
                color=comp.color,
                loc=comp.loc
            )

        # 2. Replicar e integrar todas las "Base Cuadrante" encontradas en este nivel
        for idx, base in enumerate(bases_cuadrante):
            niveles[nivel].add(
                base.obj,
                name=f"{base.name}_ref_nv{nivel}_{idx}",  # Nombre único para evitar colisiones
                color=base.color,
                loc=base.loc
            )

    # ==========================================
    # Configuración de render
    # ==========================================
    render_options = {
        "width": 1200,
        "height": 1200,
        "color_theme": "black_and_white",
        "view": "top",
        "zoom": 1.0,
    }

    # ==========================================
    # Generar PNG por nivel
    # ==========================================
    imagenes_generadas = []

    for nivel in sorted(niveles.keys(), key=int):
        archivo_png = f"nivel_{nivel}.png"
        # print(f"Generando PNG Nivel {nivel}...")

        # Utiliza el método inyectado por tu plugin cadquery_png_plugin
        niveles[nivel].exportPNG(
            file_path=archivo_png,
            options=render_options
        )

        imagenes_generadas.append(archivo_png)

    # print("PNG por niveles generados")

    # ==========================================
    # Crear PDF multipágina
    # ==========================================
    if not imagenes_generadas:
        raise RuntimeError(
            "No se encontraron componentes con niveles válidos."
        )

    paginas = []
    for archivo in imagenes_generadas:
        # Se añade .copy() para evitar problemas de punteros cerrados en memoria con PIL
        with Image.open(archivo) as img:
            paginas.append(img.convert("RGB").copy())

    paginas[0].save(
        pdf_salida,
        save_all=True,
        append_images=paginas[1:],
        resolution=300.0
    )

    # print(f"PDF generado: {pdf_salida}")
    return pdf_salida
