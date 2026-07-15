import plotly.graph_objects as go
from shapely.geometry import Polygon
import pandas as pd

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
        self.tipo = "muro"

        # Sincronizar geometrías 2D y 3D
        self._actualizar_geometrias()

    def cortar_altura(self, z_inicio_corte, altura_corte):
        """
        Crea un hueco vertical en el muro.
        z_inicio_corte: altura relativa desde la base del muro.
        altura_corte: alto del hueco.
        """

        segmentos = []

        z_base = self.z
        z_tope_relativo = self.altura  # altura del muro desde su base

        z_fin_corte = z_inicio_corte + altura_corte

        # VALIDACIÓN: evitar cortes fuera del muro
        if z_inicio_corte < 0:
            z_inicio_corte = 0

        if z_fin_corte > z_tope_relativo:
            z_fin_corte = z_tope_relativo

        # 1. PARTE INFERIOR
        if z_inicio_corte > 0:
            muro_inferior = Muro(
                ancho=self.ancho,
                largo=self.largo,
                x=self.x,
                y=self.y,
                z=z_base,
                piso=self.piso,
                description=self.description + "_inferior",
                lado=self.lado,
                altura=z_inicio_corte
            )
            segmentos.append(muro_inferior)

        # 2. PARTE SUPERIOR
        if z_fin_corte < z_tope_relativo:
            altura_superior = z_tope_relativo - z_fin_corte

            muro_superior = Muro(
                ancho=self.ancho,
                largo=self.largo,
                x=self.x,
                y=self.y,
                z=z_base + z_fin_corte,
                piso=self.piso,
                description=self.description + "_superior",
                lado=self.lado,
                altura=altura_superior
            )
            segmentos.append(muro_superior)

        return segmentos

    def segmentar_altura(self, medidas):
        """
        Divide el muro verticalmente en varios segmentos según una lista de alturas.
        medidas: Lista de flotantes, ej. [1.0, 0.4, 0.3]
        """
        segmentos = []
        z_base_original = self.z
        z_acumulado_relativo = 0.0

        for i, altura_segmento in enumerate(medidas):
            # Validación por si las medidas pasadas superan la altura total del muro original
            if z_acumulado_relativo >= self.altura:
                break
                
            # Si la altura del segmento actual excede lo que queda de muro, lo limitamos
            if z_acumulado_relativo + altura_segmento > self.altura:
                altura_segmento = self.altura - z_acumulado_relativo

            # Evitamos crear segmentos con altura cero o negativa
            if altura_segmento <= 0:
                continue

            muro_segmento = Muro(
                ancho=self.ancho,
                largo=self.largo,
                x=self.x,
                y=self.y,
                z=z_base_original + z_acumulado_relativo,  # Se apila según lo acumulado
                piso=self.piso,
                description=f"{self.description}_seg_{i+1}",
                lado=self.lado,
                altura=altura_segmento
            )
            segmentos.append(muro_segmento)
            
            # Actualizamos el acumulado para el siguiente segmento
            z_acumulado_relativo += altura_segmento

        return segmentos

    def segmentar_horizontal(self, medidas):
        """
        Divide el muro horizontalmente sobre su lado más largo.
        
        - Si ancho > largo, corta sobre el eje X.
        - Si largo >= ancho, corta sobre el eje Y.
        
        medidas: Lista de tamaños de segmentos.
        Ejemplo: [2.0, 1.5, 3.0]
        """

        segmentos = []

        # Detectamos cuál es el lado dominante
        cortar_en_x = self.ancho >= self.largo

        longitud_total = self.ancho if cortar_en_x else self.largo

        acumulado = 0.0

        for i, medida in enumerate(medidas):

            # Si ya excedimos la longitud total, detenemos
            if acumulado >= longitud_total:
                break

            # Ajuste del último segmento si se pasa
            if acumulado + medida > longitud_total:
                medida = longitud_total - acumulado

            # Evitamos segmentos inválidos
            if medida <= 0:
                continue

            # Construcción del nuevo muro segmentado
            if cortar_en_x:
                muro_segmento = Muro(
                    ancho=medida,
                    largo=self.largo,
                    x=self.x + acumulado,
                    y=self.y,
                    z=self.z,
                    piso=self.piso,
                    description=f"{self.description}_seg_{i+1}",
                    lado=self.lado,
                    altura=self.altura
                )
            else:
                muro_segmento = Muro(
                    ancho=self.ancho,
                    largo=medida,
                    x=self.x,
                    y=self.y + acumulado,
                    z=self.z,
                    piso=self.piso,
                    description=f"{self.description}_seg_{i+1}",
                    lado=self.lado,
                    altura=self.altura
                )

            segmentos.append(muro_segmento)

            acumulado += medida

        return segmentos

    def dividir_en_altura(self, z_inicio_hueco, altura_hueco):
        """
        Divide el muro verticalmente (en el eje Z) para crear un hueco.
        Retorna una lista con el segmento de abajo (antepecho) y el de arriba (dintel).
        """
        segmentos = []

        # 1. Calcular el segmento inferior (desde la base actual hasta el inicio del hueco)
        # Solo se crea si hay espacio entre la base del muro y el inicio del hueco
        altura_inferior = z_inicio_hueco - self.z
        if altura_inferior > 0:
            muro_inferior = Muro(
                ancho=self.ancho, largo=self.largo, x=self.x, y=self.y,
                z=self.z, piso=self.piso,
                description=self.description + " (inferior)",
                lado=self.lado, altura=altura_inferior
            )
            segmentos.append(muro_inferior)

        # 2. Calcular el segmento superior (desde el final del hueco hasta el techo del muro)
        z_final_hueco = z_inicio_hueco + altura_hueco
        z_techo_original = self.z + self.altura

        altura_superior = z_techo_original - z_final_hueco
        if altura_superior > 0:
            muro_superior = Muro(
                ancho=self.ancho, largo=self.largo, x=self.x, y=self.y,
                z=z_final_hueco, piso=self.piso,
                description=self.description + " (superior/dintel)",
                lado=self.lado, altura=altura_superior
            )
            segmentos.append(muro_superior)

        return segmentos

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
        # Si self.z es None o no se ha definido explícitamente (asumiendo que por defecto inicia en 0 o None en el constructor),
        # calculamos la base según el piso. Si ya tiene un valor (incluso 0 en una segmentación), usamos self.z de forma absoluta.
        
        # NOTA: Para evitar que el '0' de la segmentación active el cálculo por defecto del piso completo,
        # asegúrate de que en el constructor de Muro, si no pasas 'z', este valga por defecto la altura del piso,
        # o cambia la lógica aquí para usar un atributo 'z_absoluto' si es necesario.
        
        # Si quieres mantener una transición limpia, haz que use self.z directamente si estás controlando las alturas de los muros de forma manual:
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
        return [{
            "ancho": self.ancho,
            "largo": self.largo,
            "altura": self.altura,
            "area": self.area,
            "piso": self.piso,
            "description": self.description,
            "geometria": self.geometria,
            "x": self.x,
            "y": self.y,
            "tipo": self.tipo,
            "lado": self.lado,
            "geometria_3d": self.geometria_3d,
        }]

# Ejemplo de uso
# muro_base = Muro(ancho=5.0, largo=0.15, x=0, y=0, description="Muro Fachada")
# muro_base.get_data()