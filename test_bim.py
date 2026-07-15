import cadquery as cq
from ocp_vscode import show

from bim.cuadrante_1 import cuadrante_1

box = cq.Workplane("XY").box(20, 20, 20)

vertices = [
        {
            "vertice": "V1",
            "x": 301686.819,
            "y": 8933010.389
        },
        {
            "vertice": "V2",
            "x": 301784.025,
            "y": 8933010.389
        },
        {
            "vertice": "V3",
            "x": 301784.025,
            "y": 8932948.875
        },
        {
            "vertice": "V4",
            "x": 301716.755,
            "y": 8932934.421
        },
        {
            "vertice": "V5",
            "x": 301672.692,
            "y": 8932955.262
        }
    ]

ambientes = [
  {
    "Ambientes": "Aulas Secundaria",
    "Metros_cuadrados": 300,
    "Cantidad": 5,
    "Unitario": 60,
    "Ancho": 7.5,
    "Largo": 8,
    "Tipo": "Fijo",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Aula de Innovacion Sec",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Taller creativo Sec",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Laboratorio",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Escalera Sec",
    "Metros_cuadrados": 8.64,
    "Cantidad": 1,
    "Unitario": 8.64,
    "Ancho": 7.5,
    "Largo": 2.5,
    "Tipo": "Fijo",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "SSHH Sec - Hombres",
    "Metros_cuadrados": 14.5,
    "Cantidad": 1,
    "Unitario": 14.5,
    "Ancho": 7.5,
    "Largo": 2.0,
    "Tipo": "Variable",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Sec - Mujeres",
    "Metros_cuadrados": 15.5,
    "Cantidad": 1,
    "Unitario": 15.5,
    "Ancho": 7.5,
    "Largo": 2.1,
    "Tipo": "Variable",
    "Pabellon": "Derecha",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Aulas Primaria",
    "Metros_cuadrados": 720,
    "Cantidad": 12,
    "Unitario": 60,
    "Ancho": 7.5,
    "Largo": 8,
    "Tipo": "Fijo",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Biblioteca",
    "Metros_cuadrados": 93.75,
    "Cantidad": 1,
    "Unitario": 93.75,
    "Ancho": 7.5,
    "Largo": 12.5,
    "Tipo": "Fijo",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Aula de Innovacion Prim",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Taller creativo Prim",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Escalera Prim",
    "Metros_cuadrados": 8.64,
    "Cantidad": 1,
    "Unitario": 8.64,
    "Ancho": 7.5,
    "Largo": 2.5,
    "Tipo": "Fijo",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "SSHH Prim - Hombres",
    "Metros_cuadrados": 20.5,
    "Cantidad": 1,
    "Unitario": 20.5,
    "Ancho": 7.5,
    "Largo": 2.7,
    "Tipo": "Variable",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Prim - Mujeres",
    "Metros_cuadrados": 23,
    "Cantidad": 1,
    "Unitario": 23,
    "Ancho": 7.5,
    "Largo": 3.1,
    "Tipo": "Variable",
    "Pabellon": "Izquierda",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Aulas Ciclo I",
    "Metros_cuadrados": 80,
    "Cantidad": 2,
    "Unitario": 40,
    "Ancho": 5.3,
    "Largo": 7.5,
    "Tipo": "Fijo",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Aulas Ciclo II",
    "Metros_cuadrados": 60,
    "Cantidad": 1,
    "Unitario": 60,
    "Ancho": 8.0,
    "Largo": 7.5,
    "Tipo": "Fijo",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1 y 2"
  },
  {
    "Ambientes": "Aulas Psicomotricidad",
    "Metros_cuadrados": 0,
    "Cantidad": 0,
    "Unitario": 0,
    "Ancho": 0.0,
    "Largo": 7.5,
    "Tipo": "Fijo",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Topico",
    "Metros_cuadrados": 27,
    "Cantidad": 1,
    "Unitario": 27,
    "Ancho": 3.6,
    "Largo": 7.5,
    "Tipo": "Fijo",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Lactario",
    "Metros_cuadrados": 22.5,
    "Cantidad": 1,
    "Unitario": 22.5,
    "Ancho": 3,
    "Largo": 7.5,
    "Tipo": "Fijo",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Inicial - Hombres",
    "Metros_cuadrados": 10.5,
    "Cantidad": 1,
    "Unitario": 10.5,
    "Ancho": 2.0,
    "Largo": 7.5,
    "Tipo": "Variable",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Inicial - Mujeres",
    "Metros_cuadrados": 10.5,
    "Cantidad": 1,
    "Unitario": 10.5,
    "Ancho": 2.0,
    "Largo": 7.5,
    "Tipo": "Variable",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Cocina Inicial",
    "Metros_cuadrados": 18.2,
    "Cantidad": 1,
    "Unitario": 18.2,
    "Ancho": 2.4,
    "Largo": 7.5,
    "Tipo": "Variable",
    "Pabellon": "Inferior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Direccion Adm.",
    "Metros_cuadrados": 9.75,
    "Cantidad": 1,
    "Unitario": 9.75,
    "Ancho": 2.0,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Área de espera",
    "Metros_cuadrados": 15,
    "Cantidad": 1,
    "Unitario": 15,
    "Ancho": 3.0,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Sala de Reuniones",
    "Metros_cuadrados": 42,
    "Cantidad": 1,
    "Unitario": 42,
    "Ancho": 8.4,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Area de ingreso",
    "Metros_cuadrados": 18,
    "Cantidad": 1,
    "Unitario": 18,
    "Ancho": 3.6,
    "Largo": 5.0,
    "Tipo": "Fijo",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Sala de Profesores",
    "Metros_cuadrados": 40,
    "Cantidad": 1,
    "Unitario": 40,
    "Ancho": 8.0,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Adm. - Hombres",
    "Metros_cuadrados": 17.25,
    "Cantidad": 1,
    "Unitario": 17.25,
    "Ancho": 3.5,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SSHH Adm. - Mujeres",
    "Metros_cuadrados": 17.25,
    "Cantidad": 1,
    "Unitario": 17.25,
    "Ancho": 3.5,
    "Largo": 5.0,
    "Tipo": "Variable",
    "Pabellon": "Superior",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Losa Deportiva",
    "Metros_cuadrados": 420,
    "Cantidad": 1,
    "Unitario": 420,
    "Ancho": 15,
    "Largo": 28,
    "Tipo": "Fijo",
    "Pabellon": "Medio",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Taller EPT",
    "Metros_cuadrados": 90,
    "Cantidad": 1,
    "Unitario": 90,
    "Ancho": 7.5,
    "Largo": 12,
    "Tipo": "Fijo",
    "Pabellon": "Medio",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "SUM",
    "Metros_cuadrados": 345,
    "Cantidad": 1,
    "Unitario": 345,
    "Ancho": 16,
    "Largo": 21.6,
    "Tipo": "Fijo",
    "Pabellon": "Medio",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Cocina Prim - Sec",
    "Metros_cuadrados": 41.7,
    "Cantidad": 1,
    "Unitario": 41.7,
    "Ancho": 7.5,
    "Largo": 5.6,
    "Tipo": "Variable",
    "Pabellon": "Medio",
    "Piso_de_preferencia": "1"
  },
  {
    "Ambientes": "Patio de Inicial",
    "Metros_cuadrados": 150,
    "Cantidad": 1,
    "Unitario": 150,
    "Ancho": 7.5,
    "Largo": 20.0,
    "Tipo": "Variable",
    "Pabellon": "Medio",
    "Piso_de_preferencia": "1"
  }
]

vertices = [[punto["x"], punto["y"]] for punto in vertices]
    
data_builded, assembly, factory_capas, RESUMEN_AREAS = cuadrante_1(
    vertices,
    ambientes
)

print("antes del show")

show(
    assembly,
    port=3939
)

print("después del show")