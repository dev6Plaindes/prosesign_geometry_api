import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd
class Muro:
    def __init__(self, ancho, largo, x=0, y=0, z=0, piso=1, description="muro", lado=None, altura=2.7, altura_piso=3.0):
        self.ancho = ancho
        self.largo = largo
        self.altura = altura
        self.area = ancho * largo
        self.piso = piso
        self.description = description
        self.x = x
        self.y = y
        self.z = z
        self.lado = lado
        self.altura_piso = altura_piso

        # Sincronizar geometrías 2D y 3D
        self._actualizar_geometrias()

    def _actualizar_geometrias(self):
        """Genera el Polygon 2D y las coordenadas para el volumen 3D"""
        # 1. Geometría 2D
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        # 2. Geometría 3D
        if self.z == 0:
          z_base = (self.piso - 1) * self.altura
          z_techo = z_base + self.altura
        else:
          z_base = self.z
          z_techo = z_base + self.altura

        x_b, y_b = self.geometria.exterior.xy
        xl, yl = list(x_b), list(y_b)

        self.geometria_3d = {
            'x': xl + xl,
            'y': yl + yl,
            'z': [z_base]*len(xl) + [z_techo]*len(xl)
        }

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self._actualizar_geometrias()

    def dividir(self, offset_inicio, ancho_corte, lado):
        """
        Divide el muro en dos segmentos.
        Corregido para el nuevo __init__: (ancho, largo, x, y, piso, description, lado, altura)
        """
        if self.ancho >= self.largo:
            # Muro horizontal (Se divide en el eje X)
            muro_izq = Muro(
                ancho=offset_inicio,largo= self.largo,x= self.x,y= self.y,
                piso=self.piso, description=self.description + " izquierda", lado=lado,altura= self.altura
            ) if offset_inicio > 0 else None

            resto_derecho = self.ancho - (offset_inicio + ancho_corte)
            muro_der = Muro(
                ancho=resto_derecho,largo= self.largo,x= self.x + offset_inicio + ancho_corte,y= self.y,
                piso=self.piso, description=self.description + " derecha", lado=lado, altura=self.altura
            ) if resto_derecho > 0 else None
        else:
            # Muro vertical (Se divide en el eje Y)
            muro_izq = Muro(
                ancho=self.ancho,largo= offset_inicio, x=self.x, y=self.y,
                piso=self.piso, description=self.description + " arriba", lado=lado, altura=self.altura
            ) if offset_inicio > 0 else None

            resto_abajo = self.largo - (offset_inicio + ancho_corte)
            muro_der = Muro(
                ancho=self.ancho, largo=resto_abajo, x=self.x, y=self.y + offset_inicio + ancho_corte,
                piso=self.piso, description=self.description + " abajo", lado=lado, altura=self.altura
            ) if resto_abajo > 0 else None

        return [m for m in [muro_izq, muro_der] if m is not None]

    def render(self, fig, color="black"):
        x, y = self.geometria.exterior.xy
        fig.add_trace(go.Scatter(
            x=list(x), y=list(y),
            fill="toself", mode="lines",
            name=self.description,
            line=dict(color=color),
            opacity=1, showlegend=False
        ))

    def draw(self, fig=None):
        """Visualización 2D rápida"""
        if fig is None:
            fig = go.Figure()
            fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1))
        self.render(fig)
        fig.show()

    def render_3d(self, fig, color="grey"):
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
        """Visualización 3D rápida"""
        if fig is None:
            fig = go.Figure()
        self.render_3d(fig)
        fig.update_layout(
            scene=dict(aspectmode='data'),
            title=f"Render 3D - {self.description}"
        )
        fig.show()

    def get_data(self):
        return pd.DataFrame({
            "ancho": [self.ancho], "largo": [self.largo], "altura": [self.altura],
            "area": [self.area], "piso": [self.piso], "description": [self.description],
            "geometria": [self.geometria], "x": [self.x], "y": [self.y],
            "tipo": ["muro"], "lado": [self.lado], "geometria_3d": [self.geometria_3d]
        })

