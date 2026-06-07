import plotly.graph_objects as go
import numpy as np


import numpy as np
import plotly.graph_objects as go


import numpy as np
import plotly.graph_objects as go

def render_3d(
    escena: list, 
    titulo: str = "Render 3D"
):
    fig = go.Figure()

    colores = {
        "Muros": "rgb(183,183,183)",
        "Columnas": "rgb(123,123,123)",
        "Ventana": "rgba(50, 50, 50, 0.4)",
        "Balcon": "rgb(102, 102, 102)",
        "Vigas": "rgb(123,123,123)",
        "Patio": "rgb(1, 130, 3)",
        "Pasadizo": "rgb(183,183,183)",
        "Losa": "rgb(34,41,47)",
        "Puerta": "rgb(43,23,13)",
    }

    todos_los_x = []
    todos_los_y = []
    todos_los_z = []

    # Iteramos sobre la lista de diccionarios, considerando todo el objeto
    for pieza in escena:
        nombre = pieza["name"]
        
        if not pieza["vertices"] or not pieza["faces"]:
            continue

        # Intentamos obtener el estilo si la función obtener_estilo existe en tu entorno
        try:
            estilo = obtener_estilo(nombre)
        except NameError:
            estilo = {"fill_color": "rgba(100, 100, 100, 0.2)"}

        lista_vertices_unicos = []
        mapa_vertices = {}  
        I, J, K = [], [], []

        # 1. PROCESAMIENTO COMPLETO DE LAS CARAS (FACES)
        for cara_3d in pieza["faces"]:
            cara_indices = []
            for pt in cara_3d:
                # Conservamos las coordenadas 3D exactas (X, Y, Z)
                pt_tupla = (round(pt[0], 4), round(pt[1], 4), round(pt[2], 4))
                if pt_tupla not in mapa_vertices:
                    mapa_vertices[pt_tupla] = len(lista_vertices_unicos)
                    lista_vertices_unicos.append(pt_tupla)
                cara_indices.append(mapa_vertices[pt_tupla])

            # Triangulación dinámica de las caras para go.Mesh3d (soporta 3 y 4 puntos)
            if len(cara_indices) == 4:
                # Triángulo A
                I.append(cara_indices[0])
                J.append(cara_indices[1])
                K.append(cara_indices[2])
                # Triángulo B
                I.append(cara_indices[0])
                J.append(cara_indices[2])
                K.append(cara_indices[3])
            elif len(cara_indices) == 3:
                I.append(cara_indices[0])
                J.append(cara_indices[1])
                K.append(cara_indices[2])

        vertices = np.array(lista_vertices_unicos)
        vertices = np.round(vertices, 4)
        vertices[np.abs(vertices) < 1e-6] = 0

        # Acumulación para el cálculo de los límites de la cámara
        todos_los_x.extend(vertices[:, 0])
        todos_los_y.extend(vertices[:, 1])
        todos_los_z.extend(vertices[:, 2])

        # Asignación del color correspondiente según el diccionario de la escena
        color_plotly = "rgba(200, 200, 200, 0.9)"
        for clave, color in colores.items():
            if clave in nombre:
                color_plotly = color
                break

        # 2. ADICIÓN DEL OBJETO VOLUMÉTRICO 3D (Malla + Aristas)
        fig.add_trace(
            go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=I,
                j=J,
                k=K,
                name=nombre,
                color=color_plotly,
                flatshading=True,
                # Evita que las caras traseras queden invisibles al girar la cámara
                contour=dict(show=True, color="rgb(40,40,40)", width=1.5),
                lighting=dict(
                    ambient=0.6,
                    diffuse=0.5,
                    fresnel=0.2,
                    specular=0.1,
                    roughness=0.5
                )
            )
        )

        # 3. PROYECCIÓN DE SHAPES (Bim Planar Fill) EN EL SUELO Z = 0
        if estilo.get("fill_color") or "Losa" in nombre:
            fill_c = estilo.get("fill_color", "rgba(50, 50, 50, 0.15)")
            
            min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
            min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
            
            # Construcción del plano bidimensional proyectado en la base
            x_shape = [min_x, max_x, max_x, min_x]
            y_shape = [min_y, min_y, max_y, max_y]
            z_shape = [0.0, 0.0, 0.0, 0.0] 

            fig.add_trace(
                go.Mesh3d(
                    x=x_shape,
                    y=y_shape,
                    z=z_shape,
                    i=[0, 0],
                    j=[1, 2],
                    k=[2, 3],
                    color=fill_c,
                    opacity=0.35,
                    name=f"Base - {nombre}",
                    showlegend=False,
                    hoverinfo='skip'
                )
            )

    # --- CONFIGURACIÓN DE LOS LÍMITES GLOBALES ---
    if todos_los_x:
        min_x, max_x = min(todos_los_x), max(todos_los_x)
        min_y, max_y = min(todos_los_y), max(todos_los_y)
        min_z, max_z = min(todos_los_z), max(todos_los_z)

        margen = 1.0
        rango_x = [min_x - margen, max_x + margen]
        rango_y = [min_y - margen, max_y + margen]
        rango_z = [min_z - margen, max_z + margen] if min_z < 0 else [0, max_z + margen]
    else:
        rango_x, rango_y, rango_z = None, None, None

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (Metros)", range=rango_x, autorange=False),
            yaxis=dict(title="Y (Metros)", range=rango_y, autorange=False),
            zaxis=dict(title="Z (Altura)", range=rango_z, autorange=False),
            aspectmode='data'  # Proporción exacta 1:1 de los metros de CadQuery
        ),
        title=titulo,
        margin=dict(r=20, l=20, b=20, t=40),
        template="plotly_white"
    )

    return fig


