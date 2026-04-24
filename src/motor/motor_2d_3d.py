import pandas as pd
from shapely import Polygon

from src.motor.geometrias.area import Area

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

    # Convertir medidas a una lista para poder modificarlas
    medidas_list = list(medidas)

    # Calcular espacio total y sumatoria de valores fijos
    if direccion == "horizontal":
        total = self.ancho
    else:
        total = self.largo

    suma_fijos = sum(m for m in medidas_list if m != "auto")

    if suma_fijos > total:
        print(f"⚠️ Aviso: Las medidas fijas ({suma_fijos}) superan el total ({total}). Se escalarán proporcionalmente.")
        factor_escala = total / suma_fijos
        medidas_list = [m * factor_escala if isinstance(m, (int, float)) else m for m in medidas_list]
        # Recalcular suma_fijos con las medidas escaladas
        suma_fijos = sum(m for m in medidas_list if m != "auto")

    # Si hay 'auto', calcular su tamaño
    medidas_finales = []
    for m in medidas_list:
        if m == "auto":
            auto_size = max(0, total - suma_fijos) # Asegurarse que no sea negativo
            medidas_finales.append(auto_size)
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

  def render_3d(self):
        """
        Punto de entrada principal para el renderizado 3D.
        Crea la figura y lanza la cadena de dibujo de subáreas.
        """
        import plotly.graph_objects as go
        fig = go.Figure()

        # 1. Dibujar el plano base (Terreno)
        x_t, y_t = self.geometria.exterior.xy
        fig.add_trace(go.Mesh3d(
            x=list(x_t), y=list(y_t), z=[0] * len(x_t),
            opacity=0.1, color="black", name="Terreno Base"
        ))

        # 2. Llamar al render_3d de cada subárea (Area)
        for sub in self.subareas:
            if hasattr(sub, 'render_3d'):
                sub.render_3d(fig=fig)

        # 3. Configuración final del Layout
        fig.update_layout(
            title=f"Vista 3D: {self.description}",
            scene=dict(
                aspectmode='data',
                xaxis_title='X (m)', yaxis_title='Y (m)', zaxis_title='Z (m)',
                camera=dict(eye=dict(x=1.2, y=-1.2, z=1.2))
            ),
            margin=dict(l=0, r=0, b=0, t=50),
            showlegend=True
        )
        return fig