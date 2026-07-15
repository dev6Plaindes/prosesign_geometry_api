import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd

class TechoDosAguas:
    def __init__(
        self,
        ancho,
        largo,
        x=0,
        y=0,
        z=0,
        piso=1,
        altura=0.25,
        altura_piso=3.0,
        altura_cumbrera=1.35,
        orientacion='X'
    ):

        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.z = z
        self.piso = piso
        self.altura = altura
        self.altura_piso = altura_piso
        self.altura_cumbrera = altura_cumbrera
        self.orientacion = orientacion.upper()
        self.tipo = "techo"

        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        z_base = self.z if self.z != 0 else self.piso * self.altura_piso

        # esquinas base
        p0 = (self.x, self.y)
        p1 = (self.x + self.ancho, self.y)
        p2 = (self.x + self.ancho, self.y + self.largo)
        p3 = (self.x, self.y + self.largo)

        self.geometria = Polygon([p0, p1, p2, p3])

        x_coords = []
        y_coords = []
        z_coords = []

        # =========================================================
        # ORIENTACIONES
        # =========================================================

        # NORTE / SUR
        # cumbrera paralela al eje X
        if self.orientacion in ['N', 'S']:

            y_centro = self.y + self.largo / 2

            vertices = [

                # lado inferior
                (self.x, self.y, z_base),
                (self.x + self.ancho, self.y, z_base),

                # cumbrera
                (self.x + self.ancho,
                y_centro,
                z_base + self.altura_cumbrera),

                (self.x,
                y_centro,
                z_base + self.altura_cumbrera),

                # lado superior
                (self.x + self.ancho,
                self.y + self.largo,
                z_base),

                (self.x,
                self.y + self.largo,
                z_base),
            ]

        # ESTE / OESTE
        # cumbrera paralela al eje Y
        else:

            x_centro = self.x + self.ancho / 2

            vertices = [

                # izquierda
                (self.x, self.y, z_base),

                # cumbrera
                (x_centro,
                self.y,
                z_base + self.altura_cumbrera),

                # derecha
                (self.x + self.ancho,
                self.y,
                z_base),

                (self.x + self.ancho,
                self.y + self.largo,
                z_base),

                # cumbrera atrás
                (x_centro,
                self.y + self.largo,
                z_base + self.altura_cumbrera),

                (self.x,
                self.y + self.largo,
                z_base),
            ]

        # =========================================================
        # CAPA INFERIOR
        # =========================================================

        for v in vertices:
            x_coords.append(v[0])
            y_coords.append(v[1])
            z_coords.append(v[2])

        # =========================================================
        # CAPA SUPERIOR (grosor)
        # =========================================================

        for v in vertices:
            x_coords.append(v[0])
            y_coords.append(v[1])
            z_coords.append(v[2] + self.altura)

        self.geometria_3d = {
            'x': x_coords,
            'y': y_coords,
            'z': z_coords
        }
    
    def get_data(self):
        return [{
            "ancho": self.ancho, "largo": self.largo, "altura": self.altura,
            "piso": self.piso,
            "geometria": self.geometria, "x": self.x, "y": self.y,
            "tipo": self.tipo, "geometria_3d": self.geometria_3d,
        }]

    def render_3d(self, fig, color="gray"):

        fig.add_trace(go.Mesh3d(
            x=self.geometria_3d['x'],
            y=self.geometria_3d['y'],
            z=self.geometria_3d['z'],

            opacity=1.0,
            color=color,
            flatshading=True,
            alphahull=0
        ))

    def draw_3d(self):

        fig = go.Figure()

        self.render_3d(fig)

        fig.update_layout(
            scene=dict(
                aspectmode='data'
            )
        )

        fig.show()