from shapely.geometry import Polygon
import plotly.graph_objects as go
import pandas as pd

class Ventana:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="ventana"):
        """
        ancho: horizontal (o ancho si es muro vertical)
        largo: vertical (o alto si es muro horizontal)
        x, y: posición inferior izquierda
        piso: piso del aula
        description: texto descriptivo
        """
        self.ancho = ancho
        self.largo = largo
        self.area = ancho * largo
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description

        # Geometría de la ventana (Polygon)
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.geometria = Polygon([
            (x, y),
            (x + self.ancho, y),
            (x + self.ancho, y + self.largo),
            (x, y + self.largo)
        ])

    def render(self, fig, color="gray", borde="white"):
      """
      Dibuja la ventana en el fig de plotly con relleno de vidrio y borde de marco
      """

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

from shapely.geometry import Polygon

class Pasadizo:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="Pasadizo"):
        """
        ancho: dimensión horizontal del pasadizo
        largo: dimensión vertical del pasadizo
        x, y: posición de la esquina inferior izquierda
        piso: nivel en el que se encuentra
        description: nombre o etiqueta del pasadizo
        """
        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.area = ancho * largo

        # Definición de la geometría usando Polygon de Shapely
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def set_position(self, x, y):
        """Actualiza la posición y regenera el polígono"""
        self.x = x
        self.y = y
        self.geometria = Polygon([
            (x, y),
            (x + self.ancho, y),
            (x + self.ancho, y + self.largo),
            (x, y + self.largo)
        ])

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
            "tipo": "pasadizo",
            "subtipo": "circulacion"
        }

        return pd.DataFrame(data, index=[0])

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
            opacity=0.5, # Un poco más transparente que las columnas
            name=self.description,
            hoverinfo="text",
            text=f"{self.description} (Piso {self.piso})<br>Área: {self.area}m²"
        ))
        return fig

from shapely.geometry import Polygon

class Losa:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="losa"):
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

        # Definición de la geometría usando Polygon de Shapely
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def set_position(self, x, y):
        """Actualiza la posición y regenera el polígono"""
        self.x = x
        self.y = y
        self.geometria = Polygon([
            (x, y),
            (x + self.ancho, y),
            (x + self.ancho, y + self.largo),
            (x, y + self.largo)
        ])
    
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
            "subtipo": "estructura"
        }

        return pd.DataFrame(data, index=[0])

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

class Columna:
    def __init__(self, ancho, largo, x=0, y=0, piso=1, description="columna", lado=None):
        """
        ancho: ancho de la columna (horizontal)
        largo: profundidad de la columna (vertical)
        x, y: posición inferior izquierda
        piso: piso donde está la columna
        description: texto descriptivo
        """
        self.ancho = ancho
        self.largo = largo
        self.area = ancho * largo
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.lado = lado

        # Geometría de la columna (Polygon)
        self.geometria = Polygon([
            (x, y),
            (x + ancho, y),
            (x + ancho, y + largo),
            (x, y + largo)
        ])

    def set_position(self, x, y):
        """
        Cambia la posición de la columna y actualiza la geometría
        """
        self.x = x
        self.y = y
        self.geometria = Polygon([
            (x, y),
            (x + self.ancho, y),
            (x + self.ancho, y + self.largo),
            (x, y + self.largo)
        ])
    
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
            "tipo": "columna",
            "lado": self.lado
        }

        return pd.DataFrame(data, index=[0])

    def render(self, fig, color="grey", borde="black"):
        """
        Dibuja la columna en el fig de plotly
        """
        import plotly.graph_objects as go

        x, y = self.geometria.exterior.xy
        x = list(x)
        y = list(y)

        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            fill="toself",
            mode="lines",
            line=dict(color=borde, width=2),  # marco de la columna
            fillcolor=color,
            opacity=1.0,
            name=self.description,
            showlegend=False
        ))

import numpy as np
from shapely.geometry import Polygon, LineString

class Puerta:
    def __init__(self, ancho, largo, x, y, piso=1, description="puerta", lado=None):
        self.ancho = ancho
        self.largo = largo
        self.x = x
        self.y = y
        self.piso = piso
        self.description = description
        self.lado = lado

        # Atributos de geometría (objetos Shapely)
        self.geometria_marco = None
        self.geometria_hoja = None
        self.geometria_arco = None

        # Inicializar geometría
        self._actualizar_geometria()

    def _actualizar_geometria(self):
        """Calcula la geometría: Apertura hacia la IZQUIERDA e INTERIOR."""
        # 1. Marco
        self.geometria_marco = Polygon([
            (self.x, self.y),
            (self.x + self.ancho, self.y),
            (self.x + self.ancho, self.y + self.largo),
            (self.x, self.y + self.largo)
        ])

        num_puntos = 20

        if self.lado == "top":
            r = self.ancho
            # Pivote esquina superior derecha, abre hacia abajo y a la izquierda (interior)
            pivot_x, pivot_y = self.x + self.ancho, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x, pivot_y - r)])
            # Arco de 270° (3pi/2) a 180° (pi)
            theta = np.linspace(3 * np.pi / 2, np.pi, num_puntos)

        elif self.lado == "bottom":
            r = self.ancho
            # Pivote esquina inferior derecha, abre hacia arriba y a la izquierda (interior)
            pivot_x, pivot_y = self.x + self.ancho, self.y
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x, pivot_y + r)])
            # Arco de 90° (pi/2) a 180° (pi)
            theta = np.linspace(np.pi / 2, np.pi, num_puntos)

        elif self.lado == "left":
            r = self.largo
            # Pivote esquina inferior izquierda, abre hacia la derecha y arriba (interior)
            pivot_x, pivot_y = self.x, self.y
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x, pivot_y + r)])
            # Para que sea a la izquierda desde la vista del usuario entrando:
            # Pivote superior izquierda, abre hacia abajo-derecha
            pivot_x, pivot_y = self.x, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x + r, pivot_y)])
            # Arco de 0° a 270° (o -90°)
            theta = np.linspace(0, -np.pi / 2, num_puntos)

        elif self.lado == "right":
            r = self.largo
            # Pivote esquina superior derecha, abre hacia abajo e izquierda (interior)
            pivot_x, pivot_y = self.x + self.ancho, self.y + self.largo
            self.geometria_hoja = LineString([(pivot_x, pivot_y), (pivot_x - r, pivot_y)])
            # Arco de 180° (pi) a 270° (3pi/2)
            theta = np.linspace(np.pi, 3 * np.pi / 2, num_puntos)

        else:
            self.geometria_hoja = None
            self.geometria_arco = None
            return

        # Generar los puntos del arco
        arco_puntos = [(pivot_x + r * np.cos(t), pivot_y + r * np.sin(t)) for t in theta]
        self.geometria_arco = LineString(arco_puntos)

    def set_position(self, x, y):
        """Actualiza la posición y recalcula toda la geometría."""
        self.x = x
        self.y = y
        self._actualizar_geometria()

    def get_data(self):
        dataframes = []

        # 🔷 Marco (Polygon)
        if self.geometria_marco:
            data_marco = pd.DataFrame([{
                "ancho": self.ancho,
                "largo": self.largo,
                "area": self.ancho * self.largo,
                "piso": self.piso,
                "description": self.description + " marco",
                "geometria": self.geometria_marco,
                "x": self.x,
                "y": self.y,
                "tipo": "puerta_marco",
                "subtipo": "puerta",
                "lado": self.lado
            }])
            dataframes.append(data_marco)

        # 🔥 Hoja (LineString)
        if self.geometria_hoja:
            data_hoja = pd.DataFrame([{
                "ancho": None,
                "largo": None,
                "area": 0,
                "piso": self.piso,
                "description": self.description + " hoja",
                "geometria": self.geometria_hoja,
                "x": self.x,
                "y": self.y,
                "tipo": "puerta_hoja",
                "subtipo": "puerta",
                "lado": self.lado
            }])
            dataframes.append(data_hoja)

        # 🔥 Arco (LineString)
        if self.geometria_arco:
            data_arco = pd.DataFrame([{
                "ancho": None,
                "largo": None,
                "area": 0,
                "piso": self.piso,
                "description": self.description + " arco",
                "geometria": self.geometria_arco,
                "x": self.x,
                "y": self.y,
                "tipo": "puerta_arco",
                "subtipo": "puerta",
                "lado": self.lado
            }])
            dataframes.append(data_arco)

        return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

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

class Muro:
  def __init__(self, ancho, largo, x = 0, y = 0, piso = 1, description = "muro", lado=None):
    self.ancho = ancho
    self.largo = largo
    self.area = ancho * largo
    self.piso = piso
    self.description = description
    self.x = x
    self.y = y
    self.geometria = Polygon([
        (x, y),
        (x + ancho, y),
        (x + ancho, y + largo),
        (x, y + largo)
    ])
    self.lado = lado

  def set_position(self, x, y):
    self.x = x
    self.y = y
    self.geometria = Polygon([
        (x, y),
        (x + self.ancho, y),
        (x + self.ancho, y + self.largo),
        (x, y + self.largo)
    ])

  def dividir(self, offset_inicio, ancho_corte, lado):
        """
        Divide el muro en dos segmentos dejando un hueco (offset_inicio, offset_inicio + ancho_corte).
        Retorna una lista de 2 muros nuevos.
        """
        if self.ancho >= self.largo:
            # Muro horizontal
            # Muro izquierdo
            if offset_inicio > 0:
                muro_izq = Muro(offset_inicio, self.largo, self.x, self.y, self.piso, self.description + " izquierda", lado=lado)
            else:
                muro_izq = None

            # Muro derecho
            resto_derecho = self.ancho - (offset_inicio + ancho_corte)
            if resto_derecho > 0:
                muro_der = Muro(resto_derecho, self.largo, self.x + offset_inicio + ancho_corte, self.y, self.piso, self.description + " derecha", lado=lado)
            else:
                muro_der = None
        else:
            # Muro vertical
            # Muro arriba
            if offset_inicio > 0:
                muro_arriba = Muro(self.ancho, offset_inicio, self.x, self.y, self.piso, self.description + " arriba", lado=lado)
            else:
                muro_arriba = None

            # Muro abajo
            resto_abajo = self.largo - (offset_inicio + ancho_corte)
            if resto_abajo > 0:
                muro_abajo = Muro(self.ancho, resto_abajo, self.x, self.y + offset_inicio + ancho_corte, self.piso, self.description + " abajo", lado=lado)
            else:
                muro_abajo = None

            muro_izq = muro_arriba
            muro_der = muro_abajo

        # Devolver solo los muros válidos
        return [m for m in [muro_izq, muro_der] if m is not None]

  def render(self, fig, color="black"):
    x, y = self.geometria.exterior.xy

    x = list(x)
    y = list(y)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill="toself",
        mode="lines",
        name=self.description,
        line=dict(color=color),
        opacity=1,
        showlegend=False
    ))
  def get_data(self):
    return pd.DataFrame({
        "ancho": [self.ancho],
        "largo": [self.largo],
        "area": [self.area],
        "piso": [self.piso],
        "description": [self.description],
        "geometria": [self.geometria],
        "x": [self.x],
        "y": [self.y],
        "tipo": ["muro"],
        "lado": [self.lado]  # 🔥 opcional pero muy útil
    })
    

class Aula:
  def __init__(self, ancho, largo, x = 0, y = 0, piso = 1, description = "aula"):
    self.ancho = ancho
    self.largo = largo
    self.area = ancho * largo
    self.piso = piso
    self.description = description
    self.x = x
    self.y = y
    self.geometria = Polygon([
        (x, y),
        (x + ancho, y),
        (x + ancho, y + largo),
        (x, y + largo)
    ])
    self.muros=[]
    self.puertas=[]
    self.columnas = []
    self.crear_muros()
    self.crear_columnas()

  def crear_muros(self, grosor=0.3):
    self.muros = []

    x = self.x
    y = self.y
    ancho = self.ancho
    largo = self.largo

    # Muro inferior: ocupa todo el ancho en la base
    muro_inf = Muro(ancho, grosor, x, y, self.piso, "muro inferior")

    # Muro superior: ocupa todo el ancho en la cima
    muro_sup = Muro(ancho, grosor, x, y + largo - grosor, self.piso, "muro superior")

    # Muro izquierdo: entre muro inferior y superior (sin solaparse)
    muro_izq = Muro(grosor, largo - 2 * grosor, x, y + grosor, self.piso, "muro izquierdo")

    # Muro derecho: espejado al izquierdo
    muro_der = Muro(grosor, largo - 2 * grosor, x + ancho - grosor, y + grosor, self.piso, "muro derecho")

    self.muros.extend([muro_inf, muro_sup, muro_izq, muro_der])

  def crear_columnas(self, grosor=0.4):
    """
    Crea una columna en cada esquina del aula.
    grosor: tamaño de la columna (ancho/largo)
    """
    x = self.x
    y = self.y
    ancho = self.ancho
    largo = self.largo

    self.columnas = []

    # Esquina inferior izquierda
    col_inf_izq = Columna(grosor, grosor, x, y, self.piso, "columna inferior izquierda", lado="left")
    self.columnas.append(col_inf_izq)

    # Esquina inferior derecha
    col_inf_der = Columna(grosor, grosor, x + ancho - grosor, y, self.piso, "columna inferior derecha", lado="right")
    self.columnas.append(col_inf_der)

    # Esquina superior izquierda
    col_sup_izq = Columna(grosor, grosor, x, y + largo - grosor, self.piso, "columna superior izquierda", lado="left")
    self.columnas.append(col_sup_izq)

    # Esquina superior derecha
    col_sup_der = Columna(grosor, grosor, x + ancho - grosor, y + largo - grosor, self.piso, "columna superior derecha", lado="right")
    self.columnas.append(col_sup_der)

  def get_data(self):

    dataframes = []

    # 🔷 1. Aula
    data_aula = pd.DataFrame({
        "ancho": self.ancho,
        "largo": self.largo,
        "area": self.area,
        "piso": self.piso,
        "description": self.description,
        "geometria": self.geometria,
        "x": [self.x],
        "y": [self.y],
        "tipo": ["aula"]
    })

    dataframes.append(data_aula)

    # 🔥 2. Muros
    for muro in self.muros:
        if hasattr(muro, "get_data"):
            dataframes.append(muro.get_data())

    # 🔥 3. Columnas
    for col in self.columnas:
        if hasattr(col, "get_data"):
            dataframes.append(col.get_data())

    # 🔥 4. Puertas
    for puerta in self.puertas:
        if hasattr(puerta, "get_data"):
            dataframes.append(puerta.get_data())

    # 🔗 Unir todo
    return pd.concat(dataframes, ignore_index=True)

  def set_position(self, x, y):
    self.x = x
    self.y = y

    # 🔷 actualizar geometría del aula
    self.geometria = Polygon([
        (x, y),
        (x + self.ancho, y),
        (x + self.ancho, y + self.largo),
        (x, y + self.largo)
    ])

    # 🔥 recrear muros en nueva posición
    self.crear_muros()

  def puerta(self, lado="top", ancho_puerta=1.0):
    """
    Crea una puerta en el muro indicado usando la clase Puerta.
    lado: 'top', 'bottom', 'left', 'right'
    ancho_puerta: ancho de la puerta en metros
    """
    muro_obj = None
    for muro in self.muros:
        if lado == "top" and "superior" in muro.description:
            muro_obj = muro
        elif lado == "bottom" and "inferior" in muro.description:
            muro_obj = muro
        elif lado == "left" and "izquierdo" in muro.description:
            muro_obj = muro
        elif lado == "right" and "derecho" in muro.description:
            muro_obj = muro

    if muro_obj is None:
        raise ValueError(f"No se encontró muro para el lado '{lado}'")

    # Centrar la puerta y calcular offset
    if lado in ["top", "bottom"]:
        offset = (muro_obj.ancho - ancho_puerta - 0.6)
        # Dividir el muro en dos partes dejando el hueco
        nuevos_muros = muro_obj.dividir(offset_inicio=offset, ancho_corte=ancho_puerta, lado=lado)
        x_puerta = muro_obj.x + offset
        y_puerta = muro_obj.y
        puerta = Puerta(ancho=ancho_puerta, largo=muro_obj.largo,
                        x=x_puerta, y=y_puerta,
                        piso=self.piso, description=f"puerta {lado}", lado=lado)
    else:  # "left" o "right"
        offset = (muro_obj.largo - ancho_puerta - 0.3)
        nuevos_muros = muro_obj.dividir(offset_inicio=offset, ancho_corte=ancho_puerta, lado=lado)
        x_puerta = muro_obj.x
        y_puerta = muro_obj.y + offset
        puerta = Puerta(ancho=muro_obj.ancho, largo=ancho_puerta,
                        x=x_puerta, y=y_puerta,
                        piso=self.piso, description=f"puerta {lado}", lado=lado)

    # Reemplazar el muro original por los segmentos y agregar la puerta
    self.muros.remove(muro_obj)
    self.muros.extend(nuevos_muros)
    self.puertas.append(puerta)

  def ventana_porcentaje(self, lado="top", porcentaje=0.5, cantidad=1, gap=0.2):
    """
    Crea ventanas tomando un porcentaje del muro para cada ventana.

    lado: 'top', 'bottom', 'left', 'right'
    porcentaje: porcentaje del muro que ocupará cada ventana (0 a 1)
    cantidad: número de ventanas
    gap: espacio entre ventanas
    """
    # 1️⃣ Seleccionar el muro más grande del lado
    muros_lado = [m for m in self.muros if
                   (lado == "top" and "superior" in m.description) or
                   (lado == "bottom" and "inferior" in m.description) or
                   (lado == "left" and "izquierdo" in m.description) or
                   (lado == "right" and "derecho" in m.description)]
    if not muros_lado:
        raise ValueError(f"No hay muros para el lado {lado}")

    # Tomar el muro más grande
    if lado in ["top", "bottom"]:
        ancho_muro = max(muros_lado, key=lambda m: m.ancho).ancho
        ancho_ventana = ancho_muro * porcentaje
    else:  # left o right
        largo_muro = max(muros_lado, key=lambda m: m.largo).largo
        ancho_ventana = largo_muro * porcentaje

    # 2️⃣ Llamar a la función ventana original usando el ancho calculado
    self.ventana(lado=lado, cantidad=cantidad, ancho_ventana=ancho_ventana, gap=gap)

  def ventana(self, lado="top", cantidad=1, ancho_ventana=1.0, gap=0.2):
    """
    Crea ventanas sobre el muro más grande del lado indicado.
    lado: 'top', 'bottom', 'left', 'right'
    cantidad: número de ventanas
    gap: espacio entre ventanas
    ancho_ventana: ancho de cada ventana (horizontal) o alto (vertical)
    alto_ventana: altura de la ventana
    """
    # 1️⃣ Seleccionar el muro del lado indicado y más grande
    muro_obj = None
    max_dim = -1
    for muro in self.muros:
        if lado == "top" and "superior" in muro.description and muro.ancho > max_dim:
            muro_obj = muro
            max_dim = muro.ancho
        elif lado == "bottom" and "inferior" in muro.description and muro.ancho > max_dim:
            muro_obj = muro
            max_dim = muro.ancho
        elif lado == "left" and "izquierdo" in muro.description and muro.largo > max_dim:
            muro_obj = muro
            max_dim = muro.largo
        elif lado == "right" and "derecho" in muro.description and muro.largo > max_dim:
            muro_obj = muro
            max_dim = muro.largo

    if muro_obj is None:
        raise ValueError(f"No se encontró muro para el lado '{lado}'")

    # 2️⃣ Calcular posición inicial de las ventanas
    if lado in ["top", "bottom"]:
        total_gap = gap * (cantidad + 1)
        ancho_total = cantidad * ancho_ventana + total_gap
        x0 = muro_obj.x + (muro_obj.ancho - ancho_total) / 2 + gap
        y_vent = muro_obj.y if lado == "bottom" else muro_obj.y
        for i in range(cantidad):
            vent = Ventana(ancho=ancho_ventana, largo=muro_obj.largo,
                           x=x0, y=y_vent, piso=self.piso,
                           description=f"ventana {lado}")
            # Cortar el muro usando el método dividir
            tramos = muro_obj.dividir(offset_inicio=x0 - muro_obj.x, ancho_corte=ancho_ventana, lado=lado)
            self.muros.remove(muro_obj)
            self.muros.extend(tramos)
            self.muros.append(vent)
            x0 += ancho_ventana + gap
            muro_obj = tramos[0] if tramos else muro_obj  # seguir cortando

    else:  # left o right
        total_gap = gap * (cantidad + 1)
        largo_total = cantidad * ancho_ventana + total_gap
        y0 = muro_obj.y + (muro_obj.largo - largo_total) / 2 + gap
        x_vent = muro_obj.x
        for i in range(cantidad):
            vent = Ventana(muro_obj.ancho, largo=ancho_ventana,
                           x=x_vent, y=y0, piso=self.piso,
                           description=f"ventana {lado}")
            # Cortar el muro usando el método dividir
            tramos = muro_obj.dividir(offset_inicio=y0 - muro_obj.y, ancho_corte=ancho_ventana, lado=lado)
            self.muros.remove(muro_obj)
            self.muros.extend(tramos)
            self.muros.append(vent)
            y0 += ancho_ventana + gap
            muro_obj = tramos[0] if tramos else muro_obj

  def invertir_distribucion(self):
    """
    Invierte la distribución de muros del aula:
    - Muros verticales (left, right) ocupan toda la altura del aula
    - Muros horizontales (top, bottom) ocupan todo el ancho del aula
    """
    # Separar muros por tipo
    horizontales = [m for m in self.muros if "superior" in m.description or "inferior" in m.description]
    verticales   = [m for m in self.muros if "izquierdo" in m.description or "derecho" in m.description]

    # Grosor original
    grosor_horizontal = horizontales[0].largo if horizontales else 0
    grosor_vertical   = verticales[0].ancho if verticales else 0

    # Altura total y ancho total del aula
    alto_total = self.largo
    ancho_total = self.ancho

    # Ajustar muros verticales: ocupar toda la altura entre horizontales
    for m in verticales:
        nuevo_largo = alto_total - 2 * grosor_horizontal
        m.largo = nuevo_largo
        m_y = self.y + grosor_horizontal
        m.set_position(m.x, m_y)

    # Ajustar muros horizontales: ocupar todo el ancho
    for m in horizontales:
        m.ancho = ancho_total
        if "inferior" in m.description:
            m.set_position(self.x, self.y)
        elif "superior" in m.description:
            m.set_position(self.x, self.y + alto_total - grosor_horizontal)

    return self.muros

  def draw(self, fig):
    # 🔷 Dibujar aula
    x, y = self.geometria.exterior.xy
    x = list(x)
    y = list(y)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill="toself",
        mode="lines",
        name=self.description,
        line=dict(color="white"),
        opacity=0.3
    ))

    # 🔥 Dibujar muros
    for muro in self.muros:
        muro.render(fig)

    for col in self.columnas:
        col.render(fig)

    for puerta in self.puertas:
        puerta.render(fig)

  def render(self):
    import plotly.graph_objects as go

    fig = go.Figure()

    # 🔷 Dibujar aula
    x, y = self.geometria.exterior.xy
    x = list(x)
    y = list(y)

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill="toself",
        mode="lines",
        name="Aula",
        line=dict(color="white"),
        opacity=0.3
    ))

    # 🔥 Dibujar muros
    for muro in self.muros:
        muro.render(fig)

    for col in self.columnas:
        col.render(fig)

    for puerta in self.puertas:
        puerta.render(fig)

    # Ajustes visuales
    fig.update_layout(
        title="Aula con muros",
        xaxis=dict(scaleanchor="y", showgrid=True),
        yaxis=dict(showgrid=True),
        showlegend=True
    )

    fig.show()


class Area:
  def __init__(self, ancho, largo, x= 0, y = 0, pisos=[1], description = "Area"):
    self.ancho = ancho
    self.largo = largo
    self.x = x
    self.y = y
    self.area = ancho * largo
    self.geometria = Polygon([(x, y),(x + ancho, y),(x + ancho, y + largo),(x, y + largo)])
    self.pisos = pisos
    self.description = description
    self.aulas = []
    self.subareas = []
    self.pasadizos = []
    self.losas = []

  def get_data(self):

    dataframes = []

    # 🔷 1. Data del área actual
    data_area = pd.DataFrame({
        "ancho": [self.ancho],
        "largo": [self.largo],
        "area": [self.area],
        "pisos": [self.pisos],
        "description": [self.description],
        "geometria": [self.geometria],
        "x": [self.x],
        "y": [self.y],
        "tipo": ["area"]
    })

    dataframes.append(data_area)

    # 🔥 2. Aulas
    for aula in self.aulas:
        if hasattr(aula, "get_data"):
            dataframes.append(aula.get_data())

    # 🔥 3. Subáreas (RECURSIVO 🔥)
    for subarea in self.subareas:
        if hasattr(subarea, "get_data"):
            dataframes.append(subarea.get_data())

    # 🔥 4. Pasadizos
    for pas in self.pasadizos:
        if hasattr(pas, "get_data"):
            dataframes.append(pas.get_data())

    # 🔥 5. Losas
    for losa in self.losas:
        if hasattr(losa, "get_data"):
            dataframes.append(losa.get_data())

    # 🔗 Unir todo
    return pd.concat(dataframes, ignore_index=True)

  def sumar_anchos_aulas_por_piso(self, numero_piso):
    """Suma el ancho de todas las aulas cuyo atributo piso sea igual a numero_piso."""
    # Cambiamos 'in' por '==' porque aula.piso es un entero
    return sum(aula.ancho for aula in self.aulas if getattr(aula, 'piso', None) == numero_piso)

  def sumar_largos_aulas_por_piso(self, numero_piso):
    """Suma el largo de todas las aulas cuyo atributo piso sea igual a numero_piso."""
    total_largo = sum(aula.largo for aula in self.aulas if aula.piso == numero_piso)
    return total_largo

  def centrar_losas(self, piso=None):
    """
    Desplaza todas las losas dentro del área (o del piso indicado)
    para que el conjunto quede centrado, sin alterar su orientación.
    """
    # 1. Filtrar losas por el piso especificado
    losas_filtradas = self.losas if piso is None else [L for L in self.losas if L.piso == piso]

    if not losas_filtradas:
        return  # No hay nada que mover

    # 2. Obtener el Bounding Box (Extensión total) del conjunto de losas
    x_min = min(L.x for L in losas_filtradas)
    x_max = max(L.x + L.ancho for L in losas_filtradas)
    y_min = min(L.y for L in losas_filtradas)
    y_max = max(L.y + L.largo for L in losas_filtradas)

    ancho_conjunto = x_max - x_min
    largo_conjunto = y_max - y_min

    # 3. Calcular el desplazamiento necesario (Offset)
    # Buscamos que el centro del conjunto coincida con el centro del Area (self)
    offset_x = self.x + (self.ancho - ancho_conjunto) / 2 - x_min
    offset_y = self.y + (self.largo - largo_conjunto) / 2 - y_min

    # 4. Aplicar desplazamiento a cada losa y actualizar su geometría
    from shapely.geometry import Polygon

    for losa in losas_filtradas:
        # Solo sumamos el offset, manteniendo ancho y largo originales (sin girar)
        losa.x += offset_x
        losa.y += offset_y

        if hasattr(losa, "geometria"):
            # Re-calculamos el polígono en la nueva posición
            losa.geometria = Polygon([
                (losa.x, losa.y),
                (losa.x + losa.ancho, losa.y),
                (losa.x + losa.ancho, losa.y + losa.largo),
                (losa.x, losa.y + losa.largo)
            ])

        # Si la losa tiene elementos internos (mallas, líneas de cancha),
        # asegúrate de que su clase Losa también actualice sus coordenadas internas.

  def centrar_pasadizos(self, piso=None):
    """
    Centra todos los pasadizos dentro del área (o solo del piso indicado).
    """
    pasadizos_filtrados = self.pasadizos if piso is None else [p for p in self.pasadizos if p.piso == piso]

    if not pasadizos_filtrados:
        return  # No hay pasadizos que centrar

    # 1. Calcular el bounding box (el bloque total) de los pasadizos
    x_min = min(p.x for p in pasadizos_filtrados)
    x_max = max(p.x + p.ancho for p in pasadizos_filtrados)
    y_min = min(p.y for p in pasadizos_filtrados)
    y_max = max(p.y + p.largo for p in pasadizos_filtrados)

    ancho_bloque = x_max - x_min
    largo_bloque = y_max - y_min

    # 2. Calcular offsets respecto al centro del Area principal
    offset_x = self.x + (self.ancho - ancho_bloque) / 2 - x_min
    offset_y = self.y + (self.largo - largo_bloque) / 2 - y_min

    # 3. Mover pasadizos y actualizar su geometría
    for pas in pasadizos_filtrados:
        pas.x += offset_x
        pas.y += offset_y

        if hasattr(pas, "geometria"):
            # Si usas Polygon de shapely:
            from shapely.geometry import Polygon
            pas.geometria = Polygon([
                (pas.x, pas.y),
                (pas.x + pas.ancho, pas.y),
                (pas.x + pas.ancho, pas.y + pas.largo),
                (pas.x, pas.y + pas.largo)
            ])

        # Si el Pasadizo tiene muros internos, puertas o columnas,
        # deberías replicar aquí el bucle de actualización que usamos en aulas.

  def centrar_aulas(self, piso=None):
    """
    Centra todas las aulas dentro del área (o solo del piso indicado)
    y mueve también todos sus muros.
    """
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if not aulas_filtradas:
        return  # No hay aulas que centrar

    # Calcular bounding box de todas las aulas
    x_min = min(aula.x for aula in aulas_filtradas)
    x_max = max(aula.x + aula.ancho for aula in aulas_filtradas)
    y_min = min(aula.y for aula in aulas_filtradas)
    y_max = max(aula.y + aula.largo for aula in aulas_filtradas)

    ancho_aulas = x_max - x_min
    largo_aulas = y_max - y_min

    # Calcular offsets para centrar
    offset_x = self.x + (self.ancho - ancho_aulas) / 2 - x_min
    offset_y = self.y + (self.largo - largo_aulas) / 2 - y_min

    # Mover aulas y sus muros
    for aula in aulas_filtradas:
        aula.x += offset_x
        aula.y += offset_y

        # Actualizar geometría del aula
        if hasattr(aula, "geometria"):
            aula.geometria = Polygon([
                (aula.x, aula.y),
                (aula.x + aula.ancho, aula.y),
                (aula.x + aula.ancho, aula.y + aula.largo),
                (aula.x, aula.y + aula.largo)
            ])

        # Mover todos los muros del aula
        if hasattr(aula, "muros"):
            for muro in aula.muros:
                muro.x += offset_x
                muro.y += offset_y
                # Actualizar geometría si existe
                if hasattr(muro, "geometria"):
                    muro.geometria = Polygon([
                        (muro.x, muro.y),
                        (muro.x + muro.ancho, muro.y),
                        (muro.x + muro.ancho, muro.y + muro.largo),
                        (muro.x, muro.y + muro.largo)
                    ])
        # Mover todas las columnas del aula
        if hasattr(aula, "columnas"):
            for col in aula.columnas:
                col.x += offset_x
                col.y += offset_y
                if hasattr(col, "geometria"):
                    col.geometria = Polygon([
                        (col.x, col.y),
                        (col.x + col.ancho, col.y),
                        (col.x + col.ancho, col.y + col.largo),
                        (col.x, col.y + col.largo)
                    ])
        # --- Mover todas las puertas del aula ---
        if hasattr(aula, "puertas"):
            for puerta in aula.puertas:
                # 1. Actualizar coordenadas básicas
                puerta.x += offset_x
                puerta.y += offset_y

                # 2. Forzar el recálculo de la geometría (Marco, Hoja y Arco)
                # Asegúrate de que el método se llame así en tu clase Puerta
                if hasattr(puerta, "_actualizar_geometria"):
                    puerta._actualizar_geometria()

  def pasadizo(self, ancho, largo, piso=1, description="pasadiso"):
    pasadizo_piso = [a for a in self.pasadizos if a.piso == piso]

    # Coordenadas iniciales
    if not pasadizo_piso:
        abs_x, abs_y = self.x, self.y
    else:
        # Colocar al lado derecho de la última aula del mismo piso
        ultima = pasadizo_piso[-1]
        abs_x = ultima.x + ultima.ancho
        abs_y = ultima.y

        # Si se sale del límite del área, mover a la siguiente fila dentro del mismo piso
        if abs_x + ancho > self.x + self.ancho:
            abs_x = self.x
            abs_y = ultima.y + ultima.largo

    # Verificar que la nueva aula quepa dentro del área en el piso actual
    if abs_y + largo > self.y + self.largo:
        # Subir al siguiente piso
        piso += 1
        abs_x, abs_y = self.x, self.y

    # Crear y agregar el aula
    nueva = Pasadizo(ancho, largo, abs_x, abs_y, piso, description)
    self.pasadizos.append(nueva)

  def losa(self, ancho, largo, piso=1, description="losa"):
    losa_piso = [a for a in self.pasadizos if a.piso == piso]

    # Coordenadas iniciales
    if not losa_piso:
        abs_x, abs_y = self.x, self.y
    else:
        # Colocar al lado derecho de la última aula del mismo piso
        ultima = losa_piso[-1]
        abs_x = ultima.x + ultima.ancho
        abs_y = ultima.y

        # Si se sale del límite del área, mover a la siguiente fila dentro del mismo piso
        if abs_x + ancho > self.x + self.ancho:
            abs_x = self.x
            abs_y = ultima.y + ultima.largo

    # Verificar que la nueva aula quepa dentro del área en el piso actual
    if abs_y + largo > self.y + self.largo:
        # Subir al siguiente piso
        piso += 1
        abs_x, abs_y = self.x, self.y

    # Crear y agregar el aula
    nueva = Losa(ancho, largo, abs_x, abs_y, piso, description)
    self.losas.append(nueva)

  def insertar_losas(self, cantidad_losas, gap=0.2, piso=1, ancho_losa=3, largo_losa=3):
    """
    Inserta losas dentro del área respetando:
    - máximo 3 losas
    - separación (gap)
    - límites del área

    Las losas se colocan en fila horizontal (y bajan si no hay espacio).
    """

    # 🔒 Limitar a máximo 3
    cantidad_losas = min(cantidad_losas, 3)

    if cantidad_losas <= 0:
        return []

    losas_creadas = []

    # Punto inicial
    x_actual = self.x
    y_actual = self.y

    for i in range(cantidad_losas):

        # 🔁 Si no entra en horizontal → bajar fila
        if x_actual + ancho_losa > self.x + self.ancho:
            x_actual = self.x
            y_actual += largo_losa + gap

        # ❌ Si ya no entra en vertical → parar
        if y_actual + largo_losa > self.y + self.largo:
            break

        # ✅ Crear losa
        nueva = Losa(ancho_losa, largo_losa, x_actual, y_actual, piso, f"losa_{i+1}")
        self.losas.append(nueva)
        losas_creadas.append(nueva)

        # ➡️ Avanzar en X con gap
        x_actual += ancho_losa + gap

    return losas_creadas

  def aula(self, ancho, largo, piso=1, description="aula", lado="right"):
    """
    Agrega un aula al área, colocándola al lado derecho de la última aula agregada en el mismo piso.
    Si no hay espacio en el piso actual, sube automáticamente al siguiente piso.
    """
    # Filtrar aulas del mismo piso
    aulas_piso = [a for a in self.aulas if a.piso == piso]

    # Coordenadas iniciales
    if not aulas_piso:
        abs_x, abs_y = self.x, self.y
    else:
        # Colocar al lado derecho de la última aula del mismo piso
        ultima = aulas_piso[-1]
        abs_x = ultima.x + ultima.ancho
        abs_y = ultima.y

        # Si se sale del límite del área, mover a la siguiente fila dentro del mismo piso
        if abs_x + ancho > self.x + self.ancho:
            abs_x = self.x
            abs_y = ultima.y + ultima.largo

    # Verificar que la nueva aula quepa dentro del área en el piso actual
    if abs_y + largo > self.y + self.largo:
        # Subir al siguiente piso
        piso += 1
        abs_x, abs_y = self.x, self.y

    # Crear y agregar el aula
    nueva = Aula(ancho, largo, abs_x, abs_y, piso, description)
    self.aulas.append(nueva)

    # Solo unir muros si hay al menos 2 aulas en el mismo piso
    aulas_mismo_piso = [a for a in self.aulas if a.piso == nueva.piso]
    if len(aulas_mismo_piso) > 1:
        tipo_apilamiento = self.tipo_apilamiento_penultimo_ultimo(piso=nueva.piso)
        if tipo_apilamiento == "vertical":
            self.unir_penultimo_y_ultimo(piso=nueva.piso)
            self.unir_penultima_y_ultima_columnas(piso=nueva.piso)
        elif tipo_apilamiento == "horizontal":
            self.unir_penultimo_y_ultimo_horizontal(piso=nueva.piso)
            self.unir_penultima_y_ultima_columnas_horizontal(piso=nueva.piso)

    if lado=="right":
      nueva.puerta("right")
      nueva.ventana_porcentaje("right", cantidad= 1, gap=0.2, porcentaje=0.7)
      nueva.ventana_porcentaje("left", cantidad= 2, gap=0.5, porcentaje= 0.5)

    elif lado=="left":
      nueva.puerta("left")
      nueva.ventana_porcentaje("left", cantidad= 1, gap=0.2, porcentaje=0.7)
      nueva.ventana_porcentaje("right", cantidad= 2, gap=0.5, porcentaje= 0.5)

    elif lado=="top":
      nueva.puerta("bottom")
      nueva.ventana_porcentaje("bottom", cantidad= 1, gap=0.2, porcentaje=0.7)
      nueva.ventana_porcentaje("top", cantidad= 2, gap=0.5, porcentaje= 0.5)

    elif lado=="bottom":
      nueva.puerta("top")
      nueva.ventana_porcentaje("top", cantidad= 1, gap=0.2, porcentaje=0.7)
      nueva.ventana_porcentaje("bottom", cantidad= 2, gap=0.5, porcentaje= 0.5)

    return nueva

  def unir_penultimo_y_ultimo(self, piso=None):
    """
    Toma el penúltimo y último aula agregadas en el mismo piso,
    detecta muros horizontales que se tocan, elimina el duplicado del último aula,
    y ajusta verticalmente los muros horizontales:
      - penúltimo aula crece hacia arriba la mitad del muro
      - último aula crece hacia abajo la mitad del muro
    También considera muros verticales para posibles ajustes.
    """
    # Filtrar aulas por piso si se especifica
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if len(aulas_filtradas) < 2:
        raise ValueError("No hay suficientes aulas para unir muros en este piso")

    penultima, ultima = aulas_filtradas[-2], aulas_filtradas[-1]
    muros_a_eliminar = []

    for muro_nuevo in ultima.muros:
        if muro_nuevo.ancho > muro_nuevo.largo:  # horizontal
            for muro_existente in penultima.muros:
                if muro_existente.ancho > muro_existente.largo:
                    if muro_nuevo.geometria.touches(muro_existente.geometria):
                        muros_a_eliminar.append(muro_nuevo)

                        # Ajustar muros horizontales
                        muro_existente.set_position(muro_existente.x, muro_existente.y + muro_existente.largo / 2)  # penúltimo hacia arriba
                        muro_nuevo.set_position(muro_nuevo.x, muro_nuevo.y - muro_nuevo.largo / 2)  # último hacia abajo
                        break

        elif muro_nuevo.largo > muro_nuevo.ancho:  # vertical
            for muro_existente in penultima.muros:
                if muro_existente.largo > muro_existente.ancho:
                    # opcional: ajustar si los verticales se tocan o alinean
                    if muro_nuevo.geometria.touches(muro_existente.geometria):
                        # Ejemplo: mover verticales ligeramente hacia el centro para unir
                        centro_x = (muro_existente.x + muro_nuevo.x) / 2
                        muro_existente.set_position(centro_x, muro_existente.y)
                        muro_nuevo.set_position(centro_x, muro_nuevo.y)
                        break

    # Eliminar muros duplicados del último aula
    for muro in muros_a_eliminar:
        ultima.muros.remove(muro)

    return muros_a_eliminar


  def unir_penultimo_y_ultimo_horizontal(self, piso=None):
    """
    Toma el penúltimo y último aula agregadas en el mismo piso,
    detecta muros verticales contiguos y elimina el duplicado del último aula.
    Solo afecta muros verticales; muros horizontales se mantienen.
    Además mueve la mitad del largo del muro restante para alinearlo correctamente.
    """
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if len(aulas_filtradas) < 2:
        raise ValueError("No hay suficientes aulas para unir muros verticales en este piso")

    penultima, ultima = aulas_filtradas[-2], aulas_filtradas[-1]

    muros_a_eliminar = []

    for muro_nuevo in ultima.muros:
        # Solo muros verticales
        if muro_nuevo.largo > muro_nuevo.ancho:
            for muro_existente in penultima.muros:
                if muro_existente.largo > muro_existente.ancho:
                    # Verificar si los muros verticales se tocan
                    if muro_nuevo.geometria.touches(muro_existente.geometria):
                        muros_a_eliminar.append(muro_nuevo)

                        # Mover la mitad del largo del muro existente
                        if hasattr(muro_existente, 'set_position'):
                            muro_existente.set_position(
                                muro_existente.x + muro_existente.ancho / 2,
                                muro_existente.y
                            )
                        break

    # Eliminar muros duplicados
    for muro in muros_a_eliminar:
        ultima.muros.remove(muro)

    return muros_a_eliminar

  def unir_penultima_y_ultima_columnas(self, piso=None):
    """
    Une columnas del penúltimo y último aula en el mismo piso:
      - Detecta columnas que se tocan o están muy cerca
      - Elimina las duplicadas del último aula
      - La columna que queda (del penúltimo aula) se mueve hacia arriba la mitad de su altura
    """
    # Filtrar aulas por piso si se especifica
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if len(aulas_filtradas) < 2:
        raise ValueError("No hay suficientes aulas para unir columnas en este piso")

    penultima, ultima = aulas_filtradas[-2], aulas_filtradas[-1]
    columnas_a_eliminar = []

    for col_nueva in ultima.columnas:
        for col_existente in penultima.columnas:
            # Detectar si se tocan o están muy cerca
            if col_nueva.geometria.touches(col_existente.geometria):
                # Eliminar la columna duplicada del último aula
                columnas_a_eliminar.append(col_nueva)

                # Mover la columna del penúltimo aula hacia arriba la mitad de su altura
                col_existente.set_position(col_existente.x, col_existente.y + col_existente.largo / 2)
                break  # ya encontramos un duplicado, no revisar más columnas

    # Eliminar las columnas duplicadas del último aula
    for col in columnas_a_eliminar:
        ultima.columnas.remove(col)

    return columnas_a_eliminar

  def unir_penultima_y_ultima_columnas_horizontal(self, piso=None):
    """
    Une columnas del penúltimo y último aula en el mismo piso:
      - Detecta columnas que se tocan o están muy cerca
      - Elimina las duplicadas del último aula
      - La columna que queda (del penúltimo aula) se mueve hacia la derecha la mitad de su ancho
    """
    # Filtrar aulas por piso si se especifica
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if len(aulas_filtradas) < 2:
        raise ValueError("No hay suficientes aulas para unir columnas en este piso")

    penultima, ultima = aulas_filtradas[-2], aulas_filtradas[-1]
    columnas_a_eliminar = []

    for col_nueva in ultima.columnas:
        for col_existente in penultima.columnas:
            # Detectar si se tocan o están muy cerca
            if col_nueva.geometria.touches(col_existente.geometria):
                # Eliminar la columna duplicada del último aula
                columnas_a_eliminar.append(col_nueva)

                # Mover la columna del penúltimo aula hacia la derecha la mitad de su ancho
                col_existente.set_position(col_existente.x + col_existente.ancho / 2, col_existente.y)
                break  # ya encontramos un duplicado, no revisar más columnas

    # Eliminar las columnas duplicadas del último aula
    for col in columnas_a_eliminar:
        ultima.columnas.remove(col)

    return columnas_a_eliminar

  def tipo_apilamiento_penultimo_ultimo(self, piso=None):
    """
    Retorna 'vertical' si las aulas están apiladas una sobre otra,
    'horizontal' si están lado a lado,
    o None si no se puede determinar claramente.
    Solo considera aulas del mismo piso si se indica.
    """
    aulas_filtradas = self.aulas if piso is None else [a for a in self.aulas if a.piso == piso]

    if len(aulas_filtradas) < 2:
        return None

    penultima, ultima = aulas_filtradas[-2], aulas_filtradas[-1]

    tol = 1e-6

    if abs(penultima.x - ultima.x) < tol:
        return "vertical"
    elif abs(penultima.y - ultima.y) < tol:
        return "horizontal"
    else:
        return None

  def render(self):
    import plotly.graph_objects as go

    fig = go.Figure()

    # 🔷 Área principal
    x, y = self.geometria.exterior.xy

    fig.add_trace(go.Scatter(
        x=list(x),
        y=list(y),
        fill="toself",
        fillcolor="white",
        line=dict(color="gray", width=2),
        name=self.description
    ))

    # 🔥 Renderizar aulas
    for aula in self.aulas:
        aula.draw(fig)

    fig.update_layout(
        title=f"{self.description}",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=700,
        height=500,
        showlegend=True
    )

    fig.show()

  def areas_m(self, *medidas, direccion="horizontal"):
    """
    Divide el Motor2D en subáreas usando medidas absolutas en metros o 'auto'.
    Solo se permite un 'auto', que se ajustará automáticamente para llenar el espacio restante.

    Ejemplo:
        motor.areas_por_metros_o_auto(3, "auto", 2, direccion="horizontal")
        motor.areas_por_metros_o_auto(4, "auto", direccion="vertical")
    """
    resultados = []

    if direccion not in ["horizontal", "vertical"]:
        raise ValueError("direccion debe ser 'horizontal' o 'vertical'")

    # Contar cuántos 'auto' hay
    autos = sum(1 for m in medidas if m == "auto")
    if autos > 1:
        raise ValueError("Solo se permite un 'auto' por dirección")

    # Calcular espacio total y sumatoria de valores fijos
    if direccion == "horizontal":
        total = self.ancho
    else:
        total = self.largo

    suma_fijos = sum(m for m in medidas if m != "auto")
    if suma_fijos > total:
        raise ValueError("La suma de medidas fijas excede el tamaño del Motor2D")

    # Si hay 'auto', calcular su tamaño
    medidas_finales = []
    for m in medidas:
        if m == "auto":
            medidas_finales.append(total - suma_fijos)
        else:
            medidas_finales.append(m)

    # Crear subáreas
    if direccion == "horizontal":
        x0 = self.x
        for w in medidas_finales:
            sub = Area(
                ancho=w,
                largo=self.largo,
                x=x0,
                y=self.y
            )
            resultados.append(sub)
            x0 += w
    else:
        y0 = self.y
        for l in medidas_finales:
            sub = Area(
                ancho=self.ancho,
                largo=l,
                x=self.x,
                y=y0
            )
            resultados.append(sub)
            y0 += l

    self.subareas = resultados
    return resultados

  def draw(self, fig=None):
    """
    Renderiza el área y sus aulas. Si se pasa un fig externo, se dibuja allí.
    Esto permite que otra clase, como Render2d, maneje el renderizado final.
    """
    import plotly.graph_objects as go

    # Crear figura nueva solo si no se pasa una externa
    if fig is None:
        fig = go.Figure()

    # 🔷 Área principal
    x, y = self.geometria.exterior.xy
    fig.add_trace(go.Scatter(
        x=list(x),
        y=list(y),
        fill="toself",
        fillcolor="white",
        line=dict(color="gray", width=2, dash="dot"),
        name=self.description
    ))

    # 🔥 Renderizar aulas
    for aula in self.aulas:
        if hasattr(aula, "draw"):
            aula.draw(fig)

    for area in self.subareas:
        if hasattr(area, "draw"):
            area.draw(fig)

    for pas in self.pasadizos:
        pas.draw(fig)

    for losa in self.losas:
        losa.draw(fig)

    # Configuración de layout (puede ser modificada por Render2d si se desea)
    fig.update_layout(
        title=f"{self.description}",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=700,
        height=500,
        showlegend=True
    )

    # No hacer fig.show() aquí para que otra clase lo maneje
    return fig

class Motor2D:
  def __init__(self, ancho, largo, x= 0, y = 0, piso=1, description = "Render"):
    self.ancho = ancho
    self.largo = largo
    self.x = x
    self.y = y
    self.area = ancho * largo
    self.geometria = Polygon([(x, y),(x + ancho, y),(x + ancho, y + largo),(x, y + largo)])
    self.piso = piso
    self.description = description
    self.subareas = []

  def areas(self, *pesos, direccion="horizontal"):
        """
        Divide el Motor2D en sub-motores según los pesos.
        Retorna una lista de Motor2D.
        """
        total_pesos = sum(pesos)
        resultados = []

        if direccion not in ["horizontal", "vertical"]:
            raise ValueError("direccion debe ser 'horizontal' o 'vertical'")

        if direccion == "horizontal":
            x0 = self.x
            for peso in pesos:
                w = (peso / total_pesos) * self.ancho
                sub = Area(
                    ancho=w,
                    largo=self.largo,
                    x=x0,
                    y=self.y
                )
                resultados.append(sub)
                x0 += w
        else:
            y0 = self.y
            for peso in pesos:
                l = (peso / total_pesos) * self.largo
                sub = Area(
                    ancho=self.ancho,
                    largo=l,
                    x=self.x,
                    y=y0
                )
                resultados.append(sub)
                y0 += l
        self.subareas = resultados
        return resultados

  def areas_m(self, *medidas, direccion="horizontal"):
    """
    Divide el Motor2D en subáreas usando medidas absolutas en metros o 'auto'.
    Solo se permite un 'auto', que se ajustará automáticamente para llenar el espacio restante.

    Ejemplo:
        motor.areas_por_metros_o_auto(3, "auto", 2, direccion="horizontal")
        motor.areas_por_metros_o_auto(4, "auto", direccion="vertical")
    """
    resultados = []

    if direccion not in ["horizontal", "vertical"]:
        raise ValueError("direccion debe ser 'horizontal' o 'vertical'")

    # Contar cuántos 'auto' hay
    autos = sum(1 for m in medidas if m == "auto")
    if autos > 1:
        raise ValueError("Solo se permite un 'auto' por dirección")

    # Calcular espacio total y sumatoria de valores fijos
    if direccion == "horizontal":
        total = self.ancho
    else:
        total = self.largo

    suma_fijos = sum(m for m in medidas if m != "auto")
    if suma_fijos > total:
        raise ValueError("La suma de medidas fijas excede el tamaño del Motor2D")

    # Si hay 'auto', calcular su tamaño
    medidas_finales = []
    for m in medidas:
        if m == "auto":
            medidas_finales.append(total - suma_fijos)
        else:
            medidas_finales.append(m)

    # Crear subáreas
    if direccion == "horizontal":
        x0 = self.x
        for w in medidas_finales:
            sub = Area(
                ancho=w,
                largo=self.largo,
                x=x0,
                y=self.y
            )
            resultados.append(sub)
            x0 += w
    else:
        y0 = self.y
        for l in medidas_finales:
            sub = Area(
                ancho=self.ancho,
                largo=l,
                x=self.x,
                y=y0
            )
            resultados.append(sub)
            y0 += l

    self.subareas = resultados
    return resultados

  def get_data(self):
      """
      Devuelve un DataFrame con los datos del Motor2D y todas sus subáreas recursivamente.
      """
      # Datos del área principal
      data = {
          "ancho": self.ancho,
          "largo": self.largo,
          "area": self.area,
          "piso": self.piso,
          "description": self.description,
          "geometria": self.geometria,
          "tipo":"render",
          "x": self.x,
          "y": self.y
      }
      df = pd.DataFrame(data, index=[0])

      # Recorrer subáreas recursivamente
      for sub in self.subareas:
          df = pd.concat([df, sub.get_data()], ignore_index=True)

      return df

  def render(self):
    """
    Renderiza el Motor2D y todas sus subáreas.
    Devuelve un objeto plotly Figure listo para mostrar.
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    # 🔷 Dibujar el Motor2D principal como área base
    x, y = self.geometria.exterior.xy
    fig.add_trace(go.Scatter(
        x=list(x),
        y=list(y),
        fill="toself",
        fillcolor="white",
        line=dict(color="black", width=2),
        name=self.description
    ))

    # 🔥 Dibujar todas las subáreas
    for sub in self.subareas:
        # Cada sub es un Area, usamos su render sobre la misma figura
        sub.draw(fig=fig)

    # Configuración de layout
    fig.update_layout(
        title=f"{self.description}",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=800,
        height=600,
        showlegend=True
    )

    return fig