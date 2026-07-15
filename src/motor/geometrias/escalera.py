import pandas as pd
from shapely.geometry import Polygon
import plotly.graph_objects as go

import numpy as np

class Escalera:
    def __init__(self, ancho=1.2, largo = 4, x=0, y=0, piso_inicio=1,
                 altura_piso=1.47, num_escalones=7,
                 direccion="norte", description="Escalera", z=0):

        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.z = z
        self.piso_inicio = piso_inicio
        self.altura_piso = altura_piso
        self.num_escalones = num_escalones
        self.direccion = direccion
        self.description = description

        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def draw(self, fig, color="rgba(200,200,200,0.6)"):
        x_coords, y_coords = self.geometria.exterior.xy

        fig.add_trace(go.Scatter(
            x=list(x_coords),
            y=list(y_coords),
            fill="toself",
            fillcolor=color,
            line=dict(color="black", width=2),
            name=self.description
        ))

        for i in range(1, self.num_escalones):
            frac = i / self.num_escalones

            if self.direccion in ["norte", "sur"]:
                pos_y = self.y + self.largo * frac
                fig.add_trace(go.Scatter(
                    x=[self.x, self.x + self.ancho],
                    y=[pos_y, pos_y],
                    mode="lines",
                    line=dict(color="gray", width=1),
                    showlegend=False
                ))
            else:
                pos_x = self.x + self.ancho * frac
                fig.add_trace(go.Scatter(
                    x=[pos_x, pos_x],
                    y=[self.y, self.y + self.largo],
                    mode="lines",
                    line=dict(color="gray", width=1),
                    showlegend=False
                ))

        return fig

    def render_3d(self, fig = None, color="gray"):
        if fig == None:
            fig = go.Figure()

        dz = self.altura_piso / self.num_escalones

        # Dimensiones de la huella
        step_l = self.largo / self.num_escalones if self.direccion in ["norte", "sur"] else self.largo
        step_w = self.ancho / self.num_escalones if self.direccion in ["este", "oeste"] else self.ancho

        # AQUÍ ESTÁ EL CAMBIO: Sumamos self.z
        z0 = ((self.piso_inicio - 1) * self.altura_piso) + self.z

        for i in range(self.num_escalones):
            z = z0 + i * dz

            if self.direccion == "norte":
                x, y = self.x, self.y + i * step_l
            elif self.direccion == "sur":
                x, y = self.x, self.y + self.largo - (i + 1) * step_l
            elif self.direccion == "este":
                x, y = self.x + i * step_w, self.y
            else:  # oeste
                x, y = self.x + self.ancho - (i + 1) * step_w, self.y

            self._add_box(fig, x, y, z, step_w, step_l, dz, color)

        return fig

    def draw_3d(self, fig, color="gray"):
        dz = self.altura_piso / self.num_escalones

        step_l = self.largo / self.num_escalones if self.direccion in ["norte", "sur"] else self.largo
        step_w = self.ancho / self.num_escalones if self.direccion in ["este", "oeste"] else self.ancho

        z0 = (self.piso_inicio - 1) * self.altura_piso

        for i in range(self.num_escalones):

            z = z0 + i * dz

            if self.direccion == "norte":
                x = self.x
                y = self.y + i * step_l

            elif self.direccion == "sur":
                x = self.x
                y = self.y + self.largo - (i + 1) * step_l

            elif self.direccion == "este":
                x = self.x + i * step_w
                y = self.y

            else:  # oeste
                x = self.x + self.ancho - (i + 1) * step_w
                y = self.y

            self._add_box(fig, x, y, z, step_w, step_l, dz, color)

        return fig
    
    def get_data(self):
        filas = []

        dz = self.altura_piso / self.num_escalones

        step_l = self.largo / self.num_escalones if self.direccion in ["norte", "sur"] else self.largo
        step_w = self.ancho / self.num_escalones if self.direccion in ["este", "oeste"] else self.ancho

        z0 = ((self.piso_inicio - 1) * self.altura_piso) + self.z

        for i in range(self.num_escalones):
            z = z0 + i * dz

            if self.direccion == "norte":
                x, y = self.x, self.y + i * step_l
            elif self.direccion == "sur":
                x, y = self.x, self.y + self.largo - (i + 1) * step_l
            elif self.direccion == "este":
                x, y = self.x + i * step_w, self.y
            else:  # oeste
                x, y = self.x + self.ancho - (i + 1) * step_w, self.y

            # 🔹 geometría 2D del escalón
            geom_2d = Polygon([
                (x, y),
                (x + step_w, y),
                (x + step_w, y + step_l),
                (x, y + step_l)
            ])

            # 🔹 geometría 3D del escalón (igual a tu box)
            geom_3d = {
                "x": [x, x+step_w, x+step_w, x, x, x+step_w, x+step_w, x],
                "y": [y, y, y+step_l, y+step_l, y, y, y+step_l, y+step_l],
                "z": [z, z, z, z, z+dz, z+dz, z+dz, z+dz]
            }

            filas.append({
                "tipo": "escalera",
                "subtipo": "escalon",
                "indice": i,
                "description": self.description,
                "piso_inicio": self.piso_inicio,
                "x": x,
                "y": y,
                "z_min": z,
                "z_max": z + dz,
                "ancho": step_w,
                "largo": step_l,
                "geometria": geom_2d,
                "geometria_3d": geom_3d
            })

        return filas

    def _add_box(self, fig, x, y, z, dx, dy, dz, color):

        # 8 vértices del cubo
        X = [x, x+dx, x+dx, x, x, x+dx, x+dx, x]
        Y = [y, y, y+dy, y+dy, y, y, y+dy, y+dy]
        Z = [z, z, z, z, z+dz, z+dz, z+dz, z+dz]

        # CARAS del cubo (6 caras = 12 triángulos)
        i = [0,0,0, 1,1, 2,2, 3,4,5, 6,7]
        j = [1,2,3, 2,5, 3,6, 0,5,6, 7,4]
        k = [2,3,1, 5,6, 6,7, 4,6,7, 4,0]

        fig.add_trace(go.Mesh3d(
            x=X, y=Y, z=Z,
            i=i, j=j, k=k,
            color=color,
            opacity=1
        ))


class Descanso():
    def __init__(self, ancho, largo, x=0, y=0, z=0):
        self.ancho = ancho
        self.largo = largo
        self.altura = 0.15
        self.x = x
        self.y = y
        self.z = z
        self._actualizar_geometrias()
        self.geometria_3d = None

    def _actualizar_geometrias(self):
        # Mantenemos tu lógica de Polygon para 2D
        from shapely.geometry import Polygon
        self.geometria = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

    def generar_geometria_3d(self):
        """
        Calcula y almacena los vértices y las caras del prisma 3D.
        Útil para cálculos de colisiones o exportación de geometría.
        """
        # 1. Definir los 8 vértices
        # Base inferior (z)
        v_0 = [self.x, self.y, self.z]
        v_1 = [self.x + self.ancho, self.y, self.z]
        v_2 = [self.x + self.ancho, self.y + self.largo, self.z]
        v_3 = [self.x, self.y + self.largo, self.z]

        # Base superior (z + altura)
        v_4 = [self.x, self.y, self.z + self.altura]
        v_5 = [self.x + self.ancho, self.y, self.z + self.altura]
        v_6 = [self.x + self.ancho, self.y + self.largo, self.z + self.altura]
        v_7 = [self.x, self.y + self.largo, self.z + self.altura]

        vertices = np.array([v_0, v_1, v_2, v_3, v_4, v_5, v_6, v_7])

        # 2. Definir las caras (índices de los vértices para formar triángulos)
        # Cada cara del prisma tiene 2 triángulos
        caras = np.array([
            [0, 1, 2], [0, 2, 3], # Base inferior
            [4, 5, 6], [4, 6, 7], # Base superior
            [0, 4, 5], [0, 5, 1], # Cara frontal
            [1, 5, 6], [1, 6, 2], # Cara derecha
            [2, 6, 7], [2, 7, 3], # Cara trasera
            [3, 7, 4], [3, 4, 0]  # Cara izquierda
        ])

        # Guardamos en un diccionario o estructura de datos
        self.geometria_3d = {
            'vertices': vertices,
            'caras': caras
        }
    
    def get_data(self):

        # 🔥 Asegurar que la geometría 3D existe
        if self.geometria_3d is None:
            self.generar_geometria_3d()

        filas = []

        filas.append({
            "tipo": "descanso",
            "subtipo": "plataforma",
            "description": "Descanso",
            "x": self.x,
            "y": self.y,
            "z_min": self.z,
            "z_max": self.z + self.altura,
            "ancho": self.ancho,
            "largo": self.largo,
            "altura": self.altura,
            "geometria": self.geometria,
            "geometria_3d": self.geometria_3d
        })

        return filas

    def render_3d(self, fig=None, color='gray', opacity=1):
        if fig is None:
            fig = go.Figure()

        # Si no se ha generado la geometría, la generamos
        if self.geometria_3d is None:
            self.generar_geometria_3d()

        v = self.geometria_3d['vertices']
        c = self.geometria_3d['caras']

        # Añadir el sólido usando los datos de geometria_3d
        fig.add_trace(go.Mesh3d(
            x=v[:, 0], y=v[:, 1], z=v[:, 2],
            i=c[:, 0], j=c[:, 1], k=c[:, 2],
            color=color,
            opacity=opacity,
            flatshading=True,
            name="Descanso"
        ))

        # Opcional: Dibujar bordes usando los vértices calculados
        # (Aquí podrías añadir la lógica de los Scatter3d que vimos antes)

        return fig

class EscalerasCompleta:
    def __init__(self, ancho=2.4, largo=4, x=0, y=0, z=0, piso_inicio=1,
                 altura_piso=3.0, num_escalones=7,
                 direccion="norte", description="Escalera"):
        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.z = z
        self.piso_inicio = piso_inicio
        self.altura_piso = altura_piso
        self.num_escalones = num_escalones
        self.direccion = direccion
        self.description = description
        self.escaleras = []
        self.descanso_escalera = None
        self.z_inicio = 0 # Referencia base

        # Definición del área total en planta
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def generate_escaleras(self):
        # 1. Parámetros de geometría básica
        ancho_tramo = self.ancho / 2
        largo_tramo = self.largo - 1.2  # Restamos el espacio del descanso
        altura_media = self.altura_piso / 2

        # 2. Tramo 1 (Sube del nivel 0 a altura_media)
        # IMPORTANTE: Asegúrate de que Escalera acepte 'z' o cámbialo al nombre correcto
        z_inicio = self.z
        distancia_mid = 1.47
        z_mid = z_inicio + distancia_mid
        if self.direccion == "sur":
            self.escaleras.append(Escalera(
                ancho=ancho_tramo,
                largo=largo_tramo,
                x=self.x,
                y=self.y,
                z=z_inicio,  # Cambié z_inicio por z (ajusta según tu clase Escalera)
                num_escalones=self.num_escalones
            ))

            # 3. El Descanso (Pasadizo)
            self.descanso_escalera = Descanso(
                ancho=self.ancho,
                largo=1.2,
                x=self.x,
                y=self.y + largo_tramo,
                z=z_mid,
            )

            self.escaleras.append(Escalera(
                ancho=ancho_tramo,
                largo=largo_tramo,
                x=self.x + ancho_tramo,
                y=self.y,
                z=z_mid,
                altura_piso=1.43,
                num_escalones=self.num_escalones,
                direccion=self.direccion
            ))

        elif self.direccion == "norte":
            # Tramo 1: Comienza arriba a la derecha y baja hacia el descanso
            self.escaleras.append(Escalera(
                ancho=ancho_tramo, largo=largo_tramo,
                x=self.x + ancho_tramo, y=self.y + 1.2,
                z=z_inicio, num_escalones=self.num_escalones, direccion = "sur"
            ))
            # Descanso: Abajo (ocupa todo el ancho)
            self.descanso_escalera = Descanso(
                ancho=self.ancho, largo=1.2,
                x=self.x, y=self.y, z=z_mid
            )
            # Tramo 2: Comienza en el descanso y sube hacia el norte
            self.escaleras.append(Escalera(
                ancho=ancho_tramo, largo=largo_tramo,
                x=self.x, y=self.y + 1.2,
                z=z_mid, altura_piso=1.43,
                num_escalones=self.num_escalones, direccion=self.direccion
            ))

        elif self.direccion == "este":
            # Tramo 1: De izquierda a derecha (parte superior)
            self.escaleras.append(Escalera(
                ancho=largo_tramo, largo=ancho_tramo,
                x=self.x  + 1.2, y=self.y,
                z=z_inicio, num_escalones=self.num_escalones, direccion="oeste"
            ))
            # Descanso: A la derecha
            self.descanso_escalera = Descanso(
                ancho=1.2, largo=self.ancho,
                x=self.x, y=self.y, z=z_mid
            )

            # Tramo 2: Regresa de derecha a izquierda (parte inferior)
            self.escaleras.append(Escalera(
                ancho=largo_tramo, largo=ancho_tramo,
                x=self.x + 1.2, y=self.y + self.ancho / 2,
                z=z_mid, altura_piso=1.43,
                num_escalones=self.num_escalones, direccion=self.direccion
            ))

        elif self.direccion == "oeste":
            # Tramo 1: De derecha a izquierda (parte inferior)
            self.escaleras.append(Escalera(
                ancho=largo_tramo, largo=ancho_tramo,
                x=self.x, y=self.y,
                z=z_inicio, num_escalones=self.num_escalones, direccion="este"
            ))

            # Descanso: A la derecha
            self.descanso_escalera = Descanso(
                ancho=1.2, largo=self.ancho,
                x=self.x + largo_tramo, y=self.y, z=z_mid
            )

            # # Tramo 2: De izquierda a derecha (parte superior)
            self.escaleras.append(Escalera(
                ancho=largo_tramo, largo=ancho_tramo,
                x=self.x, y=self.y +self.ancho / 2,
                z=z_mid, altura_piso=1.43,
                num_escalones=self.num_escalones, direccion=self.direccion
            ))

    def render_3d(self, fig=None):
        if fig is None:
            fig = go.Figure()

        # Renderizar sub-elementos
        for escalera in self.escaleras:
            escalera.render_3d(fig)

        if self.descanso_escalera:
            self.descanso_escalera.render_3d(fig)

        return fig

    def get_data(self):

        data = []

        # =====================================
        # 1. DATA BASE ESCALERA COMPLETA
        # =====================================
        data_base = {
            "tipo": "escalera_completa",
            "description": self.description,
            "piso_inicio": self.piso_inicio,
            "x": self.x,
            "y": self.y,
            "ancho": self.ancho,
            "largo": self.largo,
            "geometria": self.geometria,
            "geometria_3d": None
        }

        data.append(data_base)

        # =====================================
        # 2. ESCALERAS (TRAMOS)
        # =====================================
        for esc in self.escaleras:

            if hasattr(esc, "get_data"):

                esc_data = esc.get_data()

                # Equivalente exacto a concat
                if isinstance(esc_data, list):

                    data.extend(esc_data)

                else:

                    data.append(esc_data)

        # =====================================
        # 3. DESCANSO
        # =====================================
        if (
            self.descanso_escalera
            and hasattr(
                self.descanso_escalera,
                "get_data"
            )
        ):

            descanso_data = (
                self.descanso_escalera.get_data()
            )

            if isinstance(descanso_data, list):

                data.extend(descanso_data)

            else:

                data.append(descanso_data)

        # =====================================
        # CONCAT FINAL
        # =====================================
        return data
