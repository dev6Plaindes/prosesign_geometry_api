import pandas as pd
from refactor.cuadrante_1 import cuadrante_1
import cadquery as cq

vertices_terreno = [
    [272100.00, 8692200.00],
    [272100.00, 8692235.00],
    [272140.00, 8692250.00],
    [272140.00, 8692290.00],
    [272190.00, 8692290.00],
    [272190.00, 8692255.00],
    [272150.00, 8692240.00],
    [272150.00, 8692200.00],
]

df_excel = pd.read_csv("./data_ambiente.csv")
data_builded, ensamblaje, factory_capas = cuadrante_1(vertices_terreno, df_excel)

# 1. Convertimos el ensamblaje en un solo sólido combinado
solido_combinado = ensamblaje.toCompound()

# 2. Lo metemos dentro de un Workplane SIMPLEMENTE para poder exportarlo
#    Ya NO usamos .section() ni .projectTo2D()
plano_2d = cq.Workplane("XY").add(solido_combinado)

# 3. Exportamos. El truco está en que CadQuery proyectará el 3D a 2D automáticamente en el SVG
name_svg = "plano_2d.svg"
plano_2d.export(
    name_svg,
    opt={
        "width": 800,
        "height": 800,
        "showAxes": False,
        "projectionDir": (0, 0, 1),  # Mira estrictamente desde arriba (Eje Z), aplanando todo a 2D
        "strokeWidth": 0.05,
        "strokeColor": (0, 0, 0),
        "showHidden": True,              # True para mostrarlas, False para desaparecerlas por completo
        "hiddenStrokeWidth": 0.3,       # Grosor de la línea oculta
        "hiddenStrokeColor": (255, 0, 0), # Puedes cambiar el color (ej. Rojo) para diferenciarlas
        "hiddenDashArray": "5,5"
    }
)

print(f"-> ¡Éxito! SVG generado por proyección: {name_svg}")

factory_capas.export_svg_all_capas()