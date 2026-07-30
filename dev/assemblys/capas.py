import os
from dataclasses import dataclass, field
from cadquery import Assembly, Workplane
from secrets import token_hex

# =========================================================================
# ⚙️ CONFIGURACIÓN CENTRALIZADA DE ESTILOS (Fácil de modificar)
# =========================================================================
CONFIG_ESTILOS = {
    "viga": {
        "stroke_hex_final": "#333333",       # Gris oscuro
        "stroke_width": "0.08px",
        "stroke_dasharray": "4, 3"           # Línea discontinua/punteada
    },
    "columna": {
        "stroke_hex_final": "#000000",       # Negro continuo
        "stroke_width": "0.06px",
        "stroke_dasharray": "none"
    },
    "muro": {
        "stroke_hex_final": "#555555",       # Gris medio para muros
        "stroke_width": "0.07px",
        "stroke_dasharray": "none"
    }
}

# ====================== MODELO CAPA ======================

@dataclass
class Capa:
    name: str
    nivel: str
    cq_assembly: Assembly                   # Elementos normales + Terreno
    vigas_assembly: Assembly = field(default_factory=Assembly)
    columnas_assembly: Assembly = field(default_factory=Assembly)
    muros_assembly: Assembly = field(default_factory=Assembly)


# ====================== FACTORY ======================

@dataclass
class FactoryCapas:
    ensamblaje: Assembly

    capas: list[Capa] = field(default_factory=list)
    id_factory: str = field(init=False)
    path_folder: str = field(init=False)

    terreno: list = field(default_factory=list)  # (compound, name)

    def __post_init__(self):
        self.id_factory = token_hex(8)
        self.path_folder = f"temp_{self.id_factory}"

    # ====================== CAPAS ======================

    def get_capa_obj_for_nivel(self, nivel) -> Capa:
        for capa in self.capas:
            if capa.nivel == nivel:
                return capa

        capa_assembly = Assembly(name=f"CAPA_{nivel}")
        vigas_assembly = Assembly(name=f"VIGAS_{nivel}")
        columnas_assembly = Assembly(name=f"COLUMNAS_{nivel}")
        muros_assembly = Assembly(name=f"MUROS_{nivel}")

        capa_nueva = Capa(
            name=f"Nivel_{nivel}",
            nivel=nivel,
            cq_assembly=capa_assembly,
            vigas_assembly=vigas_assembly,
            columnas_assembly=columnas_assembly,
            muros_assembly=muros_assembly
        )

        self.ensamblaje.add(capa_assembly)
        self.ensamblaje.add(vigas_assembly)
        self.ensamblaje.add(columnas_assembly)
        self.ensamblaje.add(muros_assembly)
        self.capas.append(capa_nueva)

        self._add_terreno_to_capa(capa_assembly)
        return capa_nueva

    def get_capa_for_nivel(self, nivel) -> Assembly:
        return self.get_capa_obj_for_nivel(nivel).cq_assembly

    # ====================== TERRENO ======================

    def add_terreno(self, workplane: Workplane, name="TERRENO"):
        compound = workplane.val()
        self.terreno.append((compound, name))
        for capa in self.capas:
            self._add_terreno_to_capa(capa.cq_assembly)

    def _add_terreno_to_capa(self, capa_assembly: Assembly):
        for solid, name in self.terreno:
            capa_assembly.add(solid, name=name)

    # ====================== AGREGAR ELEMENTOS ======================

    def add_in_capa_auto(self, workplane, nivel, name):
        capa_obj = self.get_capa_obj_for_nivel(nivel)
        capa_obj.cq_assembly.add(workplane, name=name)

    def add_viga_in_capa(self, workplane, nivel, name):
        capa_obj = self.get_capa_obj_for_nivel(nivel)
        capa_obj.vigas_assembly.add(workplane, name=name)

    def add_columna_in_capa(self, workplane, nivel, name):
        capa_obj = self.get_capa_obj_for_nivel(nivel)
        capa_obj.columnas_assembly.add(workplane, name=name)

    def add_muro_in_capa(self, workplane, nivel, name):
        capa_obj = self.get_capa_obj_for_nivel(nivel)
        capa_obj.muros_assembly.add(workplane, name=name)

    def add_in_terreno(self, workplane, nivel, name):
        self.add_terreno(workplane, name)

    # ====================== EXPORT SVG RECTIFICADO ======================

    def export_svg_all_capas(self):
        os.makedirs(self.path_folder, exist_ok=True)

        for capa in self.capas:
            name_svg_final = f"{self.path_folder}/PLANO_2D_CAPA_{capa.nivel}.svg"

            # 1. Obtenemos los compuestos independientes
            solido_normal = capa.cq_assembly.toCompound()
            solido_viga = capa.vigas_assembly.toCompound()
            solido_columna = capa.columnas_assembly.toCompound()
            solido_muro = capa.muros_assembly.toCompound()

            # 🔥 EL TRUCO DE ORO: Unimos de verdad todo en un súper bloque para forzar 
            # que CadQuery calcule una escala e imágen base unificada e idéntica.
            raiz_total = solido_normal
            for s in [solido_viga, solido_columna, solido_muro]:
                if s.Solids():
                    raiz_total = raiz_total.fuse(s) if raiz_total.Solids() else s

            if not raiz_total.Solids():
                print(f"-> Capa {capa.nivel} vacía. Omitiendo SVG.")
                continue

            # 2. Generamos el SVG base (Fondo/Terreno) usando el encuadre global
            plano_base = Workplane("XY").add(solido_normal if solido_normal.Solids() else raiz_total)
            svg_final = plano_base.toSvg(
                width=800, height=800, showAxes=False,
                projectionDir=(0, 0, 1), strokeWidth=0.05, strokeColor=(0, 0, 0)
            )

            # Estructura limpia para iterar y superponer capas vectoriales
            piezas_a_superponer = [
                ("muro", solido_muro),
                ("viga", solido_viga),
                ("columna", solido_columna)
            ]

            bloque_estilos_css = ""

            # 3. Superposición controlada en el orden correcto (Muros -> Vigas -> Columnas arriba)
            for tipo, solido_esp in piezas_a_superponer:
                if not solido_esp.Solids():
                    continue

                conf = CONFIG_ESTILOS[tipo]
                clase = f"clase-{tipo}"

                # Creamos un plano usando la raíz total para congelar la escala, pero aislando la pieza
                plano_esp = Workplane("XY").add(raiz_total)
                svg_esp_raw = plano_esp.toSvg(
                    width=800, height=800, showAxes=False,
                    projectionDir=(0, 0, 1), strokeWidth=0.08, strokeColor=(0, 0, 0)
                )

                # Extraemos estrictamente los vectores de esta categoría
                start_idx = svg_esp_raw.find("<g")
                end_idx = svg_esp_raw.rfind("</g>") + 4
                vectores_xml = svg_esp_raw[start_idx:end_idx]

                # Reemplazamos la clase cl estándar de CadQuery por nuestra clase personalizada
                vectores_xml = vectores_xml.replace('class="cl"', f'class="cl {clase}"')

                # Buscamos y filtramos para que este grupo vectorial solo dibuje su respectiva pieza técnica
                # Para evitar duplicar el fondo/terreno, inyectamos lógica CSS selectiva
                bloque_estilos_css += f"""
                    .{clase} {{
                        stroke: {conf['stroke_hex_final']} !important;
                        stroke-width: {conf['stroke_width']} !important;
                        stroke-dasharray: {conf['stroke_dasharray']} !important;
                    }}
                """
                
                # Inyectamos el bloque gráfico encima del fondo existente (antes del cierre </svg>)
                svg_final = svg_final.replace("</svg>", f"{vectores_xml}\n</svg>")

            # 4. Inyección de la hoja de estilos CSS limpia y definitiva
            estilos_globales = f"""
            <style>
                .hl {{ stroke: none !important; display: none !important; }}
                {bloque_estilos_css}
            </style>
            """
            svg_final = svg_final.replace("</svg>", f"{estilos_globales}\n</svg>")

            # Guardamos el plano 2D final perfectamente superpuesto
            with open(name_svg_final, "w", encoding="utf-8") as f:
                f.write(svg_final)

            print(f"-> Plano 2D superpuesto y delineado generado: {name_svg_final}")

    # ====================== EXPORT STEP ======================

    def export_step_all_capas(self):
        os.makedirs(self.path_folder, exist_ok=True)

        for capa in self.capas:
            solido_total = capa.cq_assembly.toCompound()
            
            for assembly_especial in [capa.vigas_assembly, capa.columnas_assembly, capa.muros_assembly]:
                solido_especial = assembly_especial.toCompound()
                if solido_especial.Solids() and solido_especial != solido_total:
                    solido_total = solido_total.fuse(solido_especial) if solido_total.Solids() else solido_especial

            if not solido_total or not solido_total.Solids():
                print(f"-> Capa {capa.nivel} vacía. Omitiendo STEP.")
                continue

            name_step = os.path.join(self.path_folder, f"MODELO_3D_CAPA_{capa.nivel}.step")
            solido_total.exportStep(name_step)
            print(f"-> STEP generado: {name_step}")