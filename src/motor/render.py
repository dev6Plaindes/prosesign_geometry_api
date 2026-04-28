import plotly.graph_objects as go
from shapely import wkt
import pandas as pd
import numpy as np

class Render:
    def __init__(self, data=None, pisos=1):
        self.data = data if data is not None else []
        self.data_render = []
        self.pisos = pisos

    def convert_data(self):
        data_convert = []
        for registro in self.data:
            wkt_string = registro.get("geometria")

            if hasattr(wkt_string, 'exterior'):
                data_convert.append(registro)
                continue

            if isinstance(wkt_string, str) and wkt_string.strip():
                try:
                    poligono_recuperado = wkt.loads(wkt_string)
                    registro["geometria"] = poligono_recuperado
                    data_convert.append(registro)
                except Exception as e:
                    print(f"Error al cargar WKT: {e}")

        self.data_render = data_convert
        return data_convert

    def render_2d(self):
        lista_a_dibujar = self.convert_data()
        figuras_html = ""

        for nivel_actual in range(1, int(self.pisos) + 1):
            fig = go.Figure()
            hay_datos_en_piso = False

            for registro in lista_a_dibujar:
                # 1. Extraer tipo y descripción primero
                tipo = registro.get('tipo')
                descripcion = registro.get("description", "Objeto")
                
                piso_registro = None 
                val_piso = registro.get("piso") 

                if isinstance(val_piso, (list, np.ndarray)):
                    if len(val_piso) > 0 and not pd.isna(val_piso).all():
                        piso_registro = max(val_piso)
                elif pd.notnull(val_piso):
                    piso_registro = val_piso

                # 2. FILTRO EXPANDIDO:
                # Se dibuja si:
                # - Es del piso actual
                # - O es tipo 'max_rect'
                # - O su descripción es 'Render'
                es_siempre_visible = (tipo == "max_rect" or descripcion == "Render")
                
                if piso_registro != nivel_actual and not es_siempre_visible:
                    continue

                hay_datos_en_piso = True
                x, y = registro["geometria"].exterior.xy

                scatter_params = dict(
                    x=list(x), y=list(y), fill="toself", mode='lines'
                )
                
                # Lógica de leyenda mejorada
                if_showlengd = "techo" in descripcion.lower()
                if_showlengd = not if_showlengd

                # 3. RENDERIZADO
                if tipo == "muro":
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor="rgba(200, 200, 200, 0.5)",
                                            line=dict(color="black", width=1), showlegend=False))
                elif tipo == "columna":
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor="black",
                                            line=dict(color="black", width=1), showlegend=False))
                elif tipo == "ventana":
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor="gray",
                                            line=dict(color="black", width=1), showlegend=False))
                elif tipo == "techo":
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor="gray",
                                            line=dict(color="black", width=1), showlegend=False))
                elif tipo == "max_rect":
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor="rgba(200, 200, 200, 0.0)",
                                            line=dict(color="black", width=1, dash="dash"), 
                                            name="Límite Terreno", showlegend=False))
                else:
                    # Aquí caen los "Render" y otros ambientes
                    # Si es Render, podrías querer un estilo específico, si no, usa el default:
                    fill_color = "rgba(50, 50, 50, 0.0)" if descripcion == "Render" else "rgba(255, 255, 255, 0.2)"
                    
                    fig.add_trace(go.Scatter(**scatter_params, fillcolor=fill_color,
                                            line=dict(color="gray", width=1),
                                            name=descripcion, showlegend=if_showlengd))

            if hay_datos_en_piso:
                fig.update_layout(
                    title=f"Plano de Planta - Piso {nivel_actual}",
                    plot_bgcolor='white',
                    xaxis=dict(scaleanchor="y", scaleratio=1, showgrid=True, gridcolor='lightgray'),
                    yaxis=dict(showgrid=True, gridcolor='lightgray'),
                    showlegend=True
                )
                figuras_html += fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return figuras_html
    
    def render_3d(self):
        # 1. Aseguramos que los datos base estén listos
        self.convert_data()
        
        fig = go.Figure()

        for registro in self.data:
            geo_3d = registro.get('geometria_3d')
            
            # Validamos que exista la geometría 3D y que sea un diccionario
            if not isinstance(geo_3d, dict) or 'x' not in geo_3d:
                continue

            tipo = registro.get('tipo', 'default')
            color = "gray"
            opacity = 1.0

            # Definición de colores 3D por tipo
            if tipo == "muro":
                color = "gray"
                opacity = 1.0
            
            elif tipo == "losa":
                color = "gray"
                opacity = 1.0
            
            elif tipo == "escalera":
                color = "lightgray"
                opacity = 1.0
            
            elif tipo == "descanso":
                color = "lightgray"
                opacity = 1.0
            
            elif tipo == "pasadizo":
                color = "lightgray"
                opacity = 1.0

            elif tipo == "columna":
                color = "black"
                opacity = 1.0
            
            elif tipo == "ventana":
                color = "white"
                opacity = 1.0

            elif tipo == "aula":
                color = "rgba(100, 149, 237, 0.4)" # Azul translúcido
                opacity = 0.3

            # Usamos Mesh3d para crear el volumen
            # alphahull=0 crea una malla cerrada (convex hull) alrededor de los puntos
            fig.add_trace(go.Mesh3d(
                x=geo_3d['x'],
                y=geo_3d['y'],
                z=geo_3d['z'],
                alphahull=0, 
                color=color,
                opacity=opacity,
                name=registro.get('description', tipo),
                flatshading=True # Para que las aristas se vean más definidas
            ))

        # Configuración de la escena 3D
        fig.update_layout(
            title="Renderizado 3D",
            scene=dict(
                # xaxis_title='X (Largo)',
                # yaxis_title='Y (Ancho)',
                # zaxis_title='Z (Altura)',
                aspectmode='data' # Importante: mantiene las proporciones reales
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )

        return fig
    
# # Ejecución

# data_dict_transformada = df_geom_to_dict(data_transformada)

# data_complete = terreno_poly_dict + data_dict_transformada
# render = Render(data_complete, pisos=3)
# render.render_2d()