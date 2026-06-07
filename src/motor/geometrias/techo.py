import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd

import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd

class Techo:
    def __init__(self, ancho, largo, x=0, y=0, z=0, piso=1, description="techo",
                 lado=None, altura=0.2, altura_piso=3.0, pendiente=1.0, orientacion='E'):
        self.ancho = ancho
        self.largo = largo
        self.altura = altura # Grosor de la losa
        self.x = x
        self.y = y
        self.z = z
        self.piso = piso
        self.description = description
        self.lado = lado
        self.altura_piso = altura_piso
        self.geometria = None
        self.geometria_3d = None
        self.tipo = "techo"
        self.area = None

        # Parámetros de inclinación
        self.pendiente = pendiente  # Cuánto sube en el eje Z al final del recorrido
        self.orientacion = orientacion # 'x' o 'y'

        self._actualizar_geometrias()

    def set_orientacion(self, nueva_orientacion):
        self.orientacion = nueva_orientacion.upper()
        self._actualizar_geometrias()

    def _actualizar_geometrias(self):

      self.geometria = Polygon([
          (self.x, self.y),
          (self.x + self.ancho, self.y),
          (self.x + self.ancho, self.y + self.largo),
          (self.x, self.y + self.largo)
      ])

      z_suelo = self.z if self.z != 0 else (self.piso * self.altura_piso)

      coords_esquinas = [
          (self.x, self.y),
          (self.x + self.ancho, self.y),
          (self.x + self.ancho, self.y + self.largo),
          (self.x, self.y + self.largo)
      ]

      x_coords = []
      y_coords = []
      z_coords = []

      # =========================
      # CARA INFERIOR (plana)
      # =========================
      for px, py in coords_esquinas:
          x_coords.append(px)
          y_coords.append(py)
          z_coords.append(z_suelo)

      # =========================
      # CARA SUPERIOR (inclinada)
      # =========================
      for px, py in coords_esquinas:

          z_inc = 0

          if self.orientacion == 'E':
              z_inc = ((px - self.x) / self.ancho) * self.pendiente

          elif self.orientacion == 'W':
              z_inc = ((self.x + self.ancho - px) / self.ancho) * self.pendiente

          elif self.orientacion == 'N':
              z_inc = ((py - self.y) / self.largo) * self.pendiente

          elif self.orientacion == 'S':
              z_inc = ((self.y + self.largo - py) / self.largo) * self.pendiente

          x_coords.append(px)
          y_coords.append(py)

          # altura real del techo
          z_coords.append(z_suelo + self.altura + z_inc)

      self.geometria_3d = {
          'x': x_coords,
          'y': y_coords,
          'z': z_coords
      }

    # def _actualizar_geometrias(self):
    #     # Determinamos si giramos las dimensiones
    #     # Si es N o S, el ancho del techo (su frente) se alinea con el eje X original,
    #     # pero la profundidad (donde sube la pendiente) es el eje Y.
    #     if self.orientacion in ['N', 'S']:
    #         ancho_actual = self.ancho
    #         largo_actual = self.largo
    #     else: # E o W
    #         ancho_actual = self.ancho
    #         largo_actual = self.largo

    #     # 1. Definir esquinas del plano base
    #     coords_esquinas = [
    #         (self.x, self.y),
    #         (self.x + ancho_actual, self.y),
    #         (self.x + ancho_actual, self.y + largo_actual),
    #         (self.x, self.y + largo_actual)
    #     ]

    #     self.geometria = Polygon(coords_esquinas)
    #     z_suelo = self.z if self.z != 0 else (self.piso * self.altura_piso)

    #     x_coords, y_coords, z_coords = [], [], []

    #     for capa in [0, self.altura]:
    #         for px, py in coords_esquinas:
    #             z_inc = 0
    #             # Lógica de rotación de pendiente:
    #             if self.orientacion == 'E': # Sube hacia +X
    #                 z_inc = ((px - self.x) / ancho_actual) * self.pendiente
    #             elif self.orientacion == 'W': # Sube hacia -X
    #                 z_inc = ((self.x + ancho_actual - px) / ancho_actual) * self.pendiente
    #             elif self.orientacion == 'N': # Sube hacia +Y
    #                 z_inc = ((py - self.y) / largo_actual) * self.pendiente
    #             elif self.orientacion == 'S': # Sube hacia -Y
    #                 z_inc = ((self.y + largo_actual - py) / largo_actual) * self.pendiente

    #             x_coords.append(px)
    #             y_coords.append(py)
    #             z_coords.append(z_suelo + z_inc + capa)

    #     self.geometria_3d = {'x': x_coords, 'y': y_coords, 'z': z_coords}


    def render_3d(self, fig, color="gray"):
        # Usamos Mesh3d con i, j, k definidos para cerrar el sólido (cubo deformado)
        # Si no defines i, j, k, Plotly intentará envolver los puntos con alphahull
        fig.add_trace(go.Mesh3d(
            x=self.geometria_3d['x'],
            y=self.geometria_3d['y'],
            z=self.geometria_3d['z'],
            # Definición de caras para un prisma de 8 vértices
            i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=1.0,
            color=color,
            flatshading=True,
            name=self.description
        ))

    def get_data(self):
        return [{
            "ancho": self.ancho,
            "largo": self.largo,
            "altura": self.altura,
            "piso": self.piso,
            "description": self.description,
            "geometria": self.geometria,
            "x": self.x,
            "y": self.y,
            "tipo": self.tipo,
            "lado": self.lado,
            "geometria_3d": self.geometria_3d,
        }]

    def draw_3d(self, fig=None):
        if fig is None:
            fig = go.Figure()
        self.render_3d(fig)
        fig.update_layout(scene=dict(aspectmode='data'))
        fig.show()

# techo_inclinado = Techo(
#                   ancho=5,
#                   largo=8,
#                   x=0,
#                   y=0,
#                   z=2.7,
#                   pendiente=0.80,
#                   orientacion='N'
#                   )
# techo_inclinado.get_data()
