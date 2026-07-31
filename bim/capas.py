import os
from dataclasses import dataclass, field
from cadquery import Assembly, Location, Vector, Workplane
from secrets import token_hex


# ====================== MODELO CAPA ======================

@dataclass
class Capa:
    name: str
    nivel: str
    cq_assembly: Assembly


# ====================== FACTORY ======================

@dataclass
class FactoryCapas:
    ensamblaje: Assembly

    x_referencia: float = 0.0
    y_referencia: float = 0.0
    degree_referencia: float = 0.0

    capas: list[Capa] = field(default_factory=list)
    id_factory: str = field(init=False)
    path_folder: str = field(init=False)

    # 🔥 TERRENO AHORA ES INMUTABLE (Compound)
    terreno: list = field(default_factory=list)  # (compound, name)

    def __post_init__(self):
        self.id_factory = token_hex(8)
        self.path_folder = f"temp_{self.id_factory}"

    # ====================== CAPAS ======================

    def get_capa_for_nivel(self, nivel) -> Assembly:
        for i in self.capas:
            if i.nivel == nivel:
                return i.cq_assembly

        capa_assembly = Assembly(name=f"CAPA_{nivel}")

        capa_nueva = Capa(
            name=f"Nivel_{nivel}",
            nivel=nivel,
            cq_assembly=capa_assembly
        )

        self.ensamblaje.add(capa_assembly)
        self.capas.append(capa_nueva)

        # 🔥 inyectar terreno automáticamente
        self._add_terreno_to_capa(capa_assembly)

        return capa_assembly

    # ====================== TERRENO ======================

    def add_terreno(self, workplane : Workplane, name="TERRENO"):
        """
        Guarda terreno como geometría fija (Compound)
        y lo replica en todas las capas.
        """

        # 🔴 FIX IMPORTANTE: convertir a geometría final
        compound = workplane.val()

        self.terreno.append((compound, name))

        # aplicar a todas las capas existentes
        for capa in self.capas:
            self._add_terreno_to_capa(capa.cq_assembly)

    def _add_terreno_to_capa(self, capa_assembly: Assembly):
        """
        Inserta terreno en una capa específica.
        """

        posicion = Vector(0, 0, 0)
        eje_rotacion = Vector(0, 0, 1)
        loc = Location(posicion, eje_rotacion, 0)

        for solid, name in self.terreno:
            capa_assembly.add(solid, name=name, loc=loc)

    # ====================== ELEMENTOS NORMALES ======================

    def add_in_capa_auto(self, workplane, nivel, name):
        capa_assembly = self.get_capa_for_nivel(nivel)

        posicion = Vector(self.x_referencia, self.y_referencia, 0)
        eje_rotacion = Vector(0, 0, 1)
        loc = Location(posicion, eje_rotacion, self.degree_referencia)

        capa_assembly.add(workplane, name=name, loc=loc)

    def add_columna_in_capa(self, workplane, nivel, name):
        """Alias para add_in_capa_auto, para mantener compatibilidad."""
        self.add_in_capa_auto(workplane, nivel, name)

    def add_viga_in_capa(self, workplane, nivel, name):
        """Alias para add_in_capa_auto, para mantener compatibilidad."""
        self.add_in_capa_auto(workplane, nivel, name)

    def add_in_terreno(self, workplane, nivel, name):
        self.add_terreno(workplane, name)

    # ====================== EXPORT SVG ======================

    def export_svg_all_capas(self):
        os.makedirs(self.path_folder, exist_ok=True)

        for capa in self.capas:
            solido = capa.cq_assembly.toCompound()
            plano = Workplane("XY").add(solido)

            name_svg = f"{self.path_folder}/PLANO_2D_CAPA_{capa.nivel}.svg"

            plano.export(
                name_svg,
                opt={
                    "width": 800,
                    "height": 800,
                    "showAxes": False,
                    "projectionDir": (0, 0, 1),
                    "strokeWidth": 0.05,
                    "strokeColor": (0, 0, 0)
                }
            )

            print(f"-> SVG generado: {name_svg}")

    # ====================== EXPORT STEP ======================

    def export_step_all_capas(self):
        os.makedirs(self.path_folder, exist_ok=True)

        for capa in self.capas:
            solido = capa.cq_assembly.toCompound()

            name_step = os.path.join(
                self.path_folder,
                f"MODELO_3D_CAPA_{capa.nivel}.step"
            )

            solido.exportStep(name_step)

            print(f"-> STEP generado: {name_step}")