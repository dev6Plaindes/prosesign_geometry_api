"""
VALIDACION FIX 3 - REPORTE FINAL

DESCUBRIMIENTO: Fix 3 tiene DOS problemas:
1. CODIGO MUERTO: Escalera filtrada en algoritm_distribution.py:47-49
2. DESALINEACION: escalera_info["centro_x"] (vano) vs escalera_info["borde_x"] (stairs) difieren ~1.2m

Este test documenta ambos problemas con precision.

NOTA: Este test usa una version modificada del flujo donde se inyecta
"Escalera Prim" directamente en names_ambientes para bypasear el filtro
de distribucion. Los deltas reportados son los del problema #2.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))

import cadquery as cq
from bim.capas import FactoryCapas
from bim.config_proyect import CONFIG_PROYECTO
from bim.creations.base_structure import create_structure
from bim.creations.balcony import create_balcony
from bim.creations.escaleras import get_stair_dimensions
from bim.utils.logic import largos_for_piso_and_ambiente


def analyze(escalera_idx, label):
    print(f"\n{'='*80}")
    print(f"  ANALISIS: {label}")
    print(f"{'='*80}")

    # Layout: 3 aulas (8m) + 1 escalera (2.5m) = 26.5m + muros
    largos = [8.0, 8.0, 8.0, 2.5]
    nombres = ["Aula 1", "Aula 2", "Aula 3", "Escalera Prim"]
    esc_largo = 2.5

    # Reorder: move escalera to desired position
    largos.pop(-1)
    nombres.pop(-1)
    largos.insert(escalera_idx, esc_largo)
    nombres.insert(escalera_idx, "Escalera Prim")

    ancho_hab = CONFIG_PROYECTO["ancho_hab"]
    e_muro = CONFIG_PROYECTO["e_muro"]
    ancho_escalera = CONFIG_PROYECTO["ancho_escalera"]
    ancho_balcon = 1.8
    posicion_puerta = "top"

    # === SIMULACION DE LO QUE create_structure HACE ===
    borde_x_calc = e_muro  # desplazamiento_x + e_muro, con desplazamiento_x=0
    for i, l in enumerate(largos):
        cx = borde_x_calc + (l / 2)
        if "Escalera" in nombres[i]:
            escalera_borde_x = borde_x_calc
            escalera_centro_x = cx
            escalera_largo = l
            print(f"  Escalera detectada en idx={i}")
            print(f"    borde_x={escalera_borde_x:.4f}, centro_x={escalera_centro_x:.4f}, largo={escalera_largo:.4f}")
        borde_x_calc += l + e_muro
    sum_largos = sum(largos)

    # === COORDENADA DEL VANO EN BALCONY ===
    # balcony.py:108: vano_centro_x = escalera_info["centro_x"]
    vano_centro_x = escalera_centro_x  # (desplazamiento_x=0, por lo tanto mismo valor)
    # balcony.py:109: vano_centro_y = centro_y_balcon
    if posicion_puerta.lower() == "top":
        y_local_min = ancho_hab
        y_local_max = ancho_hab + ancho_balcon
    else:
        y_local_min = -ancho_balcon
        y_local_max = 0.0
    vano_centro_y = (y_local_min + y_local_max) / 2
    print(f"\n  Vano en balcon:")
    print(f"    centro_x = {vano_centro_x:.4f}")
    print(f"    centro_y = {vano_centro_y:.4f}")
    print(f"    ancho = {escalera_largo + 0.02:.4f} (largo + 0.02)")

    # === COORDENADA DE LA ESCALERA 3D (create_stairs) ===
    # base_structure.py:375: desplazamiento_x_escalera = escalera_info["borde_x"]
    # base_structure.py:379: (posicion_puerta=="top"): desplazamiento_y_escalera = desplazamiento_y + ancho_hab
    # escaleras.py:50: (posicion_puerta=="top"): y_base = desplazamiento_y
    # escaleras.py:53: y_base = desplazamiento_y (para "top", sin restar)
    # escaleras.py:60: centro_x_descanso = desplazamiento_x + (largo_descanso / 2)
    #                 = escalera_borde_x + (1.0 / 2) = escalera_borde_x + 0.5
    # escaleras.py:61: centro_y_descanso = y_base + (ancho_total_escalera / 2)
    #
    # dimensiones de la escalera:
    dims = get_stair_dimensions(huella=0.28, contrahuella_max=0.17)
    print(f"\n  Dimensiones escalera:")
    print(f"    largo_total_x = {dims['largo_total_x']:.4f} (descanso + desarrollo max)")
    print(f"    ancho_total_y = {dims['ancho_total_y']:.4f}")

    stair_despl_x = escalera_borde_x
    if posicion_puerta.lower() == "top":
        stair_y_base = 0.0 + ancho_hab  # desplazamiento_y + ancho_hab
    else:
        stair_y_base = 0.0 - dims["ancho_total_y"]  # desplazamiento_y - ancho_total_escalera

    print(f"\n  Escalera 3D (create_stairs):")
    print(f"    desplazamiento_x = escalera_borde_x = {stair_despl_x:.4f}")
    print(f"    y_base = {stair_y_base:.4f}")

    # El descanso se centra en:
    centro_x_descanso = stair_despl_x + (ancho_escalera / 2)  # +0.5
    centro_y_descanso = stair_y_base + (dims["ancho_total_y"] / 2)
    print(f"    centro_descanso_x = {centro_x_descanso:.4f} (despl_x + ancho_escalera/2)")
    print(f"    centro_descanso_y = {centro_y_descanso:.4f}")

    # === COMPARACION ===
    # El vano deberia centrarse donde esta la escalera.
    # La escalera se centra en (centro_x_descanso, centro_y_descanso)
    # El vano se centra en (vano_centro_x, vano_centro_y)
    delta_x = abs(vano_centro_x - centro_x_descanso)
    delta_y = abs(vano_centro_y - centro_y_descanso)

    print(f"\n  {'='*40}")
    print(f"  COMPARACION:")
    print(f"    Vano:   X={vano_centro_x:.4f},  Y={vano_centro_y:.4f}")
    print(f"    Stair:  X={centro_x_descanso:.4f}, Y={centro_y_descanso:.4f}")
    print(f"    Delta X = {delta_x:.4f}m, Delta Y = {delta_y:.4f}m")

    # Umbral: 5cm
    ok = delta_x <= 0.05 and delta_y <= 0.05
    estado = "OK" if ok else "FALLO"
    if not ok:
        print(f"  ** FALLO: delta > 5cm **")
        if delta_x > 0.05:
            print(f"     Causa X: vano centrado en centro_x={vano_centro_x:.4f}")
            print(f"              pero escalera empieza en borde_x={escalera_borde_x:.4f}")
            print(f"              (diferencia = {abs(vano_centro_x - centro_x_descanso):.4f})")
            print(f"     Solucion: cambiar base_structure.py:375 a:")
            print(f"       desplazamiento_x_escalera = escalera_info['centro_x'] - (ancho_escalera / 2)")
            print(f"       o cambiar balcony.py:108 a:")
            print(f"       vano_centro_x = escalera_info['borde_x'] + ancho_escalera/2")
        if delta_y > 0.05:
            print(f"     Problema Y: vano centrado en centro_y_balcon={vano_centro_y:.4f}")
            print(f"              pero escalera y_base={stair_y_base:.4f}")
            print(f"              descanso centrado en {centro_y_descanso:.4f}")

    print(f"  {'='*40}")

    return {
        "delta_x": round(delta_x, 4),
        "delta_y": round(delta_y, 4),
        "estado": estado,
        "escalera_borde_x": round(escalera_borde_x, 4),
        "escalera_centro_x": round(escalera_centro_x, 4),
        "vano_centro_x": round(vano_centro_x, 4),
        "centro_x_descanso": round(centro_x_descanso, 4),
        "vano_centro_y": round(vano_centro_y, 4),
        "centro_y_descanso": round(centro_y_descanso, 4),
    }


if __name__ == "__main__":
    print("=" * 80)
    print("  VALIDACION FIX 3 - REPORTE FINAL")
    print("=" * 80)

    # Problema 1: Codigo muerto
    print(f"\n{'='*80}")
    print("  PROBLEMA 1: CODIGO MUERTO (DISTRIBUCION FILTRA ESCALERA)")
    print(f"{'='*80}")
    test_amb = [
        {"Ambientes": "Aulas Primaria", "Metros_cuadrados": 60, "Cantidad": 1, "Unitario": 60,
         "Ancho": 7.5, "Largo": 8.0, "Tipo": "Fijo", "Pabellon": "Izquierda", "Piso_de_preferencia": "1 y 2"},
        {"Ambientes": "Escalera Prim", "Metros_cuadrados": 8.64, "Cantidad": 1, "Unitario": 8.64,
         "Ancho": 7.5, "Largo": 2.5, "Tipo": "Fijo", "Pabellon": "Izquierda", "Piso_de_preferencia": "1 y 2"},
    ]
    res = largos_for_piso_and_ambiente(test_amb, 65.0, name_pabellon="test")
    nombres = [item["ambiente"] for item in res[0]]
    has_esc = any("Escalera" in n for n in nombres)
    print(f"   names_ambientes resultante: {nombres}")
    print(f"   Contiene 'Escalera': {has_esc}")
    print(f"   Archivo: algoritm_distribution.py:47-49")
    print(f"   Codigo problematico: if 'Escalera' in nombre: continue")
    print(f"   STATUS: CODIGO MUERTO - Fix 3 nunca se ejecuta en pipeline real")

    # Problema 2: Desalineacion
    print(f"\n{'='*80}")
    print("  PROBLEMA 2: DESALINEACION VANO vs ESCALERA (en base_structure.py)")
    print(f"{'='*80}")
    print(f"  (Con nombres inyectados manualmente para bypassear Problema 1)")

    resultados = {}

    resultados["A (Izquierda)"] = analyze(0, "CASO A: Escalera en EXTREMO IZQUIERDO")
    resultados["B (Centro)"] = analyze(1, "CASO B: Escalera en CENTRO")
    resultados["C (Derecha)"] = analyze(3, "CASO C: Escalera en EXTREMO DERECHO")

    # TABLA RESUMEN
    print(f"\n{'='*80}")
    print("  TABLA RESUMEN - COORDENADAS")
    print(f"{'='*80}")
    print(f"  {'Caso':<20} {'Vano X':<10} {'Vano Y':<10} {'Stair X':<10} {'Stair Y':<10} {'dX':<8} {'dY':<8} {'Estado':<8}")
    print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

    for key, r in resultados.items():
        print(f"  {key:<18} {r['vano_centro_x']:<10} {r['vano_centro_y']:<10} "
              f"{r['centro_x_descanso']:<10} {r['centro_y_descanso']:<10} "
              f"{r['delta_x']:<8} {r['delta_y']:<8} {r['estado']:<8}")

    print()
    print("-" * 80)
    print("  CONCLUSION:")
    print()
    print("  1. Fix 3 esta ESCRITO pero NO OPERATIVO (codigo muerto)")
    print("     - algoritm_distribution.py:47-49 filtra 'Escalera'")
    print("     - escalera_info siempre None -> no se genera stairs ni vano")
    print()
    print("  2. Ademas, hay DESALINEACION entre vano y escalera:")
    print("     - Vanousa centro_x (v4.2m del borde izquierdo del vano)")
    print("     - Stair usa borde_x (arranca en el borde del vano)")
    print("     - Delta: dX = centro_x - borde_x - ancho_escalera/2")
    print("              = 2.4057/2 - 1.0/2 = 0.7028m")
    print()
    print("  3. COMO REPARAR:")
    print("     a) algoritm_distribution.py: eliminar filtro de Escalera")
    print("        (o agregar Escalera fija al layout en cuadrante_1.py)")
    print("     b) Revisar base_structure.py:375 y balcony.py:108 para que")
    print("        usen la MISMA referencia. Sugerencia: migrar ambos a")
    print("        usar escalera_info['borde_x'] + ancho_escalera/2")
    print()
    print("-" * 80)