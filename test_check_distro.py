import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from bim.utils.logic import largos_for_piso_and_ambiente

test_amb = [
    {'Ambientes': 'Aulas Primaria', 'Metros_cuadrados': 60, 'Cantidad': 8, 'Unitario': 60,
     'Ancho': 7.5, 'Largo': 8.0, 'Tipo': 'Fijo', 'Pabellon': 'Izquierda', 'Piso_de_preferencia': '1 y 2'},
    {'Ambientes': 'Escalera Prim', 'Metros_cuadrados': 8.64, 'Cantidad': 1, 'Unitario': 8.64,
     'Ancho': 7.5, 'Largo': 2.5, 'Tipo': 'Fijo', 'Pabellon': 'Izquierda', 'Piso_de_preferencia': '1 y 2'},
]
res = largos_for_piso_and_ambiente(test_amb, 65.0, name_pabellon='test')
for i, nivel in enumerate(res):
    print(f'Nivel {i+1}:')
    for item in nivel:
        print(f'  ambiente="{item["ambiente"]}", largo={item["largo"]}')
has_esc = any('Escalera' in it['ambiente'] for niv in res for it in niv)
print(f'Contiene Escalera: {has_esc}')