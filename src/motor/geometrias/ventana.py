import pandas as pd
import plotly.graph_objects as go
from shapely.geometry import Polygon

class Ventana:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="ventana", h_alfeizar=1.2, h_ventana=1.2, h_entrepiso=2.7):
        self.ancho = ancho
        self.largo = largo
        self.h_alfeizar = h_alfeizar
        self.h_ventana = h_ventana
        self.h_entrepiso = h_entrepiso # Altura total del piso
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.h_dintel = self.h_entrepiso - (self.h_alfeizar + self.h_ventana)
        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        z_suelo = (self.piso - 1) * self.h_entrepiso

        h_dintel = self.h_entrepiso - (self.h_alfeizar + self.h_ventana)

        z_alfeizar_top = z_suelo + self.h_alfeizar
        z_ventana_top = z_alfeizar_top + self.h_ventana
        z_dintel_top = z_ventana_top + h_dintel  # = techo

        x_base, y_base = self.geometria.exterior.xy
        x_l, y_l = list(x_base), list(y_base)

        # 🔹 Alféizar
        self.geom_alfeizar_3d = {
            'x': x_l + x_l,
            'y': y_l + y_l,
            'z': [z_suelo]*len(x_l) + [z_alfeizar_top]*len(x_l)
        }

        # 🔹 Ventana
        self.geom_ventana_3d = {
            'x': x_l + x_l,
            'y': y_l + y_l,
            'z': [z_alfeizar_top]*len(x_l) + [z_ventana_top]*len(x_l)
        }

        # 🔹 Dintel
        self.geom_dintel_3d = {
            'x': x_l + x_l,
            'y': y_l + y_l,
            'z': [z_ventana_top]*len(x_l) + [z_dintel_top]*len(x_l)
        }

        # 🔥 guarda alturas (esto es CLAVE)
        self.z_suelo = z_suelo
        self.z_alfeizar_top = z_alfeizar_top
        self.z_ventana_top = z_ventana_top
        self.z_dintel_top = z_dintel_top
        self.h_dintel = h_dintel

    def render_3d(self, fig):
        # 1. Dibujar Alféizar (Muro sólido abajo)
        fig.add_trace(go.Mesh3d(
            x=self.geom_alfreizar_3d['x'], y=self.geom_alfreizar_3d['y'], z=self.geom_alfreizar_3d['z'],
            alphahull=0, opacity=1.0, color="grey", name=f"Alféizar {self.description}"
        ))

        # 2. Dibujar Ventana (El hueco)
        fig.add_trace(go.Mesh3d(
            x=self.geom_ventana_3d['x'], y=self.geom_ventana_3d['y'], z=self.geom_ventana_3d['z'],
            alphahull=0, opacity=0.3, color="skyblue", name=f"Vidrio {self.description}"
        ))

        # 3. Dibujar Dintel (Muro sólido arriba)
        fig.add_trace(go.Mesh3d(
            x=self.geom_dintel_3d['x'], y=self.geom_dintel_3d['y'], z=self.geom_dintel_3d['z'],
            alphahull=0, opacity=1.0, color="grey", name=f"Dintel {self.description}"
        ))

    def draw_3d(self, fig=None):
        if fig is None:
            fig = go.Figure()

        self.render_3d(fig)

        # Calcular medida del dintel para el título
        h_dintel_calc = self.h_entrepiso - (self.h_alfeizar + self.h_ventana)

        fig.update_layout(
            scene=dict(aspectmode='data', zaxis_title="Altura (m)"),
            title=f"{self.description.upper()}<br>Alféizar: {self.h_alfeizar}m | Ventana: {self.h_ventana}m | Dintel: {h_dintel_calc:.2f}m"
        )
        fig.show()

    def render(self, fig, color="gray", borde="white"):
      """
      Dibuja la ventana en el fig de plotly con relleno de vidrio y borde de marco
      """
      import plotly.graph_objects as go

      # Coordenadas de la geometría
      x, y = self.geometria.exterior.xy
      x = list(x)
      y = list(y)

      # Dibujar el vidrio (relleno)
      fig.add_trace(go.Scatter(
          x=x,
          y=y,
          fill="toself",
          mode="lines",
          line=dict(color=borde, width=2),  # borde del marco
          fillcolor=color,
          opacity=0.5,
          name=self.description,
          showlegend=False
      ))

    def get_data(self):
      filas = []

      # 🔹 Alféizar (parte inferior sólida)
      filas.append({
          "tipo": "muro",
          "subtipo": "alfeizar",
          "description": self.description,
          "piso": self.piso,
          "x": self.x,
          "y": self.y,
          "z_min": self.z_suelo,
          "z_max": self.z_alfeizar_top,
          "altura": self.h_alfeizar,
          "ancho": self.ancho,
          "largo": self.largo,
          "geometria": self.geometria,
          "geometria_3d": self.geom_alfeizar_3d
      })

      # 🔹 Vidrio (hueco)
      filas.append({
          "tipo": "ventana",
          "subtipo": "vidrio",
          "description": self.description,
          "piso": self.piso,
          "x": self.x,
          "y": self.y,
          "z_min": self.z_alfeizar_top,
          "z_max": self.z_ventana_top,
          "ancho": self.ancho,
          "largo": self.largo,
          "geometria": self.geometria,
          "geometria_3d": self.geom_ventana_3d
      })

      # 🔹 Dintel (parte superior)
      filas.append({
          "tipo": "muro",
          "subtipo": "dintel",
          "description": self.description,
          "piso": self.piso,
          "x": self.x,
          "y": self.y,
          "z_min": self.z_ventana_top,
          "z_max": self.z_dintel_top,
          "ancho": self.ancho,
          "largo": self.largo,
          "geometria": self.geometria,
          "geometria_3d": self.geom_dintel_3d
      })

      return filas
