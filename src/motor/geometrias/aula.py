import pandas as pd
from shapely import Polygon

from src.motor.geometrias.losa import Losa
from src.motor.geometrias.ventana import Ventana
from src.motor.geometrias.puerta import Puerta
from src.motor.geometrias.columna import Columna
from src.motor.geometrias.muro import Muro
import plotly.graph_objects as go

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
    self.geometria_3d = None
    self.muros=[]
    self.puertas=[]
    self.columnas = []
    self.crear_muros()
    self.crear_columnas()
    self.techo = None
    self.crear_techo()

  def crear_techo(self, espesor=0.3, altura_piso=2.7):

    z_base = self.piso * altura_piso  # 🔥 2.7

    self.techo = Losa(
        ancho=self.ancho,
        largo=self.largo,
        x=self.x,
        y=self.y,
        piso=self.piso,
        description=f"techo {self.description}",
        espesor=espesor,
        z_base=z_base
    )
    return self.techo

  def crear_muros(self, grosor=0.15):
    self.muros = []

    x = self.x
    y = self.y
    ancho = self.ancho
    largo = self.largo

    # Muro inferior: ocupa todo el ancho en la base
    muro_inf = Muro(ancho=ancho, largo= grosor, x=x, y=y, piso=self.piso, description="muro inferior")

    # Muro superior: ocupa todo el ancho en la cima
    muro_sup = Muro(ancho=ancho, largo=grosor, x=x, y=y + largo - grosor, piso=self.piso,description= "muro superior")

    # Muro izquierdo: entre muro inferior y superior (sin solaparse)
    muro_izq = Muro(ancho=grosor, largo=largo - 2 * grosor, x=x, y=y + grosor, piso=self.piso, description="muro izquierdo")

    # Muro derecho: espejado al izquierdo
    muro_der = Muro(ancho=grosor, largo=largo - 2 * grosor, x=x + ancho - grosor, y=y + grosor, piso=self.piso, description="muro derecho")

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
        "ancho": [self.ancho],
        "largo": [self.largo],
        "area": [self.area],
        "piso": [self.piso],
        "description": [self.description],
        "geometria": [self.geometria],
        "x": [self.x],
        "y": [self.y],
        "tipo": ["aula"],
        "geometria_3d" : [self.geometria_3d],
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

    if self.techo and hasattr(self.techo, "get_data"):
        dataframes.append(self.techo.get_data())

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

    if self.techo:
        self.techo.set_position(x, y)

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
        pass
        # raise ValueError(f"No se encontró muro para el lado '{lado}'")

    # Centrar la puerta y calcular offset
    if lado in ["top", "bottom"]:
        offset = (muro_obj.ancho - ancho_puerta - 0.6)
        nuevos_muros = muro_obj.dividir(offset_inicio=offset, ancho_corte=ancho_puerta, lado=lado)
        x_puerta = muro_obj.x + offset
        y_puerta = muro_obj.y
        # Corregido con argumentos nombrados
        puerta_obj = Puerta(ancho=ancho_puerta, largo=muro_obj.largo,
                            x=x_puerta, y=y_puerta,
                            piso=self.piso, description=f"puerta {lado}", lado=lado)
    else:  # "left" o "right"
        offset = (muro_obj.largo - ancho_puerta - 0.3)
        nuevos_muros = muro_obj.dividir(offset_inicio=offset, ancho_corte=ancho_puerta, lado=lado)
        x_puerta = muro_obj.x
        y_puerta = muro_obj.y + offset
        # Corregido con argumentos nombrados
        puerta_obj = Puerta(ancho=muro_obj.ancho, largo=ancho_puerta,
                            x=x_puerta, y=y_puerta,
                            piso=self.piso, description=f"puerta {lado}", lado=lado)

    # Reemplazar el muro original por los segmentos y agregar la puerta
    self.muros.remove(muro_obj)
    self.muros.extend(nuevos_muros)
    self.puertas.append(puerta_obj)

  def ventana_porcentaje(self, lado="top", porcentaje=0.5, cantidad=1, gap=0.2, h_alfeizar=1.2, h_ventana=1.2, h_entrepiso=2.7):
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
    self.ventana(lado=lado, cantidad=cantidad, ancho_ventana=ancho_ventana, gap=gap, h_alfeizar=h_alfeizar, h_ventana=h_ventana, h_entrepiso=h_entrepiso)

  def ventana(self, lado="top", cantidad=1, ancho_ventana=1.0, gap=0.2, h_alfeizar=1.2, h_ventana=1.2, h_entrepiso = 2.7):
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
                           description=f"ventana {lado}", h_alfeizar=h_alfeizar, h_ventana=h_ventana, h_entrepiso=h_entrepiso)
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
                           description=f"ventana {lado}", h_alfeizar=h_alfeizar, h_ventana=h_ventana, h_entrepiso=h_entrepiso)
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
  def render_3d(self, fig):
    """
    Añade todos los componentes del aula (muros, ventanas, columnas, puertas)
    a una instancia de go.Figure() existente.
    """
    # 1. Renderizar Muros y Ventanas
    # Como las ventanas se guardan en self.muros al dividir, render_3d funciona para ambos
    for muro in self.muros:
        if hasattr(muro, 'render_3d'):
            muro.render_3d(fig)

    # 2. Renderizar Columnas
    for col in self.columnas:
        if hasattr(col, 'render_3d'):
            col.render_3d(fig)

    # 3. Renderizar Puertas
    for puerta in self.puertas:
        if hasattr(puerta, 'render_3d'):
            puerta.render_3d(fig)

    if self.techo:
      self.techo.render_3d(fig)

  def draw_3d(self):
    """
    Crea una nueva figura, ejecuta el render_3d y configura la escena para mostrar el aula.
    """
    import plotly.graph_objects as go

    fig = go.Figure()

    # Llamamos al método que inyecta las geometrías
    self.render_3d(fig)

    # Configuración exclusiva para la visualización del aula individual
    fig.update_layout(
        title=f"Render 3D - {self.description} (Piso {self.piso})",
        scene=dict(
            aspectmode='data', # Mantiene las proporciones reales (1m = 1 unidad)
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            xaxis=dict(gridcolor='rgb(200, 200, 200)'),
            yaxis=dict(gridcolor='rgb(200, 200, 200)'),
            zaxis=dict(gridcolor='rgb(200, 200, 200)'),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True
    )

    fig.show()
