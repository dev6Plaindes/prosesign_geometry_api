import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd
from src.motor.geometrias.muro import Muro
class Pasadizo:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="Pasadizo", altura_piso=2.7, espesor=0.2, lado="E", z = 0):
        """
        ancho: dimensión horizontal
        largo: dimensión vertical
        x, y: posición base
        piso: nivel
        description: etiqueta
        h_entrepiso: altura del volumen 3D
        """
        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.z = z
        self.piso = piso
        self.description = description
        self.espesor = espesor
        self.altura_piso = altura_piso
        self.area = ancho * largo
        self.lado = lado

        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        self.z_suelo = (self.piso - 1) * self.altura_piso
        self.z_techo = self.z_suelo + self.espesor

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

    def render_3d(self, fig, color="lightgrey", opacity=1):
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

        parapetos = self.generar_parapeto()

        for muro in parapetos:
            muro.render_3d(fig, color="gray")


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

    def draw(self, fig, color="lightgrey", borde="black"):
        """Dibuja en 2D (Planta)"""
        x_coords, y_coords = self.geometria.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x_coords),
            y=list(y_coords),
            fill="toself",
            mode="lines",
            line=dict(color=borde, width=1),
            fillcolor=color,
            opacity=0.5,
            name=self.description,
            hoverinfo="text",
            text=f"{self.description} (Piso {self.piso})<br>Área: {self.area}m²"
        ))
        return fig

    def get_data(self):
        # 🔹 Data del pasadizo
        df_pasadizo = pd.DataFrame({
            "ancho": [self.ancho],
            "largo": [self.largo],
            "area": [self.area],
            "piso": [self.piso],
            "description": [self.description],
            "x": [self.x],
            "y": [self.y],
            "tipo": ["pasadizo"],
            "subtipo": ["circulacion"],
            "geometria": [self.geometria],
            "geometria_3d": [self.geometria_3d],
        })

        # 🔹 Data de muros (usando su propio get_data)
        muros = self.generar_parapeto()

        if not muros:
            return df_pasadizo

        df_muros = pd.concat([muro.get_data() for muro in muros], ignore_index=True)

        # 🔹 Unir todo
        return pd.concat([df_pasadizo, df_muros], ignore_index=True)

    def generar_parapeto(self):
      if self.piso <= 1:
          return []

      parapetos = []
      coords = list(zip(self.x_l, self.y_l))

      x_min = min(self.x_l)
      x_max = max(self.x_l)
      y_min = min(self.y_l)
      y_max = max(self.y_l)

      for i in range(len(coords)):
          x1, y1 = coords[i]
          x2, y2 = coords[(i + 1) % len(coords)]

          dx = abs(x2 - x1)
          dy = abs(y2 - y1)

          lado_actual = None

          # identificar lado del segmento
          if dy < 1e-6:
              if y1 == y_min:
                  lado_actual = "S"
              elif y1 == y_max:
                  lado_actual = "N"

          elif dx < 1e-6:
              if x1 == x_min:
                  lado_actual = "O"
              elif x1 == x_max:
                  lado_actual = "E"

          # 🔥 REGLA PRINCIPAL: excluir lado del objeto
          if lado_actual == self.lado:
              continue

          # crear muro horizontal
          if dy < 1e-6:
              muro = Muro(
                  ancho=dx,
                  largo=0.15,
                  x=min(x1, x2),
                  y=y1,
                  z=self.z_suelo,
                  piso=self.piso,
                  description=f"Parapeto {lado_actual}",
                  altura=0.95,
                  lado=lado_actual
              )

          # crear muro vertical
          else:
              muro = Muro(
                  ancho=0.15,
                  largo=dy,
                  x=x1,
                  y=min(y1, y2),
                  z=self.z_suelo,
                  piso=self.piso,
                  description=f"Parapeto {lado_actual}",
                  altura=0.95,
                  lado=lado_actual
              )

          muro.altura_piso = self.altura_piso  # 🔥 CLAVE
          muro._actualizar_geometrias()

          parapetos.append(muro)

      return parapetos
