import cadquery as cq

# 1. Creamos las geometrías por separado
muro_principal = cq.Workplane("XY").box(10, 10, 2)
muro_secundario = cq.Workplane("XY").box(5, 5, 2).translate((15, 0, 0))
columnas = cq.Workplane("XY").box(2, 2, 4).translate((4, 4, 0))

# 2. Inicializamos el ensamblaje raíz vacío
plano_arquitectonico = cq.Assembly()

# 3. Creamos un sub-ensamblaje independiente que actuará como la capa "CAPA_MUROS"
#    Al pasarlo vacío, este objeto ya nace con su propio nombre asignado
capa_muros = cq.Assembly(name="CAPA_MUROS")

# 4. Agregamos los muros DENTRO de este sub-ensamblaje
capa_muros.add(muro_principal, name="muro_1", color=cq.Color("black"))
capa_muros.add(muro_secundario, name="muro_2", color=cq.Color("black"))

# 5. Metemos la capa completa de muros dentro del plano principal
plano_arquitectonico.add(capa_muros)

# 6. Agregamos las columnas en su propia capa en la raíz
plano_arquitectonico.add(columnas, name="CAPA_COLUMNAS", color=cq.Color("red"))

print("-> ¡Estructura de ensamblaje creada con éxito sin errores!")