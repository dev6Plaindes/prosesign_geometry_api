import sys
sys.path.append('c:\\Users\\HP\\Desktop\\ProDesign\\prosesign_geometry_api')

import cadquery as cq
from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.escaleras import create_stairs, get_stair_dimensions

# Set up project config similar to what is used in the app
CONFIG_PROYECTO['alto_nivel'] = 3.0
CONFIG_PROYECTO['e_muro'] = 0.15
CONFIG_PROYECTO['ancho_escalera'] = 1.2
CONFIG_PROYECTO['ancho_pasadiso'] = 1.8
CONFIG_PROYECTO['ancho_hab'] = 7.0

ensamblaje = cq.Assembly()
x_escalera = 7.0 + 22.5 # desplazamiento_x + largo_bloque_fijo
desplazamiento_y_escalera = 29.9264

stair = create_stairs(
    ensamblaje=ensamblaje,
    ancho_hab=7.0,
    desplazamiento_x=x_escalera,
    desplazamiento_y=desplazamiento_y_escalera,
    sufijo_nombre="Inicial",
    posicion_puerta="bottom",
    nivel=1,
    orientacion="vertical",
    huella=0.28,
    contrahuella_max=0.17,
    pivot_x=7.0,
    pivot_y=29.9264
)

# Find bounding box
bbox = stair.val().BoundingBox()
print(f"Stair Bounding Box:")
print(f"X: {bbox.xMin} to {bbox.xMax}")
print(f"Y: {bbox.yMin} to {bbox.yMax}")
print(f"Z: {bbox.zMin} to {bbox.zMax}")
