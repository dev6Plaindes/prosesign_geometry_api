import numpy as np
import plotly.graph_objects as go
from shapely.geometry import Polygon, LineString
import pandas as pd

class Puerta:
    def __init__(self, ancho, largo, x, y, piso=1, description="puerta", lado=None, h_puerta=2.1, h_entrepiso=2.7):
        self.ancho = ancho
        self.largo = largo
        self.h_puerta = h_puerta     # Altura de la hoja de la puerta
        self.h_entrepiso = h_entrepiso # Altura total del piso
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.lado = lado

        # Inicializar geometría 2D y preparar datos para 3D
        self._actualizar_geometria()

    def _actualizar_geometria(self):
        """Calcula la geometría 2D y los volúmenes 3D."""
        # 1. Marco (Huella en el suelo)
        self.geometria_marco = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        # --- Lógica de Hoja y Arco (2D) ---
        num_puntos = 20
        # (Mantenemos tu lógica de rotación de hoja según el lado...)
        if self.lado == "top":
            r = self.ancho
            pivot_x, pivot_y = self.x + self.ancho, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x, pivot_y - r)])
            theta = np.linspace(3 * np.pi / 2, np.pi, num_puntos)
        elif self.lado == "bottom":
            r = self.ancho
            pivot_x, pivot_y = self.x + self.ancho, self.y
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x, pivot_y + r)])
            theta = np.linspace(np.pi / 2, np.pi, num_puntos)
        elif self.lado == "left":
            r = self.largo
            pivot_x, pivot_y = self.x, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x + r, pivot_y)])
            theta = np.linspace(0, -np.pi / 2, num_puntos)
        elif self.lado == "right":
            r = self.largo
            pivot_x, pivot_y = self.x + self.ancho, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x - r, pivot_y)])
            theta = np.linspace(np.pi, 3 * np.pi / 2, num_puntos)
        else:
            self.geometria_hoja = None
            self.geometria_arco = None
            theta = None

        if theta is not None:
            arco_puntos = [(pivot_x + r * np.cos(t), pivot_y + r * np.sin(t)) for t in theta]
            self.geometria_arco = LineString(arco_puntos)

        # --- Lógica 3D ---
        z_suelo = (self.piso - 1) * self.h_entrepiso
        z_puerta_top = z_suelo + self.h_puerta
        z_techo = z_suelo + self.h_entrepiso

        x_m, y_m = self.geometria_marco.exterior.xy
        xl, yl = list(x_m), list(y_m)

        # Volúmen del Dintel (Muro sobre la puerta)
        self.geom_dintel_3d = {
            'x': xl + xl, 'y': yl + yl,
            'z': [z_puerta_top]*len(xl) + [z_techo]*len(xl)
        }

        # Volúmen del Hueco (Espacio de la puerta)
        self.geom_vano_3d = {
            'x': xl + xl, 'y': yl + yl,
            'z': [z_suelo]*len(xl) + [z_puerta_top]*len(xl)
        }

    def render_3d(self, fig):
        """Dibuja el dintel y el hueco de la puerta en 3D."""
        # 1. Dibujar Dintel (Sólido)
        fig.add_trace(go.Mesh3d(
            x=self.geom_dintel_3d['x'], y=self.geom_dintel_3d['y'], z=self.geom_dintel_3d['z'],
            alphahull=0, opacity=1.0, color="grey", name=f"Dintel {self.description}"
        ))

        # 2. Dibujar Vano (Hueco translúcido para ver la apertura)
        fig.add_trace(go.Mesh3d(
            x=self.geom_vano_3d['x'], y=self.geom_vano_3d['y'], z=self.geom_vano_3d['z'],
            alphahull=0, opacity=0.1, color="white", name=f"Hueco {self.description}"
        ))

    def draw_3d(self, fig=None):
        if fig is None: fig = go.Figure()
        self.render_3d(fig)
        fig.update_layout(scene=dict(aspectmode='data'))
        fig.show()

    def render(self, fig):
        """Dibuja los componentes ya calculados en la figura de Plotly."""

        # --- Dibujar Marco ---
        x_m, y_m = self.geometria_marco.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_m), y=list(y_m),
            fill="toself", mode="lines",
            name=self.description,
            line=dict(color="white", dash="dot"),
            opacity=0.6,
            showlegend=False
        ))

        # --- Dibujar Hoja ---
        if self.geometria_hoja:
            x_h, y_h = self.geometria_hoja.xy
            fig.add_trace(go.Scatter(
                x=list(x_h), y=list(y_h),
                mode="lines",
                line=dict(color="black", width=2),
                name=f"hoja {self.description}",
                showlegend=False
            ))

        # --- Dibujar Arco ---
        if self.geometria_arco:
            x_a, y_a = self.geometria_arco.xy
            fig.add_trace(go.Scatter(
                x=list(x_a), y=list(y_a),
                mode="lines",
                line=dict(color="black", width=2, dash="solid"),
                showlegend=False
            ))