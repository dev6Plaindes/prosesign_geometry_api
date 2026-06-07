import pandas as pd
from shapely import Polygon
import plotly.graph_objects as go

from src.motor.geometrias.puerta_completa import PuertaCompleta
from src.motor.geometrias.techo_2_aguas import TechoDosAguas
from src.motor.geometrias.escalera import EscalerasCompleta
from src.motor.utils.ejes_unificados import calcular_ejes_unificados
from src.motor.utils.optimizar_ejes import optimizar_ejes_columnas
# from src.auto_plano.render import Aula, Losa, Muro, Pasadizo
from src.motor.geometrias.techo import Techo
from src.motor.geometrias.aula import Aula
from src.motor.geometrias.losa import Losa
from src.motor.geometrias.muro import Muro
from src.motor.geometrias.pasadizo import Pasadizo


# MEDIDAS VENTANA

medida_inf_vent = 0.6
medida_vent = 1.4
medida_sup_vent = 0.7
margin_m = 0.2

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
    self.columns = []
    self.muros = []
    self.vigas = []
    self.puntos_lat = {}
    self.h_piso= 2.75
    self.h_techo = 0.25
    self.grosor_col = 0.3
    self.grosor_muro = 0.15
    self.eje_auto = "y"
    self.ancho_viga = self.grosor_col
    self.h_viga = 0.6 # implementar
    self.h_viga_balcon = 0.5 # implementar
    self.ancho_balcon = 1.8
    self.h_peralte = 0.5
    self.margen_ventana = 0.4
    self.margen_puerta= 0.3
    self.ancho_puerta = 1.0
    self.num_puntos = []
    self.ancho_pasadizo = 1.8
    
  def centrar_elementos(self):
      """
      Centra todos los muros contenidos en self.muros
      respecto al área padre usando self.x y self.y como referencia.
      
      El conjunto completo de muros se mueve como bloque.
      """

      if not self.muros:
          return

      # =========================================
      # Bounding box actual de los muros
      # =========================================
      min_x = min(m.x for m in self.muros)
      max_x = max(m.x + m.ancho for m in self.muros)

      min_y = min(m.y for m in self.muros)
      max_y = max(m.y + m.largo for m in self.muros)

      ancho_actual = max_x - min_x
      largo_actual = max_y - min_y

      # =========================================
      # Centro objetivo (padre)
      # =========================================
      centro_padre_x = self.x + (self.ancho / 2)
      centro_padre_y = self.y + (self.largo / 2)

      # =========================================
      # Centro actual del grupo de muros
      # =========================================
      centro_muros_x = min_x + (ancho_actual / 2)
      centro_muros_y = min_y + (largo_actual / 2)

      # =========================================
      # Offset necesario
      # =========================================
      offset_x = centro_padre_x - centro_muros_x
      offset_y = centro_padre_y - centro_muros_y

      # =========================================
      # Aplicar desplazamiento
      # =========================================
      for muro in self.muros:
          muro.x += offset_x
          muro.y += offset_y
          muro._actualizar_geometrias()

  def create_techos(self, orientacion="E", tipo_techo = "zona_1"):
        if not self.aulas:
            return

        # 1. Identificar qué niveles existen (sin duplicados)
        niveles_unicos = sorted(list(set(aula.piso for aula in self.aulas)))

        for nivel in niveles_unicos:
            # 2. Filtrar aulas que pertenecen a este piso específico
            aulas_del_nivel = [a for a in self.aulas if a.piso == nivel]

            # 3. Obtener los límites (bounds) solo de las aulas de este nivel
            bounds_nivel = [a.geometria.bounds for a in aulas_del_nivel]

            min_x = min(b[0] for b in bounds_nivel)
            min_y = min(b[1] for b in bounds_nivel)
            max_x = max(b[2] for b in bounds_nivel)
            max_y = max(b[3] for b in bounds_nivel)

            width = max_x - min_x
            height = max_y - min_y

            # 4. Calcular Z para este nivel
            # Si el piso es 0, el techo va a 2.7. Si es 1, a 5.4, etc.
            altura_piso = 2.7
            z_techo = (nivel) * altura_piso

            # 5. Crear el objeto techo para este nivel
            
            base_x_orientacion = min_x
            
            base_width = width
            
            
            
            if orientacion == "E":
                base_x_orientacion = min_x
                
                if tipo_techo == "zona_3":
                  base_width = width + 1
                  base_x_orientacion = min_x
                
                if tipo_techo in ["zona_4", "zona_5", "zona_6"]:
                  base_width = width + 1 + 1.8
                  base_x_orientacion = min_x - 1.8
                  
                if tipo_techo in ["zona_7", "zona_8", "zona_9" ]:
                  base_width = width + 1.5 + 1.8
                  base_x_orientacion = min_x - 1.8
                
            # elif orientacion == "O":
            #     base_x_orientacion = min_x - 1
            else:
                base_x_orientacion = min_x - 1
                
                if tipo_techo == "zona_3":
                  base_width = width + 1
                  base_x_orientacion = min_x - 1
                
                if tipo_techo in ["zona_4", "zona_5", "zona_6"]:
                  base_width = width + 1 + 1.8
                  base_x_orientacion = min_x - 1
                  
                if tipo_techo in ["zona_7", "zona_8", "zona_9" ]:
                  base_width = width + 1.5 + 1.8
                  base_x_orientacion = min_x - 1.5
                  
            
                

            if nivel>1:
                
                if nivel ==  niveles_unicos[-1]:  # Si es el último nivel, le damos pendiente aunque haya varios niveles
                    techo = Muro(
                        ancho=self.ancho_balcon,
                        largo=height,
                        x=max_x + width, 
                        y=min_y,
                        z=z_techo + 0.25,
                        altura=self.h_viga_balcon
                    )
                    
                    techo.tipo = "techo"
                    techo.piso= nivel
                    techo._actualizar_geometrias()
                if tipo_techo == "zona_1": # OK
                    techo = Techo(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_techo + 0.25,
                        pendiente=0.4,
                        orientacion=orientacion
                        )
                    
                elif tipo_techo == "zona_2": # OK
                    techo = Techo(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_techo + 0.25,
                        pendiente=0.8,
                        orientacion=orientacion
                        )
                    
                elif tipo_techo == "zona_3":  # OK
                    techo = TechoDosAguas(
                        ancho=base_width,
                        largo=height,
                        x=base_x_orientacion,
                        y=min_y,
                        z=z_techo + 0.25,
                        altura_cumbrera=1.35,
                        orientacion=orientacion
                    )
                  
                
                elif tipo_techo in ["zona_4", "zona_5", "zona_6" ]: # OK
                    techo = TechoDosAguas(
                        ancho=base_width,
                        largo=height,
                        x=base_x_orientacion,
                        y=min_y,
                        z=z_techo + 0.25,
                        altura_cumbrera=2.72,
                        orientacion=orientacion
                    )
                  
                elif tipo_techo in ["zona_7", "zona_8", "zona_9" ]: # OK
                    print("Techo dos aguas para zona 7, 8 o 9")
                    techo = TechoDosAguas(
                        ancho=base_width,
                        largo=height,
                        x=base_x_orientacion,
                        y=min_y,
                        z=z_techo + 0.25,
                        altura_cumbrera=5.09,
                        orientacion=orientacion
                    ) 
                
                else:
                    techo = TechoDosAguas(
                        ancho=width,
                        largo=height,
                        x=base_x_orientacion,
                        y=min_y,
                        z=z_techo + 0.25,
                        altura_cumbrera=1.35,
                        orientacion=orientacion
                    )

            else:
                z_base = z_techo
                
                if len(niveles_unicos) > 1:
                    techo = Techo(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_base,
                        pendiente=0,
                        orientacion=orientacion
                        )
                    continue
                    
                if tipo_techo == "zona_1":
                    techo = Techo(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_base,
                        pendiente=0.4,
                        orientacion=orientacion
                        )
                
                elif tipo_techo == "zona_2":
                    techo = Techo(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_base,
                        pendiente=0.8,
                        orientacion=orientacion
                        )
                    
                elif tipo_techo == "zona_3":
                    techo = TechoDosAguas(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_base,
                        altura_cumbrera=1.35,
                        orientacion=orientacion
                    )
                else:
                    techo = TechoDosAguas(
                        ancho=width,
                        largo=height,
                        x=min_x,
                        y=min_y,
                        z=z_base,
                        altura_cumbrera=1.35,
                        orientacion=orientacion
                    )

            techo.tipo = "techo"
            techo.piso= nivel
            techo._actualizar_geometrias()

            # Guardar en la lista de muros o una lista específica de techos
            self.muros.append(techo)

  def create_puntos(self, offset_y = 0, largo = 0, offset_x= 0):
    return [offset_y, offset_y +  largo, offset_x]

  def obtener_puntos(self):
    puntos_columns = []
    puntos_puertas = []

    acumulado = 0.0

    puntos_puertas = []
    puntos_ventanas = []
    puntos_columnas = []
    ancho_ambiente= 7.5

    acumulado = 0.0
    for aula in self.aulas:
        limite_pos = aula.largo

        pos_col = self.create_puntos(round(acumulado, 4), self.grosor_col)
        pos_col_2 = self.create_puntos(round(acumulado, 4), self.grosor_col, ancho_ambiente)
        pos_puerta = self.create_puntos(round(acumulado, 4) + self.grosor_col + self.margen_puerta, self.ancho_puerta)
        pos_ventana = [pos_puerta[1] + self.margen_ventana, acumulado + limite_pos -self.margen_ventana]

        puntos_ventanas.append(pos_ventana)
        puntos_columnas.extend([pos_col, pos_col_2])
        puntos_puertas.append(pos_puerta)
        # puntos_esquinas.append(round(acumulado, 4))

        acumulado += limite_pos

    pos_col_end = self.create_puntos(round(acumulado, 4), self.grosor_col)
    pos_col_end_2 = self.create_puntos(round(acumulado, 4), self.grosor_col, ancho_ambiente)
    puntos_columnas.extend([pos_col_end,pos_col_end_2 ])

    altura_columna = (self.h_piso + self.h_techo) * self.pisos

    for puntos in puntos_columnas:
      columna = Muro(ancho=self.grosor_col, largo=self.grosor_col,x=puntos[2], y=puntos[0], altura=altura_columna)
      columna.tipo="columna"
      columna._actualizar_geometrias()
      self.columns.append(columna)

  def create_vigas_laterales(self, eje="y", pos_balcon="R"):
        # print("vigas", self.pisos)
        if self.pisos > 1:
          for nivel in range(self.pisos):
            # Calculamos la altura actual (Z) para este nivel
            # Nota: Si las vigas van sobre la columna, podrías necesitar (nivel + 1)
            z_actual = self.h_piso * (nivel + 1)

            for punto in self.num_puntos:
                if pos_balcon == "R":
                  viga = Muro(
                      x=self.x + self.grosor_col,
                      y=self.y + punto,
                      z=z_actual, # Ahora la Z es dinámica por piso
                      ancho=(self.ancho + self.ancho_balcon),
                      largo=self.grosor_col,
                      altura=self.h_peralte
                  )
                else:
                  viga = Muro(
                      x=self.x - self.grosor_col - self.ancho_balcon,
                      y=self.y + punto,
                      z=z_actual, # Ahora la Z es dinámica por piso
                      ancho=(self.ancho + self.ancho_balcon),
                      largo=self.grosor_col,
                      altura=self.h_peralte
                  )
                viga.tipo = "viga"
                viga._actualizar_geometrias()
                self.vigas.append(viga)

        return self.vigas

  def create_vigas_frontales(self, eje="y", orientacion_balcon="R"):
    ancho_m = self.ancho_viga
    medidas_m_largos = []

    if eje == "y":
        for i in range(1, len(self.num_puntos)):
            # Calculamos el tramo entre columnas
            inicio = self.num_puntos[i-1] + self.grosor_col
            fin = self.num_puntos[i]
            medidas_m_largos.append((inicio, fin))

    for medida in medidas_m_largos:
        largo_viga = medida[1] - medida[0]
        y_pos = self.y + medida[0]

        # Cambiamos a range(self.pisos) para empezar desde el nivel 0
        for i in range(self.pisos):
            # Usamos la misma lógica Z que en las laterales
            z_actual = self.h_piso * (i + 1)

            # Viga frontal izquierda
            viga_n = Muro(
                z=z_actual, x=self.x, y=y_pos,
                ancho=ancho_m, largo=largo_viga, altura=self.grosor_col
            )
            # Viga frontal derecha
            viga_n2 = Muro(
                z=z_actual, x=self.x + self.ancho - ancho_m, y=y_pos,
                ancho=ancho_m, largo=largo_viga, altura=self.grosor_col
            )

            for viga in [viga_n, viga_n2]:
                viga.tipo = "viga"
                viga.piso = i + 1
                # ¡CUIDADO AQUÍ! Si move_to_piso ya suma altura,
                # podrías estar moviéndolas dos veces.
                # Prueba comentando la siguiente línea si siguen sin verse:
                viga._actualizar_geometrias()

            self.vigas.extend([viga_n, viga_n2])

  def move_to_piso(self, element, piso=1):
        altura = self.h_piso + self.h_techo + element.z
        element.z = altura * (piso - 1)
        # self.build()

  def create_muros_laterales(self, eje="y"):
        medida_muro = self.grosor_muro
        ultimo_piso = max(self.puntos_lat.keys())

        for piso, puntos in self.puntos_lat.items():
          self.puntos_lat[piso][-1] -= (self.grosor_muro / 2)
          for i in puntos:
              muro_n = Muro(x=self.x + self.grosor_muro, y= i, ancho=self.ancho - (self.grosor_muro * 2), largo=self.grosor_muro, altura=self.h_piso)
              self.move_to_piso(muro_n, piso)
              muro_n._actualizar_geometrias()
              muro_n.piso = piso
              self.muros.append(muro_n)

  def create_muros_frontales_x(self, pos_balcon="R"):
    medida_muro = self.grosor_muro
    medidas_muros_largos = []

    # 🔥 Se asume que num_puntos ya está calculado para eje X
    for i in range(1, len(self.num_puntos)):
        medidas_muros_largos.append(
            (self.num_puntos[i - 1] + self.grosor_col, self.num_puntos[i])
        )

    for medida in medidas_muros_largos:
        for i in range(1, self.pisos + 1):

            largo_muro = medida[1] - medida[0]

            # =========================
            # 🔥 DIRECCIÓN EN EJE X
            # =========================
            if pos_balcon == "L":
                base_y = self.y
                muro_n = Muro(
                    x=self.x + medida[0],
                    y=self.y + self.ancho - medida_muro,
                    ancho=largo_muro,
                    largo=medida_muro,
                    altura=self.h_piso
                )
            else:  # "R"
                base_y = self.y + self.ancho - medida_muro
                muro_n = Muro(
                    x=self.x + medida[0],
                    y=self.y,
                    ancho=largo_muro,
                    largo=medida_muro,
                    altura=self.h_piso
                )

            acumulador_x = self.x

            muro_n2 = Muro(
                x=acumulador_x,
                y=base_y,
                ancho=0.3,
                largo=self.grosor_muro,
                altura=self.h_piso
            )

            acumulador_x += muro_n2.ancho

            puerta = Muro(
                x=acumulador_x,
                y=base_y,
                ancho=1,
                largo=self.grosor_muro,
                altura=self.h_piso
            )

            acumulador_x += puerta.ancho

            g_v = Muro(
                x=acumulador_x,
                y=base_y,
                ancho=self.margen_ventana,
                largo=self.grosor_muro,
                altura=self.h_piso
            )

            largo_ventana = (
                largo_muro
                - muro_n2.ancho
                - puerta.ancho
            )

            ventana = Muro(
                x=acumulador_x,
                y=base_y,
                ancho=largo_ventana,
                largo=self.grosor_muro,
                altura=self.h_piso
            )

            # 🔹 cortes verticales
            puerta = puerta.cortar_altura(
                z_inicio_corte=0.0,
                altura_corte=2.7
            )

            p_inf, vent, p_sup = ventana.segmentar_altura(
                medidas=[0.8, 1, 0.3]
            )
            vent.tipo="ventana"

            pedazos = [muro_n, muro_n2, g_v]
            pedazos.extend(puerta)
            # pedazos.extend([p_inf, vent, p_sup])

            for muro in pedazos:
                self.move_to_piso(muro, i)
                muro._actualizar_geometrias()
                muro.piso = i
                self.muros.append(muro)

#   def create_muros_frontales(self, eje="y", pos_balcon="R"):
#     medida_muro = self.grosor_muro
#     medidas_muros_largos = []

#     if eje == "y":
#         for i in range(1, len(self.num_puntos)):
#             medidas_muros_largos.append(
#                 (self.num_puntos[i - 1] + self.grosor_col, self.num_puntos[i])
#             )

#         for medida in medidas_muros_largos:
#             for i in range(1, self.pisos + 1):
#                 altura = self.h_piso + self.h_techo
#                 base_z = altura * (i - 1)
#                 largo_muro = medida[1] - medida[0]
#                 largo_ventana = largo_muro - (margin_m*2)
                
#                 if pos_balcon == "L":
#                     base_x = self.x
#                     muro_n = Muro(
#                         x=self.x + self.ancho - medida_muro,
#                         y=self.y + medida[0],
#                         z=base_z,
#                         ancho=medida_muro,
#                         largo=largo_muro,
#                         altura=self.h_piso
#                     )
                    
#                     m_s, m_ventana, m_e = muro_n.segmentar_horizontal(medidas=[margin_m, largo_ventana, margin_m])
#                     m_ventana.tipo = "ventana"
                    
#                 else:  # "R"
#                     base_x = self.x + self.ancho - medida_muro
#                     muro_n = Muro(
#                         x=self.x,
#                         y=self.y + medida[0],
#                         z=base_z,
#                         ancho=medida_muro,
#                         largo=largo_muro,
#                         altura=self.h_piso
#                     )
#                     m_s, m_ventana, m_e = muro_n.segmentar_horizontal(medidas=[margin_m, largo_ventana, margin_m])
                
#                 muros_n = [ m_s, m_e]

#                 # Cortar pezado del muro para las ventanas
#                 v_sup, ventana_i, v_inf = m_ventana.segmentar_altura(medidas=[medida_inf_vent, medida_vent, medida_sup_vent]) 
#                 ventana_i.tipo = "ventana"
                
#                 muros_n.extend([v_sup, ventana_i, v_inf])
#                 acumulador_y = self.y + medida[0]

#                 muro_n2 = Muro(
#                     x=base_x,
#                     y=acumulador_y,
#                     z=base_z,
#                     ancho=self.grosor_muro,
#                     largo=0.3,
#                     altura=self.h_piso
#                 )
                
#                 acumulador_y += muro_n2.largo

#                 puerta = PuertaCompleta(
#                     x=base_x,
#                     y=acumulador_y,
#                     z=base_z,
#                     ancho=self.grosor_muro,
#                     largo=1,
#                     altura=self.h_piso,
#                     piso=i,
#                     orientacion=pos_balcon,
#                 )
#                 self.muros.append(puerta.arco)

#                 acumulador_y += puerta.largo

#                 g_v = Muro(
#                     x=base_x,
#                     y=acumulador_y,
#                     z=base_z,
#                     ancho=self.grosor_muro,
#                     largo=self.margen_ventana,
#                     altura=self.h_piso
#                 )

#                 largo_ventana = (
#                     largo_muro
#                     - muro_n2.largo
#                     - puerta.largo
#                 )
                

#                 ventana = Muro(
#                     x=base_x,
#                     y=acumulador_y,
#                     z=base_z,
#                     ancho=self.grosor_muro,
#                     largo=largo_ventana,
#                     altura=self.h_piso
#                 )

#                 # 🔹 cortes verticales
#                 puerta, puerta_sup = puerta.segmentar_altura(
#                     medidas=[2.0, 0.3]
#                 )
#                 puerta.tipo = "puerta"

#                 p_inf, vent, p_sup = ventana.segmentar_altura(
#                     medidas=[medida_inf_vent, medida_vent, medida_sup_vent]
#                 )
#                 vent.tipo="ventana"

#                 pedazos = [muro_n2, g_v]
#                 pedazos.extend(muros_n)
#                 ventana_items = [p_inf, vent, p_sup]
#                 puerta_items = [puerta, puerta_sup]

#                 for muro in pedazos:
#                     self.move_to_piso(muro, i)
#                     # muro.tipo = "muro"
#                     # muro._actualizar_geometrias()
#                     muro.piso = i
#                     self.muros.append(muro)
                
#                 for v in ventana_items:
#                     v.piso = i
#                     # v._actualizar_geometrias()
#                     self.muros.append(v)
                    
#                 for p in puerta_items:
#                     p.piso = i
#                     # p._actualizar_geometrias()
#                     self.muros.append(p)

  def create_muros_frontales(self, eje="y", pos_balcon="R"):
    medida_muro = self.grosor_muro

    # Iteramos por piso y puntos reales de los ambientes tal como en los muros laterales
    for piso, puntos in self.puntos_lat.items():
        
        # Iteramos en pares de puntos para obtener el inicio y fin de cada ambiente
        for j in range(1, len(puntos)):
            inicio_ambiente = puntos[j - 1]
            fin_ambiente = puntos[j]
            
            # Altura y posición en Z para el piso actual
            altura_piso_total = self.h_piso + self.h_techo
            base_z = altura_piso_total * (piso - 1)
            
            # El largo disponible real de este ambiente
            largo_ambiente = fin_ambiente - inicio_ambiente
            
            # Definir la posición en X según el balcón
            if pos_balcon == "L":
                base_x = self.x
            else:  # "R"
                base_x = self.x + self.ancho - medida_muro

            # Nuestro acumulador Y arranca exactamente en el inicio del ambiente actual
            acumulador_y = inicio_ambiente

            # 1. Muro pequeño de tope inicial (0.3m) antes de la puerta
            muro_tope = Muro(
                x=base_x,
                y=acumulador_y,
                z=base_z,
                ancho=medida_muro,
                largo=0.3,
                altura=self.h_piso
            )
            acumulador_y += muro_tope.largo

            # 2. Creamos el objeto puerta (Largo estándar = 1.0m)
            puerta_obj = PuertaCompleta(
                x=base_x,
                y=acumulador_y,
                z=base_z,
                ancho=medida_muro,
                largo=1.0,
                altura=self.h_piso,
                piso=piso,
                orientacion=pos_balcon,
            )
            self.muros.append(puerta_obj.arco)
            acumulador_y += puerta_obj.largo

            # 3. Lo que sobra del ambiente se destina a la ventana
            largo_ventana = largo_ambiente - muro_tope.largo - puerta_obj.largo
            
            # Validación por si el ambiente es muy pequeño
            if largo_ventana < 0.5:
                largo_ventana = 0.5

            ventana_base = Muro(
                x=base_x,
                y=acumulador_y,
                z=base_z,
                ancho=medida_muro,
                largo=largo_ventana,
                altura=self.h_piso
            )

            # 4. Cortes verticales de la puerta (Puerta y dintel superior)
            puerta_corta, puerta_sup = puerta_obj.segmentar_altura(
                medidas=[2.0, 0.3]
            )
            puerta_corta.tipo = "puerta"

            # 5. Cortes verticales de la ventana (Alféizar, vidrio, dintel)
            p_inf, vent, p_sup = ventana_base.segmentar_altura(
                medidas=[medida_inf_vent, medida_vent, medida_sup_vent]
            )
            vent.tipo = "ventana"

            # 6. Agrupar y guardar componentes procesados en las listas globales
            muros_estructura = [muro_tope]
            ventanas_items = [p_inf, vent, p_sup]
            puertas_items = [puerta_corta, puerta_sup]

            # Procesar y mover muros de la estructura
            for muro in muros_estructura:
                self.move_to_piso(muro, piso)
                muro.piso = piso
                muro._actualizar_geometrias()
                self.muros.append(muro)
            
            # Procesar ventanas
            for v in ventanas_items:
                self.move_to_piso(v, piso)
                v.piso = piso
                v._actualizar_geometrias()
                self.muros.append(v)
                
            # Procesar puertas
            for p in puertas_items:
                self.move_to_piso(p, piso)
                p.piso = piso
                p._actualizar_geometrias()
                self.muros.append(p)

  def create_columns(self, eje="y", df_medidas= []):
        altura_columna = (self.h_piso + self.h_techo) * self.pisos
        if eje == "y":
            # self.num_puntos, _ = generar_lista_uniforme(self.largo, medida_columna=self.grosor_col)
            df_resumen, lista_ejes = calcular_ejes_unificados(df_medidas)
            # df_resumen, lista_ejes = calcular_ejes_unificados(df_medidas, self.grosor_col)
            ejes_limpios = optimizar_ejes_columnas(ejes = lista_ejes, grosor_col= 0.3)

            self.num_puntos = ejes_limpios

        for punto in self.num_puntos:
            col = Muro(x=self.x, y=self.y + punto, ancho=self.grosor_col, largo=self.grosor_col, altura= altura_columna)
            col_2 = Muro(x= self.x + self.ancho - self.grosor_col, y=self.y +punto, ancho=self.grosor_col, largo=self.grosor_col, altura=altura_columna)
            col.tipo="columna"
            col_2.tipo="columna"
            col._actualizar_geometrias()
            col_2._actualizar_geometrias()
            self.columns.append(col)
            self.columns.append(col_2)

        largo_pab = 0
        for aula in self.aulas:
          if aula.piso==1:
            largo_pab+=aula.largo

        largo_pab= largo_pab - self.grosor_col

        col_last_1 = Muro(x= self.x + self.ancho - self.grosor_col, y=self.y + largo_pab, ancho=self.grosor_col, largo=self.grosor_col, altura=altura_columna)
        col_last_2 = Muro(x=self.x, y=self.y + largo_pab, ancho=self.grosor_col, largo=self.grosor_col, altura= altura_columna)
        col_last_1.tipo="columna"
        col_last_2.tipo="columna"
        
        self.columns.append(col_last_1)
        self.columns.append(col_last_2)
        self.num_puntos.append(largo_pab)

        return self.columns

  def create_columns_from_aulas(self, pos="T", heigth=7.5):
    position_columns = []
    pos_y = self.y

    # 1. Recolectamos todos los inicios y el final de la última aula
    for aula in self.aulas:
        position_columns.append(aula.x)
        pos_y = aula.y

    # IMPORTANTE: Añadir el punto final de la última aula para cerrar el espacio
    if self.aulas:
        ultima_aula = self.aulas[-1]
        # Asumiendo que las aulas tienen un atributo 'ancho' o similar
        # Si no, puedes usar la lógica de posición final que manejes
        position_columns.append(ultima_aula.x + ultima_aula.ancho)

    if pos == "T":
        pos_y_t = pos_y + heigth - self.grosor_muro
        pos_y_b = pos_y
    else:
        pos_y_t = pos_y
        pos_y_b = pos_y + heigth - self.grosor_muro

    for i in range(len(position_columns)):
        pos_x = position_columns[i]

        # Definimos si hay un siguiente punto para calcular el largo del muro
        tiene_siguiente = i < len(position_columns) - 1

        if tiene_siguiente:
            largo_muro = position_columns[i + 1] - position_columns[i]
        else:
            largo_muro = 0

        # Elementos estructurales (Columnas)
        col = Muro(x=pos_x, y=pos_y, ancho=self.grosor_col, largo=self.grosor_col)
        column_2 = Muro(x=pos_x, y=pos_y_t - 0.15, ancho=self.grosor_col, largo=self.grosor_col)

        # Muro vertical divisorio
        muro_n_3 = Muro(x=pos_x, y=pos_y, ancho=self.grosor_muro, largo=heigth)
        self.muros.append(muro_n_3)

        # Solo generamos cerramientos (puertas/ventanas) si hay un tramo hacia adelante
        if tiene_siguiente:
            acumulador_x = pos_x + col.ancho
            col._actualizar_geometrias()
            column_2._actualizar_geometrias()

            # Muros de dintel y base
            muro_n = Muro(x=acumulador_x, y=pos_y_t, ancho=self.margen_puerta, largo=self.grosor_muro)
            muro_n_2 = Muro(x=acumulador_x, y=pos_y_b, ancho=largo_muro, largo=self.grosor_muro)

            acumulador_x += muro_n.ancho
            muro_n._actualizar_geometrias()

            # Puerta
            puerta_muro = PuertaCompleta(
                x=acumulador_x,
                y=pos_y_t,
                ancho=1,
                largo=self.grosor_muro,
                altura=self.h_piso,
                orientacion=pos,
                piso=1
            )
            self.muros.append(puerta_muro.arco)
            
            # PUERTA
            puerta, puerta_sup = puerta_muro.segmentar_altura(medidas=[2.0, 0.3])
            puerta.tipo = "puerta"
            
            acumulador_x += puerta_muro.ancho

            # Ventana
            g_v = Muro(
                x=acumulador_x,
                y=pos_y_t,
                ancho=self.margen_ventana,
                largo=self.grosor_muro,
                altura=self.h_piso
            )
            acumulador_x += g_v.ancho

            largo_ventana = (largo_muro - self.grosor_col - muro_n.ancho - puerta.ancho - g_v.ancho)

            if largo_ventana > 0:
                ventana = Muro(
                    x=acumulador_x,
                    y=pos_y_t,
                    ancho=largo_ventana,
                    largo=self.grosor_muro,
                    altura=self.h_piso
                )
                
                v_inf, ventana_i, v_sup = ventana.segmentar_altura(medidas=[medida_inf_vent, medida_vent, medida_sup_vent])
                ventana_i.tipo = "ventana"
                self.muros.extend([v_inf, ventana_i, v_sup])
                
                # ventana de los muros de la espalda
                largo_ventana = largo_muro - (margin_m*2)
                m_s, m_ventana, m_e = muro_n_2.segmentar_horizontal(medidas=[margin_m, largo_ventana, margin_m])
                
                self.muros.extend([m_s, m_e])
                
                v_inf_2, ventana_i_2, v_sup_2 = m_ventana.segmentar_altura(medidas=[medida_inf_vent, medida_vent, medida_sup_vent])
                
                ventana_i_2.tipo = "ventana"
                
                self.muros.extend([v_inf_2, ventana_i_2, v_sup_2])
            
            # Agregar a las listas
            self.muros.append(muro_n)
            # self.muros.append(muro_n_2)
            self.muros.extend([puerta, puerta_sup])
            self.muros.append(g_v)

        # Registro de columnas y puntos
        self.num_puntos.append(pos_x)
        self.columns.append(col)
        self.columns.append(column_2)

  def get_data(self):
        data = []

        # =====================================
        # 1. DATA DEL ÁREA ACTUAL
        # =====================================
        data_area = {
            "ancho": self.ancho,
            "largo": self.largo,
            "area": self.area,
            "pisos": self.pisos,
            "description": self.description,
            "geometria": self.geometria,
            "x": self.x,
            "y": self.y,
            "tipo": "area"
        }

        data.append(data_area)

        # =====================================
        # 2. AULAS
        # =====================================
        for aula in self.aulas:

            if hasattr(aula, "get_data"):

                aula_data = aula.get_data()

                # Mantener misma lógica concat
                if isinstance(aula_data, list):
                    data.extend(aula_data)
                else:
                    data.append(aula_data)

        # =====================================
        # 3. SUBÁREAS (RECURSIVO)
        # =====================================
        for subarea in self.subareas:

            if hasattr(subarea, "get_data"):

                sub_data = subarea.get_data()

                if isinstance(sub_data, list):
                    data.extend(sub_data)
                else:
                    data.append(sub_data)

        # =====================================
        # 4. PASADIZOS
        # =====================================
        for pas in self.pasadizos:

            if hasattr(pas, "get_data"):

                pas_data = pas.get_data()

                if isinstance(pas_data, list):
                    data.extend(pas_data)
                else:
                    data.append(pas_data)

        # =====================================
        # 5. LOSAS
        # =====================================
        for losa in self.losas:

            if hasattr(losa, "get_data"):

                losa_data = losa.get_data()

                if isinstance(losa_data, list):
                    data.extend(losa_data)
                else:
                    data.append(losa_data)

        # =====================================
        # 6. ESCALERAS
        # =====================================
        for escalera in self.escaleras:

            if hasattr(escalera, "get_data"):

                esc_data = escalera.get_data()

                if isinstance(esc_data, list):
                    data.extend(esc_data)
                else:
                    data.append(esc_data)

        # =====================================
        # 7. COLUMNAS
        # =====================================
        for column in self.columns:

            if hasattr(column, "get_data"):

                col_data = column.get_data()

                if isinstance(col_data, list):
                    data.extend(col_data)
                else:
                    data.append(col_data)

        # =====================================
        # 8. MUROS
        # =====================================
        for muro in self.muros:

            if hasattr(muro, "get_data"):

                muro_data = muro.get_data()

                if isinstance(muro_data, list):
                    data.extend(muro_data)
                else:
                    data.append(muro_data)

        # =====================================
        # 9. VIGAS
        # =====================================
        for viga in self.vigas:

            if hasattr(viga, "get_data"):

                viga_data = viga.get_data()

                if isinstance(viga_data, list):
                    data.extend(viga_data)
                else:
                    data.append(viga_data)

        # =====================================
        # MISMA LÓGICA DE CONCAT
        # =====================================
        return data

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
    nueva = Pasadizo(ancho, largo, abs_x, abs_y, piso = piso, description =description, lado=lado)

    self.pasadizos.append(nueva)
    return nueva

  def pasadizos_mult(self, ancho, largo, largo_balcon, pisos=None, description="pasadizo", lado="E", info_pisos=[]):
    """
    Crea pasadizos en múltiples pisos automáticamente.

    pisos: lista de pisos, ejemplo [1,2,3]
    Si es None, usa self.pisos
    """

    if pisos is None:
        pisos = self.pisos  # usa los pisos del área

    pasadizos_creados = []

    for piso in range(1,pisos + 1):
        # reutilizamos tu lógica existente
        if(piso==1):
          self.pasadizo(ancho =self.ancho_pasadizo, largo= largo,piso= piso,description= f"{description}_{piso}", lado=lado)
        else:
          if lado=="E":
            pas_new = self.pasadizo(ancho=ancho,largo=largo_balcon ,piso=piso , description=f"{description}_{piso}", lado=lado)
            pas_new.x -= ancho - self.ancho_pasadizo
            pas_new._actualizar_geometrias()
          else:
            self.pasadizo(ancho=self.ancho_pasadizo, largo=largo_balcon,piso=piso, description=f"{description}_{piso}", lado=lado)
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

  def insertar_losas(self, cantidad_losas, gap=0.2, piso=1, ancho_losa=15, largo_losa=28):
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
        # if y_actual + largo_losa > self.y + self.largo:
        #     break
        largo_losa = self.largo - 0.3
        if self.largo > 28:
            largo_losa = 28

        # ✅ Crear losa
        losa_i = Muro(ancho = ancho_losa,largo = largo_losa, x= x_actual, y= y_actual + 0.3, piso= piso, description= f"losa_{i+1}", altura=0.2)
        losa_i.tipo = "losa"
        self.muros.append(losa_i)
        losas_creadas.append(losa_i)

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

    if self.eje_auto == "y":
        offset = self.grosor_muro / 2
        self.puntos_lat[piso].append(nueva.y - offset)
        self.puntos_lat[piso].append(nueva.y + nueva.largo - offset)

    # if lado=="right":
    #   nueva.puerta("right")
    #   nueva.ventana_porcentaje("left", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    # elif lado=="left":
    #   nueva.puerta("left")
    #   nueva.ventana_porcentaje("right", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    # elif lado=="top":
    #   nueva.puerta("bottom")
    #   nueva.ventana_porcentaje("top", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    # elif lado=="bottom":
    #   nueva.puerta("top")
    #   nueva.ventana_porcentaje("bottom", cantidad= 1, gap=0.2, porcentaje=0.7, h_alfeizar=1.8, h_ventana=0.4)

    return nueva


  def aula(self, ancho, largo, piso=1, description="aula", lado="right"):
    """
    Agrega un aula al área, colocándola al lado derecho de la última aula agregada en el mismo piso.
    Si no hay espacio en el piso actual, sube automáticamente al siguiente piso.
    """
    colocada = False

    if piso not in self.puntos_lat:
        self.puntos_lat[piso] = []

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

    if self.eje_auto == "y":
        offset = self.grosor_muro / 2
        self.puntos_lat[piso].append(nueva.y - offset)
        self.puntos_lat[piso].append(nueva.y + nueva.largo - offset)

    aulas_mismo_piso = [a for a in self.aulas if a.piso == nueva.piso]
    if len(aulas_mismo_piso) > 1:
        tipo_apilamiento = self.tipo_apilamiento_penultimo_ultimo(piso=nueva.piso)
        if tipo_apilamiento == "vertical":
            self.unir_penultimo_y_ultimo(piso=nueva.piso)
            self.unir_penultima_y_ultima_columnas(piso=nueva.piso)
        elif tipo_apilamiento == "horizontal":
            self.unir_penultimo_y_ultimo_horizontal(piso=nueva.piso)
            self.unir_penultima_y_ultima_columnas_horizontal(piso=nueva.piso)

    # if lado=="right":
    #   nueva.puerta("right")
    #   nueva.ventana_porcentaje("right", cantidad= 1, gap=0.2, porcentaje=0.7)
    #   nueva.ventana_porcentaje("left", cantidad= 2, gap=0.5, porcentaje= 0.5)

    # elif lado=="left":
    #   nueva.puerta("left")
    #   nueva.ventana_porcentaje("left", cantidad= 1, gap=0.2, porcentaje=0.7)
    #   nueva.ventana_porcentaje("right", cantidad= 2, gap=0.5, porcentaje= 0.5)

    # elif lado=="top":
    #   nueva.puerta("bottom")
    #   nueva.ventana_porcentaje("bottom", cantidad= 1, gap=0.2, porcentaje=0.7)
    #   nueva.ventana_porcentaje("top", cantidad= 2, gap=0.5, porcentaje= 0.5)

    # elif lado=="bottom":
    #   nueva.puerta("top")
    #   nueva.ventana_porcentaje("top", cantidad= 1, gap=0.2, porcentaje=0.7)
    #   nueva.ventana_porcentaje("bottom", cantidad= 2, gap=0.5, porcentaje= 0.5)

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
                y=self.y,
                pisos=1
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
                y=y0,
                pisos=1
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

  def escalera(self, direccion="norte", pisos=2):
    """Crea escaleras entre pisos consecutivos con salto de altura 3m"""

    if pisos <= 1:
        return "pisos insuficientes"

    escaleras = []

    ALTURA_PISO = 2.7

    for i in range(1, pisos):
        z_inicio = (i - 1) * ALTURA_PISO
        z_fin = i * ALTURA_PISO

        escalera_n = EscalerasCompleta(
            x=self.x,
            y=self.y,
            z=z_inicio,
            direccion=direccion,
            piso_inicio=i
        )

        escalera_n.generate_escaleras()
        self.escaleras.append(escalera_n)
        escaleras.append(escalera_n)

    return escaleras


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

# area = Area(ancho = 10, largo = 25)

# pas, area_pab = area.areas_m(1.2, "auto")


# esc1 , pabellon, esc2 = area_pab.areas_m(2.4, "auto", 2.4, direccion="vertical")

# aula1 = pabellon.aula(ancho = 7, largo = 4, lado="left", piso=1)

# esc1.escalera(direccion="oeste", pisos=4)
# esc2.escalera(direccion="oeste", pisos=4)

# info_pisos = pabellon.obtener_resumen_pisos()

# for i in info_pisos:
#   i["largo_total"] = 25
#   print(i)

# pas.pasadizos_mult(ancho=2, largo =area_pab.largo, largo_balcon=area_pab.largo, pisos= pabellon.pisos, info_pisos = info_pisos)
# df = area.get_data()
# data_dict = df.to_dict(orient="records")

# # render = Render(data_dict, pisos=2)
# # render.render_3d
# import pandas as pd
# # pd.DataFrame(data_dict)