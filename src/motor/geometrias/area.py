import pandas as pd
from shapely import Polygon
import plotly.graph_objects as go

from src.motor.geometrias.aula import Aula
from src.motor.geometrias.escalera import EscalerasCompleta
from src.motor.geometrias.losa import Losa
from src.motor.geometrias.pasadizo import Pasadizo


class Area:
  def __init__(self, ancho, largo, x= 0, y = 0, pisos=1, description = "Area"):
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
    self.escaleras = []

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

    for escalera in self.escaleras:
        if hasattr(escalera, "get_data"):
            dataframes.append(escalera.get_data())

    # 🔗 Unir todo
    return pd.concat(dataframes, ignore_index=True)

  def obtener_resumen_pisos(self):
    pisos = sorted(set(aula.piso for aula in self.aulas if hasattr(aula, 'piso')))

    return [
        {
            "piso": piso,
            "ancho_total": self.sumar_anchos_aulas_por_piso(piso),
            "largo_total": self.sumar_largos_aulas_por_piso(piso)
        }
        for piso in pisos
    ]

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
            losa._actualizar_geometrias()

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
                if hasattr(muro, "_actualizar_geometrias"):
                    muro._actualizar_geometrias()

        if hasattr(aula, "techo") and aula.techo:
            aula.techo.x += offset_x
            aula.techo.y += offset_y

            if hasattr(aula.techo, "geometria"):
                aula.techo.geometria = Polygon([
                    (aula.techo.x, aula.techo.y),
                    (aula.techo.x + aula.techo.ancho, aula.techo.y),
                    (aula.techo.x + aula.techo.ancho, aula.techo.y + aula.techo.largo),
                    (aula.techo.x, aula.techo.y + aula.techo.largo)
                ])

            if hasattr(aula.techo, "_actualizar_geometrias"):
                aula.techo._actualizar_geometrias()

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

                if hasattr(col, "_actualizar_geometrias"):
                    col._actualizar_geometrias()

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


  def pasadizo(self, ancho, largo, piso=1, description="pasadizo", lado="E"):
    pasadizo_piso = [a for a in self.pasadizos if a.piso == piso]

    if not pasadizo_piso:
        abs_x, abs_y = self.x, self.y
    else:
        ultima = pasadizo_piso[-1]
        abs_x = ultima.x + ultima.ancho
        abs_y = ultima.y

        if abs_x + ancho > self.x + self.ancho:
            abs_x = self.x
            abs_y = ultima.y + ultima.largo

    if abs_y + largo > self.y + self.largo:
        piso += 1
        abs_x, abs_y = self.x, self.y
    print(f"insertando pasadizo en piso {piso}")
    nueva = Pasadizo(ancho, largo, abs_x, abs_y, piso = piso, description =description, lado=lado)

    self.pasadizos.append(nueva)
    return nueva

  def pasadizos_mult(self, ancho, largo, pisos=None, description="pasadizo", lado="E", info_pisos=[]):
    """
    Crea pasadizos en múltiples pisos automáticamente.

    pisos: lista de pisos, ejemplo [1,2,3]
    Si es None, usa self.pisos
    """

    if pisos is None:
        pisos = self.pisos  # usa los pisos del área

    pasadizos_creados = []

    for piso in range(1,pisos + 1):
        print(f"Creando pasadizo en piso {piso}")
        # reutilizamos tu lógica existente
        self.pasadizo(ancho, info_pisos[piso - 1]["largo_total"], piso, f"{description}_{piso}", lado=lado)

        pasadizos_creados.append(self.pasadizos[-1])

    return pasadizos_creados

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

  def bano(self, ancho, largo, piso=1, description="baño", lado="right"):
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
      nueva.ventana_porcentaje("left", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    elif lado=="left":
      nueva.puerta("left")
      nueva.ventana_porcentaje("right", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    elif lado=="top":
      nueva.puerta("bottom")
      nueva.ventana_porcentaje("top", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    elif lado=="bottom":
      nueva.puerta("top")
      nueva.ventana_porcentaje("bottom", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    return nueva

  # def escalera(self, ancho, largo, piso=1, lado="left"):
  #   """
  #   Agrega una escalera al área
  #   """
  #   aulas_piso = [a for a in self.aulas if a.piso == piso]

  #   # Coordenadas iniciales
  #   if not aulas_piso:
  #       abs_x, abs_y = self.x, self.y
  #   else:
  #       # Colocar al lado derecho de la última aula del mismo piso
  #       ultima = aulas_piso[-1]
  #       abs_x = ultima.x + ultima.ancho
  #       abs_y = ultima.y

  #       # Si se sale del límite del área, mover a la siguiente fila dentro del mismo piso
  #       if abs_x + ancho > self.x + self.ancho:
  #           abs_x = self.x
  #           abs_y = ultima.y + ultima.largo

  #   if abs_y + largo > self.y + self.largo:
  #       # Subir al siguiente piso
  #       piso += 1
  #       abs_x, abs_y = self.x, self.y

  #   escalera = Escalera(ancho, largo, abs_x, abs_y, piso)
  #   self.escaleras.append(escalera)
  #   return escalera


  def aula(self, ancho, largo, piso=1, description="aula", lado="right"):
    """
    Agrega un aula al área, colocándola al lado derecho de la última aula agregada en el mismo piso.
    Si no hay espacio en el piso actual, sube automáticamente al siguiente piso.
    """
    colocada = False

    while not colocada:
        aulas_piso = [a for a in self.aulas if a.piso == piso]

        if not aulas_piso:
            # Caso 1: Piso vacío
            abs_x, abs_y = self.x, self.y
        else:
            # Caso 2: Intentar después de la última aula
            ultima = aulas_piso[-1]
            abs_x = ultima.x + ultima.ancho
            abs_y = ultima.y

            # Si se sale del ancho, saltar a la siguiente fila en el mismo piso
            if abs_x + ancho > self.x + self.ancho:
                abs_x = self.x
                abs_y = ultima.y + ultima.largo 
                # Importante: Aquí 'ultima.largo' asume que todas las aulas 
                # de la fila anterior tenían el mismo largo.

        # Verificar si cabe en el largo del terreno (en este piso)
        if abs_y + largo <= self.y + self.largo:
            nueva = Aula(ancho, largo, abs_x, abs_y, piso, description)
            self.aulas.append(nueva)
            self._registrar_piso(piso)
            colocada = True
        else:
            # Si ya recorrimos las filas y no cabe, pasamos al siguiente nivel
            piso += 1

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

  def get_aulas_por_piso(self, numero_piso):
    """
    Retorna una lista con los objetos Aula que pertenecen al piso especificado.
    """
    # Filtramos las aulas comparando el atributo 'piso' con el parámetro recibido
    return [aula for aula in self.aulas if getattr(aula, 'piso', None) == numero_piso]

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

    for escalera in self.escaleras:
        escalera.draw(fig)

    fig.update_layout(
        title=f"{self.description}",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=700,
        height=500,
        showlegend=True
    )

    fig.show()

  def render_3d(self, fig=None):
        """
        Dibuja el suelo del área y delega el dibujo 3D a sus componentes.
        """
        import plotly.graph_objects as go
        if fig is None: fig = go.Figure()

        # 1. Suelo del Área (opcional por cada área para contexto)
        x_a, y_a = self.geometria.exterior.xy
        # Usamos el piso mínimo definido en self.pisos (asumiendo que es una lista)
        z_base = (min(self.pisos) - 1) * 3.0

        fig.add_trace(go.Mesh3d(
            x=list(x_a), y=list(y_a), z=[z_base] * len(x_a),
            opacity=0.15, color="lightgray", name=f"Nivel {self.description}",
            showlegend=True
        ))

        # 2. Renderizar Aulas (Cada aula dibuja sus muros/ventanas/puertas)
        for aula in self.aulas:
            if hasattr(aula, 'render_3d'):
                aula.render_3d(fig)

        # 3. RECURSIVIDAD: Renderizar Subáreas (Áreas dentro de áreas)
        for subarea in self.subareas:
            if hasattr(subarea, 'render_3d'):
                subarea.render_3d(fig)

        # 4. Renderizar Pasadizos y Losas
        for pas in self.pasadizos:
            if hasattr(pas, 'render_3d'):
                pas.render_3d(fig)

        for losa in self.losas:
            if hasattr(losa, 'render_3d'):
                losa.render_3d(fig)

        for escalera in self.escaleras:
            if hasattr(escalera, 'render_3d'):
                escalera.render_3d(fig)

        fig.update_layout(
            scene=dict(
                aspectmode='manual', # Cambiar a manual para control total
                aspectratio=dict(x=1, y=4, z=0.5), # Si el largo(y) es 4 veces el ancho(x)
                xaxis_title='ANCHO (X)',
                yaxis_title='LARGO (Y)',
                zaxis_title='ALTO (Z)'
            )
        )
        return fig

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

  def draw_3d(self, fig = None):
        """
        Renderiza todas las aulas contenidas en el área en una sola vista 3D.
        """
        if fig is None:
          fig = go.Figure()

        # 1. Dibujar el suelo del Área (Opcional, ayuda a dar contexto)
        x_area, y_area = self.geometria.exterior.xy
        # El suelo se dibuja en el nivel Z más bajo de las aulas (usualmente 0 si es piso 1)
        z_suelo = 0

        fig.add_trace(go.Mesh3d(
            x=list(x_area),
            y=list(y_area),
            z=[z_suelo] * len(x_area),
            opacity=0.2,
            color="lightgray",
            name=f"Suelo {self.description}",
            showlegend=True
        ))

        # 2. Renderizar cada Aula
        # Cada aula ya tiene su lógica para renderizar muros, ventanas, puertas y columnas
        for aula in self.aulas:
            # Usamos el método render_3d del aula, pasando nuestra figura 'fig'
            if hasattr(aula, 'render_3d'):
                # Si el aula tiene un método que acepta 'fig', lo usamos directamente
                # Si tu aula.render_3d actual crea su propia figura,
                # asegúrate de tener una versión que acepte la fig externa:
                aula.render_3d(fig)
            else:
                # Si no existe, podemos iterar manualmente sus listas
                for muro in aula.muros:
                    muro.render_3d(fig)
                for col in aula.columnas:
                    col.render_3d(fig)
                for puerta in aula.puertas:
                    puerta.render_3d(fig)
        for pasadiso in self.pasadizos:
            pasadiso.render_3d(fig)

        # 3. Configuración del Layout Maestro
        fig.update_layout(
            title=f"Vista 3D Completa: {self.description}",
            scene=dict(
                aspectmode='data', # Mantiene las proporciones reales (CRÍTICO)
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)',
                # Ajustamos la cámara para ver el área desde una perspectiva isométrica
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)
                )
            ),
            margin=dict(l=0, r=0, b=0, t=50),
            showlegend=True
        )

        return fig

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

  def alinear_objeto(self, objeto, lado="top"):
    """
    Mueve un objeto (Aula, Losa, Pasadizo, etc.) a los extremos del área.
    Lados permitidos: 'top', 'bottom', 'left', 'right' o combinaciones (ej: 'top, left').
    """
    lado = lado.lower()
    nueva_x = objeto.x
    nueva_y = objeto.y

    # --- Cálculo de nuevas coordenadas ---
    if "left" in lado:
        nueva_x = self.x
    elif "right" in lado:
        nueva_x = self.x + self.ancho - objeto.ancho

    if "bottom" in lado:
        nueva_y = self.y
    elif "top" in lado:
        nueva_y = self.y + self.largo - objeto.largo

    # --- Aplicar desplazamiento ---
    offset_x = nueva_x - objeto.x
    offset_y = nueva_y - objeto.y

    self._desplazar_elemento(objeto, offset_x, offset_y)

  def escalera(self, direccion="norte"):
    """Crea una escalera en el área."""
    escalera_n = EscalerasCompleta(x=self.x, y=self.y, direccion=direccion)
    escalera_n.generate_escaleras()
    self.escaleras.append(escalera_n)
    return escalera_n

  def _registrar_piso(self, piso):
    """Agrega el piso si no existe"""
    self.pisos = piso

  def _desplazar_elemento(self, obj, dx, dy):
    """Método auxiliar para mover un objeto y sus componentes internos."""
    from shapely.geometry import Polygon

    obj.x += dx
    obj.y += dy

    # Actualizar Polígono principal
    if hasattr(obj, "geometria"):
        obj.geometria = Polygon([
            (obj.x, obj.y),
            (obj.x + obj.ancho, obj.y),
            (obj.x + obj.ancho, obj.y + obj.largo),
            (obj.x, obj.y + obj.largo)
        ])

    # Actualizar sub-elementos recursivamente (Muros, Columnas, Puertas)
    for atributo in ["muros", "columnas", "puertas", "ventanas"]:
        if hasattr(obj, atributo):
            lista_elementos = getattr(obj, atributo)
            for item in lista_elementos:
                item.x += dx
                item.y += dy
                if hasattr(item, "_actualizar_geometrias"):
                    item._actualizar_geometrias()
                elif hasattr(item, "_actualizar_geometria"):
                    item._actualizar_geometria()
