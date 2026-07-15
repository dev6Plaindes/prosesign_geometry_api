import pandas as pd
from shapely.geometry import Polygon
import plotly.graph_objects as go

class Losa:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="losa", h_entrepiso=0.2, espesor=0.3, z_base=0):
        """
        ancho: dimensión horizontal del losa
        largo: dimensión vertical del losa
        x, y: posición de la esquina inferior izquierda
        piso: nivel en el que se encuentra
        description: nombre o etiqueta del losa
        """
        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.area = ancho * largo
        self.h_entrepiso = h_entrepiso

        self.espesor = espesor
        self.z_suelo = z_base
        self.z_techo = z_base + espesor
        self.z_base = z_base

        # Definición de la geometría usando Polygon de Shapely
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        # usa SOLO un sistema de alturas
        self.z_suelo = self.z_base
        self.z_techo = self.z_base + self.espesor

        x_base, y_base = self.geometria.exterior.xy
        self.x_l, self.y_l = list(x_base), list(y_base)

        self.geometria_3d = {
            'x': self.x_l + self.x_l,
            'y': self.y_l + self.y_l,
            'z': [self.z_suelo]*len(self.x_l) + [self.z_techo]*len(self.x_l)
        }
        
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self._actualizar_geometrias()

    def get_data(self):
        data = {
            "ancho": self.ancho,
            "largo": self.largo,
            "area": self.area,
            "piso": self.piso,
            "description": self.description,
            "geometria": self.geometria,
            "x": self.x,
            "y": self.y,
            "tipo": "losa",
            "subtipo": "estructura",
            "geometria_3d" : self.geometria_3d,
        }

        return [data]

    def draw(self, fig, color="lightgrey", borde="black"):
        """
        Dibuja el pasadizo en la figura de Plotly suministrada.
        color: por defecto gris claro para diferenciarlo de columnas o muros.
        """
        # Extraemos las coordenadas del polígono para Plotly
        x_coords, y_coords = self.geometria.exterior.xy

        fig.add_trace(go.Scatter(
            x=list(x_coords),
            y=list(y_coords),
            fill="toself",
            mode="lines",
            line=dict(color=borde, width=1), # Línea punteada opcional para pasadizos
            fillcolor=color,
            opacity=0.6, # Un poco más transparente que las columnas
            name=self.description,
            hoverinfo="text",
            text=f"{self.description} (Piso {self.piso})<br>Área: {self.area}m²"
        ))
        return fig

    def render_3d(self, fig, color="grey", opacity=1):
        """
        Agrega el volumen del pasadizo a una figura 3D existente.
        """
        # Dibujamos el volumen usando Mesh3d (extrusión)
        fig.add_trace(go.Mesh3d(
            x=self.x_l + self.x_l,
            y=self.y_l + self.y_l,
            z=[self.z_suelo]*len(self.x_l) + [self.z_techo]*len(self.x_l),
            alphahull=0,
            opacity=opacity,
            color=color,
            name=self.description,
            hoverinfo="text",
            text=f"{self.description}<br>Piso: {self.piso}<br>Área: {self.area}m²"
        ))

    def draw_3d(self, fig=None):
        """
        Crea una visualización 3D independiente.
        """
        if fig is None:
            fig = go.Figure()

        self.render_3d(fig)

        fig.update_layout(
            scene=dict(
                aspectmode='data',
                zaxis_title="Altura (m)",
                xaxis_title="X (m)",
                yaxis_title="Y (m)"
            ),
            title=f"Vista 3D: {self.description} - Nivel {self.piso}"
        )
        fig.show()
