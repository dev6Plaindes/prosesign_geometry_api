import plotly.graph_objects as go
import pandas as pd

def dibujar_geometrias(df):
    fig = go.Figure()

    # 1. Crear columna de descripción de forma segura (evita NaN)
    def obtener_nombre(f):
        # Intenta buscar en este orden, si no, usa el tipo, si no, 'Desconocido'
        val = f.get("description") or f.get("nombre") or f.get("tipo") or "Indefinido"
        return str(val)

    # Creamos la serie de descripciones asegurando que sean Strings
    temp_desc = df.apply(obtener_nombre, axis=1)
    conteo_desc = temp_desc.value_counts()
    
    # 2. Elementos a ignorar en la leyenda
    excluir_de_leyenda = ["muro", "columna", "puerta", "ventana", "render", "area", "indefinido"]

    categorias_en_leyenda = set()

    for i, (idx, fila) in enumerate(df.iterrows()):
        geom = fila["geometria"]
        tipo = str(fila.get("tipo", "otro")).lower()
        descripcion = temp_desc.iloc[i] # Usamos iloc para coincidir con el orden del loop
        
        cantidad = conteo_desc.get(descripcion, 0)
        nombre_leyenda = f"{descripcion} ({cantidad})"

        color = "gray"
        fill = None
        alpha = 1
        dash = "solid"

        # --- TUS COLORES ORIGINALES ---
        if "render" in tipo:
            color = "black"
        elif "area" in tipo:
            color = "black"; dash = "dash"
        elif "aula" in tipo:
            color = "gray"; fill = "gray"; alpha = 0.4
        elif "losa" in tipo:
            color = "gray"; fill = "lightgray"; alpha = 0.5
        elif "pasadizo" in tipo:
            color = "gray"; fill = "gray"; alpha = 0.3
        elif any(x in tipo for x in ["muro", "columna"]):
            color = "black"; fill = "black"; alpha = 0.8
        elif tipo.startswith("puerta"):
            color = "black"
        elif "ventana" in tipo:
            color = "white"; fill = "skyblue"; alpha = 0.7

        # --- FILTRO LEYENDA ---
        mostrar_en_leyenda = False
        if not any(ex in tipo for ex in excluir_de_leyenda):
            if descripcion not in categorias_en_leyenda:
                mostrar_en_leyenda = True
                categorias_en_leyenda.add(descripcion)

        # 🧱 DIBUJO (Simplificado para brevedad, aplica a todos los tipos)
        if geom.geom_type == "Polygon":
            x, y = geom.exterior.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                mode="lines",
                line=dict(color=color, width=1.5, dash=dash),
                fill="toself" if fill and "area" not in tipo else None,
                fillcolor=fill,
                opacity=alpha,
                name=nombre_leyenda,
                legendgroup=descripcion,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text",
                hovertemplate="<b>%{text}</b><extra></extra>"
            ))
        elif geom.geom_type == "Point":
            fig.add_trace(go.Scatter(
                x=[geom.x], y=[geom.y],
                mode="markers",
                marker=dict(color=color, size=6),
                name=nombre_leyenda,
                legendgroup=descripcion,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text"
            ))
        elif geom.geom_type == "LineString":
            x, y = geom.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                mode="lines",
                line=dict(color=color, width=2),
                name=nombre_leyenda,
                legendgroup=descripcion,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text"
            ))

    # 🔧 CONFIG FINAL
    fig.update_layout(
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        width=1100, height=700,
        showlegend=True,
        legend=dict(x=1.02, bordercolor="Gray", borderwidth=1)
    )

    return fig

import plotly.graph_objects as go
import pandas as pd

def dibujar_geometrias_por_piso(df, piso_seleccionado):
    fig = go.Figure()

    # Función para obtener un nombre seguro
    def obtener_nombre(f):
        val = f.get("description") or f.get("nombre") or f.get("tipo") or "Indefinido"
        return str(val)

    df["desc"] = df.apply(obtener_nombre, axis=1)
    df["piso"] = df.get("piso", "General")  # Elementos sin piso se consideran 'General'

    excluir_de_leyenda = ["muro", "columna", "puerta", "ventana", "area", "indefinido"]
    categorias_en_leyenda = set()

    # Filtramos los elementos:
    # - del piso seleccionado
    # - o tipo render
    # - o tipo terreno (siempre se muestra)
    df_filtrado = df[
        (df["piso"] == piso_seleccionado) |
        (df["tipo"].str.lower().str.contains("render")) |
        (df["tipo"].str.lower().str.contains("terreno"))
    ]

    conteo_desc = df_filtrado["desc"].value_counts()

    for i, (idx, fila) in enumerate(df_filtrado.iterrows()):
        geom = fila["geometria"]
        tipo = str(fila.get("tipo", "otro")).lower()
        descripcion = fila["desc"]
        cantidad = conteo_desc.get(descripcion, 0)

        # Nombre en leyenda
        nombre_leyenda = f"{descripcion} ({cantidad})"

        # Colores y estilos
        color, fill, alpha, dash = "gray", None, 1, "solid"
        if "render" in tipo:
            color = "black"
        elif "area" in tipo:
            color, dash = "black", "dash"
        elif "aula" in tipo:
            color, fill, alpha = "gray", "gray", 0.4
        elif "losa" in tipo:
            color, fill, alpha = "gray", "lightgray", 0.5
        elif "pasadizo" in tipo:
            color, fill, alpha = "gray", "gray", 0.3
        elif any(x in tipo for x in ["muro", "columna"]):
            color, fill, alpha = "black", "black", 0.8
        elif tipo.startswith("puerta"):
            color = "black"
        elif "ventana" in tipo:
            color, fill, alpha = "white", "skyblue", 0.7
        elif "terreno" in tipo:
            color, dash = "black", "dash"

        # Leyenda
        mostrar_en_leyenda = False
        key_leyenda = f"{fila['piso']}_{descripcion}"

        # Siempre mostrar terrenos y render, otros según regla
        if "terreno" in tipo or "render" in tipo:
            mostrar_en_leyenda = True
            categorias_en_leyenda.add(key_leyenda)
        elif not any(ex in tipo for ex in excluir_de_leyenda):
            if key_leyenda not in categorias_en_leyenda:
                mostrar_en_leyenda = True
                categorias_en_leyenda.add(key_leyenda)

        # Dibujo según tipo geométrico
        if geom.geom_type == "Polygon":
            x, y = geom.exterior.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                mode="lines",
                line=dict(color=color, width=1.5, dash=dash),
                fill="toself" if fill else None,
                fillcolor=fill,
                opacity=alpha,
                name=nombre_leyenda,
                legendgroup=key_leyenda,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text",
                hovertemplate=f"<br>%{{text}}<extra></extra>"
            ))
        elif geom.geom_type == "Point":
            fig.add_trace(go.Scatter(
                x=[geom.x], y=[geom.y],
                mode="markers",
                marker=dict(color=color, size=6),
                name=nombre_leyenda,
                legendgroup=key_leyenda,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text"
            ))
        elif geom.geom_type == "LineString":
            x, y = geom.xy
            fig.add_trace(go.Scatter(
                x=list(x), y=list(y),
                mode="lines",
                line=dict(color=color, width=2),
                name=nombre_leyenda,
                legendgroup=key_leyenda,
                showlegend=mostrar_en_leyenda,
                text=descripcion,
                hoverinfo="text"
            ))

    # Configuración final
    fig.update_layout(
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        width=1100, height=700,
        showlegend=True,
        legend=dict(x=1.02, bordercolor="Gray", borderwidth=1)
    )

    fig.show()