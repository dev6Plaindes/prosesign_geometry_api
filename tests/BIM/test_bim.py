import cadquery as cq
from ocp_vscode import show_object

pieza = cq.Workplane("XY").box(10, 10, 10)

show_object(pieza)