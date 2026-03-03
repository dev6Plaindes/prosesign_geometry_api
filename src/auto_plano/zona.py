from shapely import unary_union
from shapely.geometry import Polygon
from shapely.affinity import rotate, scale, translate
import uuid
from typing import Literal
from typing import Callable

TipoZona = Literal["zona", "area", "ambiente",""]

class Zona:
    def __init__(self, geometria, porcentaje=None, nivel=1, nombre= "", tipo : TipoZona = "", piso=1, grosor_muro = 0.0
):
        self.id = str(uuid.uuid4())[:8]
        self.geometria = geometria
        self.porcentaje = porcentaje
        self.nivel = nivel
        self.subzonas = []
        self.elementos = []
        self.nombre = nombre
        self.tipo = tipo # zona | area | ambiente | ""
        self.area_m2 = geometria.area
        self.piso = piso
        self._layout_aplicado = False
        minx, miny, maxx, maxy = geometria.bounds
        self.ancho = maxx - minx
        self.alto = maxy - miny
        self.grosor_muro = 0.0

    def obtener_area_util(self):
      if self.grosor_muro <= 0:
          return self.geometria

      interior = self.geometria.buffer(-self.grosor_muro)

      if interior.is_empty:
          raise ValueError("El grosor del muro es demasiado grande.")

      return interior

    def obtener_muros(self):
      if self.grosor_muro <= 0:
          return None

      interior = self.obtener_area_util()
      muros = self.geometria.difference(interior)

      return muros



    def inicializar_pisos(self):
      if not self.subzonas:
          piso1 = Zona.clonar_zona(self)
          piso1.piso = 1
          piso1.subzonas = []
          self.subzonas = [piso1]

    def obtener_area(self):
        return self.geometria.area

    def escalar(self, factor):
        self.geometria = scale(
            self.geometria,
            xfact=factor,
            yfact=factor,
            origin="centroid"
        )

    def centrar_subzonas(self):
        if not self.subzonas:
            return

        # --- Centro de la zona padre ---
        cx_padre, cy_padre = self.geometria.centroid.coords[0]

        # --- Unión de subzonas ---
        union = unary_union([z.geometria for z in self.subzonas])
        cx_hijo, cy_hijo = union.centroid.coords[0]

        dx = cx_padre - cx_hijo
        dy = cy_padre - cy_hijo

        # --- Mover todas las subzonas ---
        for z in self.subzonas:
            z.geometria = translate(z.geometria, dx, dy)

    def centrar_ambientes(self, piso: int = None):
      """
      Centra todos los subzonas de tipo 'ambiente' dentro de esta zona,
      recursivamente. Si se indica 'piso', solo afecta ese piso.
      """
      if not self.subzonas:
          return

      # Filtrar subzonas que estén en el piso indicado (si se pasa)
      subzonas_filtradas = [
          z for z in self.subzonas
          if piso is None or z.piso == piso
      ]

      # Filtrar solo ambientes directos
      ambientes = [z for z in subzonas_filtradas if z.tipo == "ambiente"]
      if ambientes:
          cx_padre, cy_padre = self.geometria.centroid.coords[0]
          union = unary_union([a.geometria for a in ambientes])
          cx_hijo, cy_hijo = union.centroid.coords[0]
          dx = cx_padre - cx_hijo
          dy = cy_padre - cy_hijo
          for a in ambientes:
              a.geometria = translate(a.geometria, dx, dy)

      # Recursividad: centrar dentro de subzonas de tipo 'zona'
      for sub in subzonas_filtradas:
          if sub.tipo == "zona":
            sub.centrar_ambientes(piso=piso)


    def agregar_elemento(self, elemento):
        self.elementos.append(elemento)

    def dividir(self, valores, orientacion="horizontal"):
      """
      valores:
        - porcentajes  [0.2, "auto", 0.3]
        - metros       [20, "auto", 15]
      """

      minx, miny, maxx, maxy = self.geometria.bounds
      ancho = maxx - minx
      alto = maxy - miny

      total = ancho if orientacion == "horizontal" else alto
      usar_porcentaje = all(v == "auto" or v <= 1 for v in valores)

      # --- fijos y autos ---
      fijos = [v for v in valores if v != "auto"]
      autos = valores.count("auto")

      if usar_porcentaje:
          usado = sum(fijos) * total
      else:
          usado = sum(fijos)

      restante = total - usado

      if restante < 0:
          raise ValueError("Las divisiones exceden el tamaño disponible")

      auto_valor = restante / autos if autos else 0

      self.subzonas = []
      cursor = minx if orientacion == "horizontal" else miny

      for v in valores:
          tamaño = (
              v * total if usar_porcentaje else v
          ) if v != "auto" else auto_valor

          if orientacion == "horizontal":
              geom = Polygon([
                  (cursor, miny),
                  (cursor + tamaño, miny),
                  (cursor + tamaño, maxy),
                  (cursor, maxy)
              ])
              cursor += tamaño
          else:
              geom = Polygon([
                  (minx, cursor),
                  (maxx, cursor),
                  (maxx, cursor + tamaño),
                  (minx, cursor + tamaño)
              ])
              cursor += tamaño

          self.subzonas.append(
              Zona(geom, porcentaje=None, nivel=self.nivel + 1)
          )

      return self.subzonas

    @staticmethod
    def clonar_zona(zona):
      return Zona(
          geometria=Polygon(zona.geometria.exterior.coords),
          porcentaje=zona.porcentaje,
          nivel=zona.nivel,
          nombre=zona.nombre,
          tipo=zona.tipo,
          piso=zona.piso
      )
    @staticmethod
    def crear_nuevo_piso(zona):
      return Zona(
          geometria=Polygon(zona.geometria.exterior.coords),
          porcentaje=zona.porcentaje,
          nivel=zona.nivel,
          nombre=zona.nombre,
          tipo=zona.tipo,
          piso=zona.piso + 1
      )

    def insertar_auto(self, zona, autoPiso=True):
      self.inicializar_pisos()

      # 1️⃣ Intentar insertar en pisos existentes
      for piso in self.subzonas:
          if piso.insertar_zona(zona):
              return piso

      # 2️⃣ Si no cabe y autoPiso está desactivado → devolver la zona no insertada
      if not autoPiso:
          return zona

      # 3️⃣ Crear nuevo piso automáticamente
      if not self.subzonas:
          raise RuntimeError("No existen pisos base para clonar")

      nuevo_piso = Zona.crear_nuevo_piso(self.subzonas[-1])
      nuevo_piso.subzonas = []

      if not nuevo_piso.insertar_zona(zona):
          raise RuntimeError("No entra ni en piso vacío")

      self.subzonas.append(nuevo_piso)
      return nuevo_piso

    def insertar_zona(self, zona, modo="auto", posicion=None, margen=0.0, gap=0.0, autoPiso=True):
      """
      Inserta una zona dentro de esta zona contenedora.

      Args:
          zona: Instancia de Zona a insertar (se clona internamente)
          modo: "auto", "horizontal", "vertical"
          posicion: tupla (x, y) para inserción manual (esquina inferior izquierda)
          margen: distancia mínima desde los bordes de la zona contenedora (metros)
          gap: separación mínima entre subzonas vecinas (metros)
          autoPiso: Si es True, asigna el piso del padre y lo añade a subzonas.
                    Si es False, solo retorna el elemento posicionado.
      """
      minx, miny, maxx, maxy = self.geometria.bounds

      # Siempre trabajamos con una copia
      zona = Zona.clonar_zona(zona)

      # Obtenemos dimensiones actuales de la zona a insertar
      zx1, zy1, zx2, zy2 = zona.geometria.bounds
      ancho_z = zx2 - zx1
      alto_z  = zy2 - zy1

      # Rotación automática en modo horizontal si es más alto que ancho
      if modo == "horizontal":
          if ancho_z < alto_z:
              zona.geometria = rotate(zona.geometria, 90, origin='center')
              zx1, zy1, zx2, zy2 = zona.geometria.bounds
              ancho_z = zx2 - zx1
              alto_z  = zy2 - zy1

      def posicion_horizontal():
          x = minx + margen
          y = miny + margen
          for sub in self.subzonas:
              bx1, by1, bx2, by2 = sub.geometria.bounds
              x = max(x, bx2 + gap)
          if x + ancho_z > maxx - margen:
              return None
          return x, y

      def posicion_vertical():
          x = minx + margen
          y = miny + margen
          for sub in self.subzonas:
              bx1, by1, bx2, by2 = sub.geometria.bounds
              y = max(y, by2 + gap)
          if y + alto_z > maxy - margen:
              return None
          return x, y

      # 1. Cálculo de coordenadas
      if posicion is not None:
          x, y = posicion
      elif modo == "auto":
          pos = posicion_horizontal()
          if pos is None:
              pos = posicion_vertical()
          if pos is None:
              print("No hay espacio disponible (ni horizontal ni vertical)")
              return False
          x, y = pos
      elif modo == "horizontal":
          pos = posicion_horizontal()
          if pos is None:
              print("No hay espacio horizontal disponible")
              return False
          x, y = pos
      elif modo == "vertical":
          pos = posicion_vertical()
          if pos is None:
              print("No hay espacio vertical disponible")
              return False
          x, y = pos
      else:
          print(f"Modo no reconocido: {modo}")
          return False

      # 2. Trasladamos la geometría al lugar calculado
      dx = x - zx1
      dy = y - zy1
      zona.geometria = translate(zona.geometria, dx, dy)

      # 3. Lógica de inserción o retorno independiente
      zona.nivel = self.nivel + 1

      if autoPiso:
          zona.piso = self.piso
          self.subzonas.append(zona)

      return zona

    def obtener_medidas_recursivas(self, path=""):
      """
      Retorna medidas y ubicación de esta zona y todas sus subzonas
      """
      minx, miny, maxx, maxy = self.geometria.bounds
      ancho = maxx - minx
      alto = maxy - miny
      area = self.geometria.area
      centro = self.geometria.centroid

      nombre_actual = self.nombre or "SIN_NOMBRE"
      path_actual = f"{path}/{nombre_actual}" if path else nombre_actual

      resultado = [{
          "nombre": nombre_actual,
          "nivel": self.nivel,
          "path": path_actual,

          # 📐 Medidas
          "ancho_m": round(ancho, 2),
          "alto_m": round(alto, 2),
          "area_m2": round(area, 2),

          # 📍 Ubicación
          "minx": round(minx, 2),
          "miny": round(miny, 2),
          "maxx": round(maxx, 2),
          "maxy": round(maxy, 2),
          "centro_x": round(centro.x, 2),
          "centro_y": round(centro.y, 2),
      }]

      for sub in self.subzonas:
          resultado.extend(
              sub.obtener_medidas_recursivas(path_actual)
          )

      return resultado

    def obtener_geometrias_recursivas(self, path=""):
      """
      Retorna la geometría EXACTA de esta zona y todas sus subzonas
      """
      nombre_actual = self.nombre or "SIN_NOMBRE"
      path_actual = f"{path}/{nombre_actual}" if path else nombre_actual

      resultado = [{
          "id": self.id,              # 🔑 CLAVE ÚNICA
          "nombre": nombre_actual,
          "nivel": self.nivel,
          "path": path_actual,
          "area_m2" : self.area_m2,
          "tipo" : self.tipo,
          "piso" : self.piso,
          "coords": [
              (round(x, 3), round(y, 3))
              for x, y in self.geometria.exterior.coords
          ]
      }]

      for sub in self.subzonas:
          resultado.extend(
              sub.obtener_geometrias_recursivas(path_actual)
          )

      return resultado
    def centrar_nucleo(self, subzonas_nucleo):
      """
      subzonas_nucleo: lista de Zona que irán al centro
      """
      if not subzonas_nucleo:
          return

      cx_padre, cy_padre = self.geometria.centroid.coords[0]

      union = unary_union([z.geometria for z in subzonas_nucleo])
      cx_nucleo, cy_nucleo = union.centroid.coords[0]

      dx = cx_padre - cx_nucleo
      dy = cy_padre - cy_nucleo

      for z in subzonas_nucleo:
          z.geometria = translate(z.geometria, dx, dy)

    def puede_colocar(self, nueva_geo, subzonas, margen=0.0):

      for z in subzonas:

          if margen == 0:
              if nueva_geo.intersects(z.geometria):
                  return False
          else:
              if nueva_geo.buffer(margen).intersects(z.geometria):
                  return False

      return True

    def establecer_reglas(self, anclaje="superior", alineacion="inicio", margen=0.2, orden=1):
      self.config_reglas = {
          "anclaje": anclaje,
          "alineacion": alineacion,
          "margen": margen,
          "orden": orden
      }

    def aplicar_layout(self, layout_fn: Callable, **kwargs):
      """
      Aplica una función de layout a esta zona.
      La función recibe (zona, **kwargs)
      """
      layout_fn(self, **kwargs)
      self._layout_aplicado = True
      return self

    def insertar_layout(self, zona, margen=0.0):
        """
        Inserta una zona SOLO si ya fue posicionada por un layout.
        No mueve la geometría.
        """

        if not getattr(zona, "_layout_aplicado", False):
            raise ValueError(
                "La zona no tiene layout aplicado. "
                "Use aplicar_layout() antes de insertar."
            )

        # Validar colisiones
        if not self.puede_colocar(zona.geometria, self.subzonas, margen):
            return False

        zona.nivel = self.nivel + 1
        zona.piso = self.piso
        self.subzonas.append(zona)
        return zona

    def obtener_area_libre(self):
        """
        Calcula el área libre real dentro de la zona
        restando la unión geométrica de todas las subzonas.
        """

        if not self.subzonas:
            return self.geometria.area

        union_subzonas = unary_union([z.geometria for z in self.subzonas])

        area_ocupada = union_subzonas.area
        area_total = self.geometria.area

        area_libre = area_total - area_ocupada

        return round(area_libre, 3)

    def obtener_ocupacion_interior(self):
        """
        Retorna el ancho y alto realmente ocupados por las subzonas
        dentro de esta zona (en metros si tu modelo está en metros).
        """

        if not self.subzonas:
            return {
                "ancho_ocupado_m": 0,
                "alto_ocupado_m": 0,
                "area_ocupada_m2": 0
            }

        # Unimos todas las subzonas
        union = unary_union([z.geometria for z in self.subzonas])

        minx, miny, maxx, maxy = union.bounds

        ancho_ocupado = maxx - minx
        alto_ocupado = maxy - miny
        area_ocupada = union.area

        return {
            "ancho_ocupado_m": round(ancho_ocupado, 3),
            "alto_ocupado_m": round(alto_ocupado, 3),
            "area_ocupada_m2": round(area_ocupada, 3)
        }

    def obtener_ocupacion_horizontal(self):
        """
        Retorna la longitud REAL ocupada en el eje X (metros).
        No usa bounding global, sino unión real de intervalos.
        """

        if not self.subzonas:
            return 0.0

        intervalos = []

        for z in self.subzonas:
            minx, _, maxx, _ = z.geometria.bounds
            intervalos.append((minx, maxx))

        # Ordenar por inicio
        intervalos.sort()

        # Unir intervalos
        unidos = []
        inicio, fin = intervalos[0]

        for i in range(1, len(intervalos)):
            actual_inicio, actual_fin = intervalos[i]

            if actual_inicio <= fin:  # se superponen
                fin = max(fin, actual_fin)
            else:
                unidos.append((inicio, fin))
                inicio, fin = actual_inicio, actual_fin

        unidos.append((inicio, fin))

        # Sumar longitudes reales
        total = sum(f - i for i, f in unidos)

        return round(total, 3)

    def obtener_ocupacion_vertical(self, piso=None):
        """
        Retorna la longitud REAL ocupada en el eje Y (metros)
        por las subzonas internas de cada piso.
        """

        if not self.subzonas:
            return 0.0

        intervalos = []

        for z in self.subzonas:

            # Si este nivel contiene pisos
            if piso is not None and z.piso != piso:
                continue

            # 🔥 Aquí bajamos un nivel (ambientes dentro del piso)
            for sub in z.subzonas:
                _, miny, _, maxy = sub.geometria.bounds
                intervalos.append((miny, maxy))

        if not intervalos:
            return 0.0

        intervalos.sort()

        unidos = []
        inicio, fin = intervalos[0]

        for i in range(1, len(intervalos)):
            actual_inicio, actual_fin = intervalos[i]

            if actual_inicio <= fin:
                fin = max(fin, actual_fin)
            else:
                unidos.append((inicio, fin))
                inicio, fin = actual_inicio, actual_fin

        unidos.append((inicio, fin))

        total = sum(f - i for i, f in unidos)

        return round(total, 3)


    def aplicar_borde_interior(self, borde: float):
      """
      Reduce la geometría hacia adentro como un border interno.
      borde: metros a reducir.
      """

      if borde <= 0:
          return

      nueva_geo = self.geometria.buffer(-borde)

      if nueva_geo.is_empty:
          raise ValueError("El borde es demasiado grande, la zona desaparece.")

      self.geometria = nueva_geo

      # Actualizar medidas
      minx, miny, maxx, maxy = self.geometria.bounds
      self.ancho = maxx - minx
      self.alto = maxy - miny
      self.area_m2 = self.geometria.area


    def obtener_altura_total_subzonas(self):
      return sum(subzona.alto for subzona in self.subzonas)

    def colocar_alrededor(self, nucleo, alrededor, margen=0.5):

      if not alrededor:
          return

      if not isinstance(nucleo, list):
          nucleo = [nucleo]

      # Bounding del núcleo
      minx = min(z.geometria.bounds[0] for z in nucleo)
      miny = min(z.geometria.bounds[1] for z in nucleo)
      maxx = max(z.geometria.bounds[2] for z in nucleo)
      maxy = max(z.geometria.bounds[3] for z in nucleo)

      # Ordenar por tamaño (opcional pero recomendable)
      alrededor.sort(key=lambda z: z.geometria.area, reverse=True)

      # cursores de cada lado
      derecha_y = miny
      izquierda_y = miny
      arriba_x = minx
      abajo_x = minx

      lado = 0

      for z in alrededor:

          zx1, zy1, zx2, zy2 = z.geometria.bounds
          ancho = zx2 - zx1
          alto = zy2 - zy1

          # --- DERECHA ---
          if lado == 0:
              x = maxx + margen
              y = derecha_y
              derecha_y += alto + margen

          # --- ABAJO ---
          elif lado == 1:
              x = abajo_x
              y = miny - alto - margen
              abajo_x += ancho + margen

          # --- IZQUIERDA ---
          elif lado == 2:
              x = minx - ancho - margen
              y = izquierda_y
              izquierda_y += alto + margen

          # --- ARRIBA ---
          else:
              x = arriba_x
              y = maxy + margen
              arriba_x += ancho + margen

          dx = x - zx1
          dy = y - zy1
          z.geometria = translate(z.geometria, dx, dy)

          lado = (lado + 1) % 4

