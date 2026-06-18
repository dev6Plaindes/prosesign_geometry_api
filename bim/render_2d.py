import plotly.graph_objects as go
import numpy as np
from collections import defaultdict

ESTILOS = {
    "Techo": {
        "line_color": "gray",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Muro": {
        "line_color": "black",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Ventana": {
        "line_color": "black",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Losa": {
        "line_color": "gray",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Balcon": {
        "line_color": "gray",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Puerta": {
        "line_color": "gray",
        "line_width": None,
        "dash": "solid",
        "fill_color": "gray",
        "legend": False,
    },
    "Escalera": {
        "line_color": "gray",
        "line_width": 1,
        "dash": "solid",
        "fill_color": None,
        "legend": False,
    },
    "Viga": {
        "line_color": "gray",
        "line_width": 1,
        "dash": "dash",
        "fill_color": None,
        "legend": False,
    },
    "Column": {
        "line_color": "black",
        "line_width": 1,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
    "Base": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
    "Cuadrante": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
    "Terreno": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
    "Aula": {
        "line_color": "lightblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightblue",
        "legend": True,
    },
    "Biblioteca": {
        "line_color": "lightgreen",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightgreen",
        "legend": True,
    },
    "Taller": {
        "line_color": "lightyellow",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightyellow",
        "legend": True,
    },
    "Topico": {
        "line_color": "lightcyan",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightcyan",
        "legend": True,
    },
    "Direccion": {
        "line_color": "beige",
        "line_width": 1,
        "dash": None,
        "fill_color": "beige",
        "legend": True,
    },
    "Sala": {
        "line_color": "ivory",
        "line_width": 1,
        "dash": None,
        "fill_color": "ivory",
        "legend": True,
    },
    "Área de": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "Cocina": {
        "line_color": "honeydew",
        "line_width": 1,
        "dash": None,
        "fill_color": "honeydew",
        "legend": True,
    },
    "DEFAULT": {
        "line_color": None,
        "line_width": None,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
}


def obtener_estilo(nombre):

    for clave, estilo in ESTILOS.items():

        if clave in nombre:
            return estilo

    return ESTILOS["DEFAULT"]


def render_2d(escena):

    fig = go.Figure()

    for nombre, geometria in escena.items():

        estilo = obtener_estilo(nombre)

        vertices = np.array(geometria["vertices"])
        faces = np.array(geometria["faces"])

        pts = vertices[:, :2]

        edges = defaultdict(int)

        for cara in faces:

            lados = [
                tuple(sorted((cara[0], cara[1]))),
                tuple(sorted((cara[1], cara[2]))),
                tuple(sorted((cara[2], cara[0]))),
            ]

            for edge in lados:
                if edge[0] != edge[1]:
                    edges[edge] += 1

        bordes = [e for e, c in edges.items() if c == 1]

        x_lines = []
        y_lines = []

        for e in bordes:

            p1 = pts[e[0]]
            p2 = pts[e[1]]

            x_lines.extend([p1[0], p2[0], None])
            y_lines.extend([p1[1], p2[1], None])

        if estilo["fill_color"]:

            min_x = np.min(pts[:, 0])
            max_x = np.max(pts[:, 0])

            min_y = np.min(pts[:, 1])
            max_y = np.max(pts[:, 1])

            fig.add_shape(
                type="rect",
                x0=min_x,
                y0=min_y,
                x1=max_x,
                y1=max_y,
                fillcolor=estilo["fill_color"],
                line=dict(width=0),
                layer="below",
            )

        fig.add_trace(
            go.Scatter(
                x=x_lines,
                y=y_lines,
                mode="lines",
                line=dict(
                    color=estilo["line_color"],
                    width=estilo["line_width"],
                    dash=estilo["dash"],
                ),
                name=nombre,
                showlegend=estilo["legend"],
            )
        )

    fig.update_layout(
        title="Render 2D",
        xaxis_title="X",
        yaxis_title="Y",
        yaxis_scaleanchor="x",
        template="plotly_white",
    )

    return fig


import plotly.graph_objects as go

# def render_2d_shapely(escena_shapely):
#     fig = go.Figure()

#     for nombre, coleccion in escena_shapely.items():
#         estilo = obtener_estilo(nombre)

#         x_lines = []
#         y_lines = []

#         # Recorremos cada objeto geométrico guardado en la colección de la pieza
#         for geom in coleccion.geoms:

#             if geom.geom_type == 'Polygon':
#                 # Extraemos el contorno del polígono
#                 x_coords, y_coords = geom.exterior.xy
#                 x_lines.extend(list(x_coords) + [None])
#                 y_lines.extend(list(y_coords) + [None])

#                 # Extraemos huecos internos si existen
#                 for interior in geom.interiors:
#                     x_int, y_int = interior.xy
#                     x_lines.extend(list(x_int) + [None])
#                     y_lines.extend(list(y_int) + [None])

#             elif geom.geom_type == 'LineString':
#                 # Extraemos las coordenadas de la línea colapsada directo
#                 x_coords, y_coords = geom.xy
#                 x_lines.extend(list(x_coords) + [None])
#                 y_lines.extend(list(y_coords) + [None])

#         # Añadimos todos los trazos recuperados a Plotly
#         fig.add_trace(
#             go.Scatter(
#                 x=x_lines,
#                 y=y_lines,
#                 mode="lines",
#                 line=dict(
#                     color=estilo["line_color"],
#                     width=estilo["line_width"],
#                     dash=estilo["dash"]
#                 ),
#                 name=nombre,
#                 showlegend=estilo["legend"],
#                 hoverinfo="skip" # Opcional: para que el borde no compita con el relleno en el hover
#             )
#         )

#         # Si requieres el fill_color, puedes calcular los bounds globales de la colección entera:
#         if estilo["fill_color"] and not coleccion.is_empty:
#             min_x, min_y, max_x, max_y = coleccion.bounds

#             # Definimos las 4 esquinas del rectángulo cerrando en el primer punto para simular el fill
#             x_rect = [min_x, max_x, max_x, min_x, min_x]
#             y_rect = [min_y, min_y, max_y, max_y, min_y]

#             fig.add_trace(
#                 go.Scatter(
#                     x=x_rect,
#                     y=y_rect,
#                     mode="text+lines",      # "text" por si quieres meter el nombre flotando adentro
#                     fill="toself",          # ◄--- ESTA ES LA CLAVE: Rellena el polígono
#                     fillcolor=estilo["fill_color"],
#                     line=dict(color="rgba(0,0,0,0)", width=0), # Línea invisible para que no duplique el borde
#                     name=nombre,
#                     legendgroup=nombre,     # Vincula este relleno a la leyenda de la línea
#                     showlegend=estilo["legend"],
#                     hoveron="fills",        # ◄--- CLAVE INTERACTIVA: El clic y hover se activan en TODO el relleno
#                     hovertemplate=f"<b>{nombre}</b><br>Largo: %{{dx}}<br><extra></extra>" # Customiza lo que dice al hacer clic/hover
#                 )
#             )

#     fig.update_layout(
#         title="Render 2D",
#         xaxis_title="X",
#         yaxis_title="Y",
#         yaxis_scaleanchor="x",
#         template="plotly_white"
#     )

#     return fig

import plotly.graph_objects as go


def render_2d_shapely(escena_shapely):
    fig = go.Figure()

    for nombre, coleccion in escena_shapely.items():
        estilo = obtener_estilo(nombre)

        # ==========================
        # LEYENDA DEL RELLENO
        # ==========================
        if estilo["fill_color"] and estilo["legend"]:
            fig.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode="markers",
                    marker=dict(size=12, color=estilo["fill_color"], symbol="square"),
                    name=nombre,
                    legendgroup=nombre,
                    showlegend=True,
                    hoverinfo="skip",
                )
            )

        x_lines = []
        y_lines = []

        # ==========================
        # RECORRER GEOMETRÍAS
        # ==========================
        for geom in coleccion.geoms:

            # --------------------------
            # POLÍGONOS
            # --------------------------
            if geom.geom_type == "Polygon":

                # Relleno del polígono real
                if estilo["fill_color"]:

                    x_fill, y_fill = geom.exterior.xy

                    fig.add_trace(
                        go.Scatter(
                            x=list(x_fill),
                            y=list(y_fill),
                            fill="toself",
                            fillcolor=estilo["fill_color"],
                            mode="lines",
                            line=dict(color="rgba(0,0,0,0)", width=0),
                            legendgroup=nombre,
                            showlegend=False,
                            hoveron="fills",
                            hovertemplate=f"<b>{nombre}</b><extra></extra>",
                        )
                    )

                # Borde exterior
                x_coords, y_coords = geom.exterior.xy

                x_lines.extend(list(x_coords) + [None])
                y_lines.extend(list(y_coords) + [None])

                # Huecos internos
                for interior in geom.interiors:
                    x_int, y_int = interior.xy

                    x_lines.extend(list(x_int) + [None])
                    y_lines.extend(list(y_int) + [None])

            # --------------------------
            # LINESTRING
            # --------------------------
            elif geom.geom_type == "LineString":

                x_coords, y_coords = geom.xy

                x_lines.extend(list(x_coords) + [None])
                y_lines.extend(list(y_coords) + [None])

        # ==========================
        # DIBUJAR BORDES
        # ==========================
        if x_lines:

            fig.add_trace(
                go.Scatter(
                    x=x_lines,
                    y=y_lines,
                    mode="lines",
                    line=dict(
                        color=estilo["line_color"],
                        width=estilo["line_width"],
                        dash=estilo["dash"],
                    ),
                    legendgroup=nombre,
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    # ==========================
    # LAYOUT
    # ==========================
    fig.update_layout(
        title="Render 2D",
        xaxis_title="X",
        yaxis_title="Y",
        yaxis_scaleanchor="x",
        template="plotly_white",
        legend=dict(groupclick="toggleitem"),
    )

    return fig


import re
import plotly.graph_objects as go


def render_2d_shapely_automatico_regex(escena_shapely):
    # Diccionario dinámico para agrupar por nivel exacto
    elementos_por_nivel = {}
    # Lista para almacenar los elementos globales que van en todos los niveles
    elementos_globales = []

    # 1. Clasificación automática
    for nombre, coleccion in escena_shapely.items():
        # Condición especial: Si contiene "Base Cuadrante" o "Terreno", es global
        if "Base Cuadrante" in nombre or "Terreno" in nombre:
            elementos_globales.append((nombre, coleccion))
            continue  # Saltamos al siguiente elemento sin asignarle un nivel específico

        # Buscamos el patrón "Nivel " seguido de cualquier número
        coincidencia = re.search(r"(Nivel\s+\d+)", nombre)

        if coincidencia:
            nivel = coincidencia.group(1)
        else:
            nivel = "Otros"  # Por si algún elemento no tiene la palabra Nivel
            continue

        if nivel not in elementos_por_nivel:
            elementos_por_nivel[nivel] = []

        elementos_por_nivel[nivel].append((nombre, coleccion))

    # 2. Inyección de elementos globales en todos los niveles detectados
    # Si no se detectó ningún nivel pero hay elementos globales, creamos un contenedor por defecto
    if not elementos_por_nivel and elementos_globales:
        elementos_por_nivel["General"] = []

    for nivel in elementos_por_nivel.keys():
        elementos_por_nivel[nivel].extend(elementos_globales)

    # Diccionario donde guardaremos cada figura generada
    graficos_por_nivel = {}

    # 3. Generación automática de un gráfico por cada nivel encontrado
    for nivel, elementos in elementos_por_nivel.items():
        fig = go.Figure()

        for nombre, coleccion in elementos:
            estilo = obtener_estilo(nombre)
            x_lines, y_lines = [], []

            for geom in coleccion.geoms:
                if geom.geom_type == "Polygon":
                    x_coords, y_coords = geom.exterior.xy
                    x_lines.extend(list(x_coords) + [None])
                    y_lines.extend(list(y_coords) + [None])

                    for interior in geom.interiors:
                        x_int, y_int = interior.xy
                        x_lines.extend(list(x_int) + [None])
                        y_lines.extend(list(y_int) + [None])

                elif geom.geom_type == "LineString":
                    x_coords, y_coords = geom.xy
                    x_lines.extend(list(x_coords) + [None])
                    y_lines.extend(list(y_coords) + [None])

            # Añadir geometría al gráfico de este nivel
            fig.add_trace(
                go.Scatter(
                    x=x_lines,
                    y=y_lines,
                    mode="lines",
                    line=dict(
                        color=estilo["line_color"],
                        width=estilo["line_width"],
                        dash=estilo["dash"],
                    ),
                    name=extraer_nombre_ambiente(nombre),
                    showlegend=estilo["legend"],
                )
            )

            if estilo["fill_color"] and not coleccion.is_empty:
                min_x, min_y, max_x, max_y = coleccion.bounds
                fig.add_shape(
                    type="rect",
                    x0=min_x,
                    y0=min_y,
                    x1=max_x,
                    y1=max_y,
                    fillcolor=estilo["fill_color"],
                    line=dict(width=0),
                    layer="below",
                )

        # Título dinámico para el gráfico actual
        fig.update_layout(
            title=f"Render 2D - {nivel}",
            yaxis_scaleanchor="x",  # Mantiene la proporción 1:1 entre X e Y
            template="plotly_white",
            xaxis=dict(
                showgrid=False,  # Quita las líneas verticales de la grilla
                showticklabels=False,  # Quita los números del eje X
                visible=False,  # Oculta la línea base del eje X
            ),
            yaxis=dict(
                showgrid=False,  # Quita las líneas horizontales de la grilla
                showticklabels=False,  # Quita los números del eje Y
                visible=False,  # Oculta la línea base del eje Y
            ),
        )

        # Guardamos la figura usando el nivel como clave
        graficos_por_nivel[nivel] = fig

    return graficos_por_nivel


import re


def extraer_nombre_ambiente(texto: str) -> str:
    """
    Busca y retorna el texto que está dentro de los corchetes [].
    Si no encuentra corchetes, retorna el texto original limpio.
    """
    # El patrón busca lo que esté entre [ y ] de forma no codiciosa (.*?)
    match = re.search(r"\[(.*?)\]", texto)

    if match:
        return match.group(1)  # Retorna solo el contenido capturado

    return texto.strip()  # Por si acaso el string no tenía corchetes
