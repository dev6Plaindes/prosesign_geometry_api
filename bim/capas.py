import os
from dataclasses import dataclass, field
from cadquery import Assembly, Location, Vector, Workplane
from secrets import token_hex

@dataclass
class Capa:
    name: str
    nivel: str
    cq_assembly : Assembly

@dataclass
class FactoryCapas:
    ensamblaje: Assembly
    x_referencia: float = 0.0
    y_referencia: float = 0.0
    degree_referencia: float = 0.0
    path: str = None
    capas : list[Capa] = field(default_factory=list)
    id_factory: str = field(init=False)
    path_folder: str = field(init=False)
    
    def __post_init__(self):
        self.id_factory = token_hex(8)
        self.path_folder = f"temp_{self.id_factory}"

    # Si existe la capa la retorna y si no la crea y retorna
    # Retorna el cq assembly
    def get_capa_for_nivel(self, nivel) -> Assembly:
        for i in self.capas:
            if i.nivel == nivel:
                return i.cq_assembly

        capa_assembly = Assembly(name=f"CAPA_{nivel}")
        capa_nueva : Capa = Capa(name=f"Nivel_{nivel}", nivel=nivel, cq_assembly=capa_assembly)
        self.ensamblaje.add(capa_assembly)
        self.capas.append(capa_nueva)
        return capa_assembly
    
    # Agregar un workplane a una capa segun el ni
    
    def add_in_terreno(self, workplane, nivel, name):   
        capa_assembly = self.get_capa_for_nivel(nivel)
        # 1. Creamos el vector de traslación con tus coordenadas de referencia
        posicion = Vector(0, 0, 0)
        
        # 2. Creamos el eje de rotación (Eje Z, ya que rotamos en el plano XY)
        eje_rotacion = Vector(0, 0, 1)
        
        # 3. Creamos la Localización combinando traslación y rotación (en grados)
        localizacion_referencia = Location(posicion, eje_rotacion, 0)
        
        # 4. Pasamos la localización al método add
        capa_assembly.add(workplane, name=name, loc=localizacion_referencia)
    
    def add_in_capa_auto(self, workplane, nivel, name):
        capa_assembly = self.get_capa_for_nivel(nivel)
        # 1. Creamos el vector de traslación con tus coordenadas de referencia
        posicion = Vector(self.x_referencia, self.y_referencia, 0)
        
        # 2. Creamos el eje de rotación (Eje Z, ya que rotamos en el plano XY)
        eje_rotacion = Vector(0, 0, 1)
        
        # 3. Creamos la Localización combinando traslación y rotación (en grados)
        localizacion_referencia = Location(posicion, eje_rotacion, self.degree_referencia)
        
        # 4. Pasamos la localización al método add
        capa_assembly.add(workplane, name=name, loc=localizacion_referencia)
        
    def export_svg_all_capas(self):
        
        os.makedirs(self.path_folder, exist_ok=True)
        
        for i in self.capas:
            capa_assembly = i.cq_assembly
            solido_combinado = capa_assembly.toCompound()
            plano_2d = Workplane("XY").add(solido_combinado)
            
            name_svg = f"temp_{self.id_factory}/PLANO_2D_CAPA_{i.nivel}.svg"

            plano_2d.export(
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
            print(f"-> ¡Éxito! SVG generado por proyección: {name_svg}")
            
            
            
