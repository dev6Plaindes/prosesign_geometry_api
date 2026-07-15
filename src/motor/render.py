import math

import plotly.graph_objects as go
from shapely import wkt
import pandas as pd
import numpy as np
import os

config_3d = {
            "max_rect": {
                "color": "rgb(32,39,45)",
                "opacity": 1.0,
            },
            "muro": {
                "color": "lightgray",
                "opacity": 1.0,
            },
            "techo": {
                "color": "rgb(55,57,54)",
                "opacity": 1.0
            },
            "losa": {
                "color": "green",
                "opacity": 1.0
            },
            "escalera": {
                "color": "lightgray",
                "opacity": 1.0
            },
            "descanso": {
                "color": "lightgray",
                "opacity": 1.0
            },
            "pasadizo": {
                "color": "gray",
                "opacity": 1.0
            },
            "columna": {
                "color": "gray",
                "opacity": 1.0,
                "border" : True
            },
            "viga": {
                "color": "gray",
                "opacity": 1.0
            },
            "parapeto": {
                "color": "gray",
                "opacity": 1.0,
                "border" : True
            },
            "ventana": {
                "color": "black",
                "opacity": 0.5,
            },
            "puerta": {
                "color": "rgb(52,30,17)",
                "opacity": 1.0,
            },
            "aula": {
                "color": "rgba(100, 149, 237, 0.4)",
                "opacity": 0.3
            }
        }
class Render:
    def __init__(self, data=None, pisos=1):
        self.data = data if data is not None else []
        self.data_render = []
        self.pisos = pisos

    def convert_data(self):
        data_convert = []
        for registro in self.data:
            wkt_string = registro.get("geometria")
            tipo = registro.get("tipo", "default")

            # 1. Si ya es un objeto geométrico (tiene el atributo 'exterior')
            if hasattr(wkt_string, 'exterior'):
                poligono = wkt_string
                data_convert.append(registro)
            
            # 2. Si viene como un string WKT, lo parseamos con la librería shapely/wkt
            elif isinstance(wkt_string, str) and wkt_string.strip():
                try:
                    poligono = wkt.loads(wkt_string)
                    registro["geometria"] = poligono
                    data_convert.append(registro)
                except Exception as e:
                    print(f"Error al cargar WKT: {e}")
                    continue
            else:
                # Si no cumple ninguna condición, saltamos este registro
                continue

            # --- TRATAMIENTO ESPECIAL PARA MAX_RECT ---
            if tipo == 'max_rect' and hasattr(poligono, 'exterior'):
                try:
                    # Extraemos las listas de coordenadas X e Y del polígono plano
                    x_base, y_base = poligono.exterior.xy
                    x_base = list(x_base)
                    y_base = list(y_base)
                    
                    # Duplicamos los vértices para modelar la base y la tapa superior en el espacio 3D
                    x_3d = x_base + x_base
                    y_3d = y_base + y_base
                    
                    # Generamos los valores de Z: la base en -0.1 y el techo en 0.0 (alto de 0.1)
                    z_3d = [-0.1] * len(x_base) + [0.0] * len(x_base)
                    
                    # Estructuramos la geometría 3D requerida por el renderizador
                    registro['geometria_3d'] = {
                        'x': x_3d,
                        'y': y_3d,
                        'z': z_3d
                    }
                except Exception as e:
                    print(f"Error al procesar la geometría 3D de max_rect: {e}")
            # ------------------------------------------

        self.data_render = data_convert
        return data_convert
    
    
    def get_configuracion(self, tipo, descripcion):
        desc = descripcion.lower()

        # PRIORIDAD: por tipo
        if tipo == "muro":
            return dict(fill="rgba(200,200,200,0.5)", line="black", legend=False)

        if tipo == "columna":
            return dict(fill="black", line="black", legend=False)

        if tipo == "ventana":
            return dict(fill="gray", line="black", legend=False)

        if tipo == "techo":
            return dict(fill="gray", line="black", legend=False)

        if tipo == "max_rect":
            return dict(
                fill="rgba(0,0,0,0)",
                line="black",
                dash="dash",
                legend_name="Area de Terreno",
                legend_color="blue"
            )

        # PRIORIDAD: por descripción
        mapping = [
            ("aula", "green"),
            ("sshh", "yellow"),
            ("tópico", "brown"),
            ("lactario", "orange"),
            ("cocina", "cyan"),
            ("patio", "gray"),
            ("pasadizo", "gray"),
            ("sum", "lime"),
            ("render", "gold"),
            ("dirección adm.", "royalblue"),
            ("área de espera", "orange"),
            ("sala de reuniones", "green"),
            ("área de ingreso", "red"),
            ("sala de profesores", "purple"),
            ("biblioteca", "black"),
        ]

        for key, color in mapping:
            if key in desc:
                return dict(
                    fill="rgba(0,0,0,0)",
                    line="black",
                    dash="dash",
                    legend_name=descripcion,
                    legend_color=color
                )

        # DEFAULT
        return dict(
            fill="rgba(255,255,255,0.2)",
            line="gray",
            legend=True
        )
    def render_2d(self, html=False):

        lista = self.convert_data()

        figuras_html = ""

        # ==========================================
        # CONFIG ESTILOS
        # ==========================================
        estilos = {

            "aula_ciclo": dict(
                fillcolor="rgba(34,139,34,0.10)",
                line_color="green",
                line_width=1,
                showlegend=True
            ),

            "aula": dict(
                fillcolor="rgba(255,165,0,0.08)",
                line_color="orange",
                line_width=1,
                showlegend=True
            ),

            "sshh": dict(
                fillcolor="rgba(0,150,255,0.08)",
                line_color="blue",
                line_width=1,
                showlegend=True
            ),

            "pasadizo": dict(
                fillcolor="rgba(120,120,120,0.06)",
                line_color="gray",
                line_width=1,
                showlegend=False
            ),

            "patio": dict(
                fillcolor="rgba(150,150,150,0.04)",
                line_color="gray",
                line_width=1,
                showlegend=False
            ),

            "muro": dict(
                fill=None,
                line_color="black",
                line_width=1.5,
                showlegend=False
            ),
            "arco": dict(
                fill=None,
                line_color="black",
                line_width=2,
                showlegend=False
            ),
            "puerta": dict(
                fill=None,
                line_color="blue",
                line_width=2,
                showlegend=False
            ),

            "columna": dict(
                fillcolor="black",
                line_color="black",
                line_width=1,
                showlegend=False
            ),

            "viga": dict(
                fill=None,
                line_color="black",
                line_width=1,
                dash="dash",
                showlegend=False
            ),

            "render": dict(
                fillcolor="rgba(255,215,0,0.03)",
                line_color="orange",
                line_width=2,
                showlegend=True
            ),

            "max_rect": dict(
                fillcolor="rgba(0,150,255,0.03)",
                line_color="blue",
                line_width=2,
                dash="dash",
                showlegend=True
            )
        }

        # ==========================================
        # LOOP PISOS
        # ==========================================
        for nivel in range(1, int(self.pisos) + 1):

            fig = go.Figure()

            hay_datos = False

            for reg in lista:

                geom = reg.get("geometria")

                if geom is None:
                    continue

                tipo = str(
                    reg.get("tipo", "")
                ).lower()

                desc_original = str(reg.get("description", "Sin nombre"))
                desc = desc_original.lower()

                piso = reg.get("piso")

                # ==================================
                # FILTRO PISO
                # ==================================
                visible_global = (
                    tipo == "render"
                    or tipo == "max_rect"
                )

                if (
                    piso != nivel
                    and not visible_global
                ):
                    continue

                hay_datos = True

                # ==================================
                # GEOMETRÍA
                # ==================================
                try:

                    x, y = geom.exterior.xy

                except Exception:
                    continue

                # ==================================
                # CLASIFICACIÓN
                # ==================================
                categoria = "default"

                if tipo == "muro":
                    categoria = "muro"

                elif tipo == "columna":
                    categoria = "columna"

                elif tipo == "viga":
                    categoria = "viga"

                elif tipo == "max_rect":
                    categoria = "max_rect"
                    
                elif tipo == "arco":
                    categoria = "arco"

                elif tipo == "render":
                    categoria = "render"

                elif "pasadizo" in desc:
                    categoria = "pasadizo"

                elif "patio" in desc:
                    categoria = "patio"

                elif "sshh" in desc:
                    categoria = "sshh"

                elif "aula ciclo" in desc:
                    categoria = "aula_ciclo"

                elif "aula" in desc:
                    categoria = "aula"

                estilo = estilos.get(
                    categoria,
                    {}
                )

                # ==================================
                # SCATTER BASE
                # ==================================
                scatter = dict(

                    x=list(x),
                    y=list(y),

                    mode="lines",

                    line=dict(
                        color=estilo.get(
                            "line_color",
                            "gray"
                        ),
                        width=estilo.get(
                            "line_width",
                            1
                        ),
                        dash=estilo.get(
                            "dash",
                            "solid"
                        )
                    ),
                    name=desc_original,

                    fill=(
                        "toself"
                        if estilo.get("fillcolor")
                        else None
                    ),

                    fillcolor=estilo.get(
                        "fillcolor",
                        None
                    ),

                    showlegend=estilo.get(
                        "showlegend",
                        False
                    ),

                    hoverinfo="name"
                )

                # ==================================
                # WEBGL
                # ==================================
                fig.add_trace(
                    go.Scattergl(
                        **scatter
                    )
                )

            # ======================================
            # LAYOUT
            # ======================================
            if hay_datos:

                fig.update_layout(

                    title=f"Piso {nivel}",

                    plot_bgcolor="white",

                    showlegend=True,

                    xaxis=dict(
                        visible=False
                    ),

                    yaxis=dict(
                        visible=False,
                        scaleanchor="x",
                        scaleratio=1
                    ),

                    margin=dict(
                        l=5,
                        r=5,
                        t=40,
                        b=5
                    )
                )

                if html:

                    figuras_html += f"""
                    <div style="
                        width:75vw;
                        margin-bottom:20px;
                    ">
                        {
                            fig.to_html(
                                full_html=False,
                                include_plotlyjs='cdn'
                            )
                        }
                    </div>
                    """

        if html:
            return figuras_html

        return fig

    def get_config_3d(self, tipo):
        return config_3d.get(tipo, {"color": "gray", "opacity": 1.0})
    
    def render_3d(self, html=False):
        # 1. Aseguramos que los datos base estén listos
        self.convert_data()
        
        fig = go.Figure()
        
        legend_items = {
            "Area de Terreno": "blue",
            "Aula": "green",
            "SSHH": "yellow",
            "Tópico": "brown",
            "Lactario": "orange",
            "Cocina": "cyan",
            "Patio": "gray",
            "Pazadiso": "gray",
            "SUM": "lime",
            "Cuadrante": "gold",
            "Dirección Adm.": "royalblue",
            "Área de espera": "orange",
            "Sala de Reuniones": "green",
            "Área de ingreso": "red",
            "Sala de Profesores": "purple",
            "Biblioteca": "black"
        }

        for registro in self.data:
            geo_3d = registro.get('geometria_3d')
            
            # Validamos que exista la geometría 3D y que sea un diccionario
            if not isinstance(geo_3d, dict) or 'x' not in geo_3d:
                continue

            tipo = registro.get('tipo', 'default')
            config = self.get_config_3d(tipo)
            color = "gray"
            opacity = 1.0
            border = config.get("border", False)
            
            if tipo != "default":
                color = config.get("color", "gray")
                opacity = config.get("opacity", 1.0)

            fig.add_trace(go.Mesh3d(
                x=geo_3d['x'],
                y=geo_3d['y'],
                z=geo_3d['z'],
                alphahull=0, 
                color=color,
                opacity=opacity,
                name=registro.get('description', tipo),
                flatshading=True
            ))
            
            if border:
                
                fig.add_trace(go.Scatter3d(
                    x=geo_3d['x'],
                    y=geo_3d['y'],
                    z=geo_3d['z'],
                    mode='lines',
                    line=dict(color="black", width=3),
                    showlegend=False
                ))

        # Configuración de la escena 3D
        fig.update_layout(
            title="Renderizado 3D",
            scene=dict(
                xaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=False, 
                    title='', 
                    visible=False
                ),
                yaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=False, 
                    title='', 
                    visible=False
                ),
                zaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=False, 
                    title='', 
                    visible=False
                ),
                aspectmode='data'
            ),
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        for name, color in legend_items.items():
            self.add_legend_item(fig, name, color)

        plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        figuras_html = f"""
        <div style="width: 75vw; border-radius: 8px; margin-bottom: 20px; padding-right: 300px">
            {plotly_html}
        </div>
                """
        if html:
            return figuras_html
        
        return fig
    
    
    def add_legend_item(self, fig, name, color):
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode='markers',
            marker=dict(size=10, color=color, symbol='square'),
            name=name,
            showlegend=True
        ))
    
# # Ejecución

# data_dict_transformada = df_geom_to_dict(data_transformada)

# data_complete = terreno_poly_dict + data_dict_transformada
# render = Render(data_complete, pisos=3)
# render.render_2d()


def save_render_image(fig, filename="render.png", folder="renders", tipo="3d"):
    """
    Guarda un Figure de Plotly como imagen PNG.
    """

    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, tipo + "_" + filename)
    
    if tipo == "3d":
        # --- PARÁMETROS INTUITIVOS ---
        angulo_grados = 60  # Ángulo de rotación en Z (por defecto Plotly usa 45)
        distancia = 3     # Controla el zoom. Mayor número = MENOS zoom (más lejos)
        altura_z = 1.4      # Qué tan arriba está la cámara mirando hacia abajo

        # Convertimos el ángulo a radianes para las funciones trigonométricas
        angulo_rad = math.radians(angulo_grados)

        # Calculamos las posiciones X e Y exactas usando seno y coseno
        nuevo_x = distancia * math.cos(angulo_rad)
        nuevo_y = distancia * math.sin(angulo_rad)

        # Aplicamos los cambios a tu figura
        fig.update_layout(
            scene_camera=dict(
                eye=dict(
                    x=nuevo_x,
                    y=nuevo_y,
                    z=altura_z
                )
            )
        )

    fig.write_image(
        path,
        format="png",
        width=1920,
        height=1080,
        scale=2
    )

    return path

