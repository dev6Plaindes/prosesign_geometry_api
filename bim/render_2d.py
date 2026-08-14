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
    "Aula de Innovacion": {
        "line_color": "green",
        "line_width": 1,
        "dash": None,
        "fill_color": "green",
        "legend": True,
    },
    "Aulas Primaria": {
        "line_color": "lightblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightblue",
        "legend": True,
    },
    "Aulas Secundaria": {
        "line_color": "lightgreen",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightgreen",
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
    # "Sala": {
    #     "line_color": "ivory",
    #     "line_width": 1,
    #     "dash": None,
    #     "fill_color": "ivory",
    #     "legend": True,
    # },
    "Sala de Profesores": {
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
    "Area de ingreso": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "SSHH Prim - Hombres": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "SSHH Prim - Mujeres": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "SSHH Adm. - Mujeres": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "SSHH Adm. - Hombres": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    # SSHH Adm. - Hombres
    # SSHH Adm. - Mujeres
    # SSHH Prim - Mujeres
    "Sala de reuniones": {
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
    "Patio Inicial": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": "gray",
        "legend": True,
    },
    "Patio Primaria Secundaria": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightgray",
        "legend": True,
    },
    "Losa Deportiva": {
        "line_color": "gray",  # O el color que prefieras para la losa
        "line_width": 1,
        "dash": None,
        "fill_color": "white",
        "legend": True,  # ¡Importante para que aparezca en la leyenda!
    },
    "Pasadizo": {
        "line_color": "gray",  # O el color que prefieras para la losa
        "line_width": 1,
        "dash": None,
        "fill_color": "white",
        "legend": False,  # ¡Importante para que aparezca en la leyenda!
    },
    "Sala de Usos Múltiples": {
        "line_color": "orange",  # O el color que prefieras para la losa
        "line_width": 1,
        "dash": None,
        "fill_color": "orange",
        "legend": True,  # ¡Importante para que aparezca en la leyenda!
    },
    # NUEVOS
    "AUDITORIO MULTIUSOS": {
        "line_color": "darkorange",
        "line_width": 1,
        "dash": None,
        "fill_color": "darkorange",
        "legend": True,
    },
    "COCINA ESCOLAR": {
        "line_color": "honeydew",
        "line_width": 1,
        "dash": None,
        "fill_color": "honeydew",
        "legend": True,
    },
    "COCINA INICIAL": {
        "line_color": "honeydew",
        "line_width": 1,
        "dash": None,
        "fill_color": "honeydew",
        "legend": True,
    },
    "COCINA PRIM - SEC": {
        "line_color": "honeydew",
        "line_width": 1,
        "dash": None,
        "fill_color": "honeydew",
        "legend": True,
    },
    "DIRECCIÓN ADMINISTRATIVA": {
        "line_color": "beige",
        "line_width": 1,
        "dash": None,
        "fill_color": "beige",
        "legend": True,
    },
    "DIRECCION ADM.": {
        "line_color": "beige",
        "line_width": 1,
        "dash": None,
        "fill_color": "beige",
        "legend": True,
    },
    "PATIO INICIAL": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": "gray",
        "legend": True,
    },
    "Patio Primaria Secundaria": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightgray",
        "legend": True,
    },
    "LOSA DEPORTIVA": {
        "line_color": "gray",
        "line_width": 1,
        "dash": None,
        "fill_color": "white",
        "legend": True,
    },
    "SALA DE REUNIONES": {
        "line_color": "khaki",
        "line_width": 1,
        "dash": None,
        "fill_color": "khaki",
        "legend": True,
    },
    "LACTARIO": {
        "line_color": "mistyrose",
        "line_width": 1,
        "dash": None,
        "fill_color": "mistyrose",
        "legend": True,
    },
    "TOPICO": {
        "line_color": "lightcyan",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightcyan",
        "legend": True,
    },
    "SALA DE PSICOMOTRICIDAD": {
        "line_color": "thistle",
        "line_width": 1,
        "dash": None,
        "fill_color": "thistle",
        "legend": True,
    },
    "SALA DE MAESTROS": {
        "line_color": "ivory",
        "line_width": 1,
        "dash": None,
        "fill_color": "ivory",
        "legend": True,
    },
    "SALA DE PROFESORES": {
        "line_color": "ivory",
        "line_width": 1,
        "dash": None,
        "fill_color": "ivory",
        "legend": True,
    },
    "BIBLIOTECA": {
        "line_color": "lightgreen",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightgreen",
        "legend": True,
    },
    "TALLER CREATIVO": {
        "line_color": "lightyellow",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightyellow",
        "legend": True,
    },
    "TALLER CREATIVO SEC": {
        "line_color": "lightyellow",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightyellow",
        "legend": True,
    },
    "TALLER CREATIVO PRIM": {
        "line_color": "lightyellow",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightyellow",
        "legend": True,
    },
    "TALLER EPT": {
        "line_color": "gold",
        "line_width": 1,
        "dash": None,
        "fill_color": "gold",
        "legend": True,
    },
    "AREA DE ESPERA": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "ÁREA DE ESPERA": {
        "line_color": "lavender",
        "line_width": 1,
        "dash": None,
        "fill_color": "lavender",
        "legend": True,
    },
    "AREA DE INGRESO": {
        "line_color": "gainsboro",
        "line_width": 1,
        "dash": None,
        "fill_color": "gainsboro",
        "legend": True,
    },
    "AULA DE INNOVACION SEC": {
        "line_color": "green",
        "line_width": 1,
        "dash": None,
        "fill_color": "green",
        "legend": True,
    },
    "AULA DE INNOVACION PRIM": {
        "line_color": "green",
        "line_width": 1,
        "dash": None,
        "fill_color": "green",
        "legend": True,
    },
    "LABORATORIO": {
        "line_color": "mediumaquamarine",
        "line_width": 1,
        "dash": None,
        "fill_color": "mediumaquamarine",
        "legend": True,
    },
    # -------------------------------------------------------------------------
    # SERVICIOS HIGIÉNICOS (SSHH)
    # -------------------------------------------------------------------------
    "SSHH SEC - HOMBRES": {
        "line_color": "powderblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "powderblue",
        "legend": True,
    },
    "SSHH SEC - MUJERES": {
        "line_color": "pink",
        "line_width": 1,
        "dash": None,
        "fill_color": "pink",
        "legend": True,
    },
    "SSHH PRIM - HOMBRES": {
        "line_color": "powderblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "powderblue",
        "legend": True,
    },
    "SSHH PRIM - MUJERES": {
        "line_color": "pink",
        "line_width": 1,
        "dash": None,
        "fill_color": "pink",
        "legend": True,
    },
    "SSHH INICIAL - HOMBRES": {
        "line_color": "powderblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "powderblue",
        "legend": True,
    },
    "SSHH INICIAL - MUJERES": {
        "line_color": "pink",
        "line_width": 1,
        "dash": None,
        "fill_color": "pink",
        "legend": True,
    },
    "SSHH ADM. - HOMBRES": {
        "line_color": "lightblue",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightblue",
        "legend": True,
    },
    "SSHH ADM. - MUJERES": {
        "line_color": "lightpink",
        "line_width": 1,
        "dash": None,
        "fill_color": "lightpink",
        "legend": True,
    },
    # [Ambiente_1 1] SUM
    # # Patio Primaria Secundaria
    "DEFAULT": {
        "line_color": None,
        "line_width": None,
        "dash": None,
        "fill_color": None,
        "legend": False,
    },
}


def obtener_estilo(nombre):
    print(f"[DEBUG RENDER] Buscando estilo para el componente: '{nombre}'")
    # Para evitar que "Losa" gane a "Patio Inicial", priorizamos las palabras clave de ambientes/leyendas
    # Primero buscamos coincidencias con los estilos que SÍ llevan leyenda (prioritarios)
    for clave, estilo in ESTILOS.items():
        if estilo["legend"] and clave in nombre:
            print(
                f"  -> Coincidencia encontrada (con leyenda): '{clave}'. Aplicando estilo."
            )
            return estilo

    # Si no es un ambiente con leyenda, buscamos en los elementos estructurales comunes (muros, losas, etc.)
    for clave, estilo in ESTILOS.items():
        if not estilo["legend"] and clave in nombre:
            print(
                f"  -> Coincidencia encontrada (sin leyenda): '{clave}'. Aplicando estilo."
            )
            return estilo

    print(
        f"  -> No se encontró coincidencia para '{nombre}'. Se usará el estilo por defecto."
    )
    return ESTILOS["DEFAULT"]


def render_2d(escena):

    fig = go.Figure()

    for nombre, geometria in escena.items():

        estilo = obtener_estilo(nombre)

        vertices = np.array(geometria["vertices"])
        faces_input = geometria["faces"]

        pts = vertices[:, :2]

        edges = defaultdict(int)

        # [DOCUMENTACIÓN] Mapeo de coordenadas de caras (tuplas 3D) a índices de vértices
        # para compatibilidad con la serialización moderna de CadQuery.
        coord_to_idx = {tuple(v): idx for idx, v in enumerate(geometria["vertices"])}

        faces_indices = []
        for face_poly in faces_input:
            face_idx = []
            for pt in face_poly:
                pt_tuple = tuple(pt)
                if pt_tuple in coord_to_idx:
                    face_idx.append(coord_to_idx[pt_tuple])
                else:
                    closest_idx = min(
                        range(len(vertices)),
                        key=lambda i: sum(
                            (vertices[i][k] - pt[k]) ** 2 for k in range(3)
                        ),
                    )
                    face_idx.append(closest_idx)
            # Solo consideramos caras triangulares para lados (o tomamos los primeros 3)
            if len(face_idx) >= 3:
                faces_indices.append(face_idx[:3])

        for cara in faces_indices:

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
        if "Base Cuadrante" in nombre or "Terreno" in nombre:
            elementos_globales.append((nombre, coleccion))
            continue

        coincidencia = re.search(r"(Nivel\s+\d+)", nombre)

        if coincidencia:
            nivel = coincidencia.group(1)
        else:
            nivel = "Otros"
            continue

        if nivel not in elementos_por_nivel:
            elementos_por_nivel[nivel] = []

        elementos_por_nivel[nivel].append((nombre, coleccion))

    # 2. Inyección de elementos globales
    if not elementos_por_nivel and elementos_globales:
        elementos_por_nivel["General"] = []

    for nivel in elementos_por_nivel.keys():
        elementos_por_nivel[nivel].extend(elementos_globales)

    graficos_por_nivel = {}

    # 3. Generación de gráficos con agrupación de leyendas
    for nivel, elementos in elementos_por_nivel.items():
        fig = go.Figure()

        # --- NUEVA LÓGICA DE AGRUPACIÓN CORREGIDA ---
        # 1. Obtenemos el nombre base sin números al final para poder agruparlos
        # Ej: "Aulas Primaria 4" -> "Aulas Primaria"
        nombres_base_por_elemento = []
        conteos_ambientes = {}

        for nombre, coleccion in elementos:
            nombre_limpio = extraer_nombre_ambiente(nombre)
            # Removemos espacios y números que estén al final de la cadena
            nombre_base = re.sub(r"\s+\d+$", "", nombre_limpio).strip()

            nombres_base_por_elemento.append((nombre, coleccion, nombre_base))
            conteos_ambientes[nombre_base] = conteos_ambientes.get(nombre_base, 0) + 1

        # Diccionario para acumular las coordenadas bajo su nombre base
        grupos_graficos = {}

        for nombre, coleccion, nombre_base in nombres_base_por_elemento:
            estilo = obtener_estilo(nombre)

            nombre_final = nombre

            # Verificamos si cumple con la condición específica

            # Patio Primaria Secundaria
            if "Losa Pasadizo Patio Inicial" in nombre and "Nivel 1" in nombre:
                nombre_final = "Patio Inicial"
                # Opcional: si quieres que el nombre_base también cambie para el conteo:
                nombre_base = "Patio Inicial"

            elif "[Ambiente_1 1] SUM" in nombre and "Nivel 1" in nombre:
                nombre_final = "Sala de Usos Múltiples (SUM)"
                # Opcional: si quieres que el nombre_base también cambie para el conteo:
                nombre_base = "Sala de Usos Múltiples (SUM)"

            elif (
                "Losa Pasadizo Patio Primaria Secundaria" in nombre
                and "Nivel 1" in nombre
            ):
                nombre_final = "Losa Deportiva"
                # Opcional: si quieres que el nombre_base también cambie para el conteo:
                nombre_base = "Losa Deportiva"
            # --------------------------------

            estilo = obtener_estilo(nombre_final)  # Usamos el nombre modificado

            # Formateamos la leyenda usando el nombre_base actualizado
            cantidad = conteos_ambientes.get(nombre_base, 1)
            nombre_leyenda = (
                f"{nombre_base} ({cantidad})" if cantidad > 1 else nombre_base
            )

            # Extraemos las coordenadas de la colección Shapely
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

            # Inicializamos el grupo si no existe
            if nombre_leyenda not in grupos_graficos:
                grupos_graficos[nombre_leyenda] = {"x": [], "y": [], "estilo": estilo}

            grupos_graficos[nombre_leyenda]["x"].extend(x_lines)
            grupos_graficos[nombre_leyenda]["y"].extend(y_lines)

            # Dibujamos el fondo (fill) de forma individual si corresponde
            if estilo["fill_color"] and not coleccion.is_empty:
                for geom in coleccion.geoms:
                    if geom.geom_type == "Polygon":
                        x_fill, y_fill = geom.exterior.xy
                        fig.add_trace(
                            go.Scatter(
                                x=list(x_fill),
                                y=list(y_fill),
                                fill="toself",
                                fillcolor=estilo["fill_color"],
                                mode="lines",
                                line=dict(color="rgba(0,0,0,0)", width=0),
                                legendgroup=nombre_leyenda,
                                showlegend=False,
                                hoveron="fills",
                                hovertemplate=f"<b>{nombre}</b><extra></extra>",
                            )
                        )

        # Añadimos un ÚNICO trazo de línea por cada grupo acumulado
        for nombre_leyenda, datos in grupos_graficos.items():
            estilo = datos["estilo"]
            fig.add_trace(
                go.Scatter(
                    x=datos["x"],
                    y=datos["y"],
                    mode="lines",
                    line=dict(
                        color=estilo["line_color"],
                        width=estilo["line_width"],
                        dash=estilo["dash"],
                    ),
                    name=nombre_leyenda,  # Mostrará: "Aulas Primaria (6)"
                    showlegend=estilo["legend"],
                )
            )
        # --------------------------------------------

        # Título y diseño dinámico para el gráfico actual
        fig.update_layout(
            title=f"Render 2D - {nivel}",
            yaxis_scaleanchor="x",
            template="plotly_white",
            xaxis=dict(showgrid=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, showticklabels=False, visible=False),
        )

        graficos_por_nivel[nivel] = fig

    return graficos_por_nivel


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
