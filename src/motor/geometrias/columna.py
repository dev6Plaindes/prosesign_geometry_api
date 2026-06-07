import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd

class Columna:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="columna", lado=None, altura=2.7):
        """
        ancho: horizontal (X)
        largo: profundidad (Y)
        altura: dimensión vertical del elemento (Z)
        """
        self.ancho = ancho
        self.largo = largo
        self.altura = altura
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.lado = lado
        self.area = ancho * largo

        # Sincronizar geometrías iniciales (2D y 3D)
        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        """Genera el Polygon 2D y las coordenadas para Mesh3d"""
        # 1. Geometría 2D (Planta)
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        # 2. Geometría 3D
        # Calculamos la base Z según el piso (asumiendo 3m de elevación por piso previo)
        z_base = (self.piso - 1) * 3.0
        z_techo = z_base + self.altura

        x_base, y_base = self.geometria.exterior.xy
        x_list = list(x_base)
        y_list = list(y_base)

        self.geometria_3d = {
            'x': x_list + x_list,
            'y': y_list + y_list,
            'z': [z_base]*len(x_list) + [z_techo]*len(x_list)
        }

    def set_position(self, x, y):
        """Cambia la posición y recalcula las geometrías"""
        self.x = x
        self.y = y
        self._actualizar_geometrias()

    def get_data(self):
        return  [{
            "ancho": self.ancho,
            "largo": self.largo,
            "altura": self.altura,
            "area": self.area,
            "piso": self.piso,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "tipo": "columna",
            "lado": self.lado,
            "geometria" : self.geometria,
            "geometria_3d" : self.geometria_3d,
        }]

    def render(self, fig, color="grey", borde="black"):
        """Dibuja la planta 2D"""
        x, y = self.geometria.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x), y=list(y),
            fill="toself",
            mode="lines",
            line=dict(color=borde, width=2),
            fillcolor=color,
            opacity=1.0,
            name=self.description,
            showlegend=False
        ))

    def render_3d(self, fig, color="darkgrey"):
        """Añade el volumen 3D a la figura"""
        fig.add_trace(go.Mesh3d(
            x=self.geometria_3d['x'],
            y=self.geometria_3d['y'],
            z=self.geometria_3d['z'],
            alphahull=0,
            opacity=1.0,
            color=color,
            flatshading=True,
            name=self.description
        ))

    def draw_3d(self, fig=None):
        if fig is None:
            fig = go.Figure()
        self.render_3d(fig)
        fig.update_layout(scene=dict(aspectmode='data'))
        fig.show()

