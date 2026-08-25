def agregar_banos(distribucion):
    # Si la lista viene anidada (ej. [[{...}, {...}]]), extraemos los elementos
    if distribucion and isinstance(distribucion[0], list):
        elementos = [item for sublista in distribucion for item in sublista]
        es_anidado = True
    else:
        elementos = list(distribucion)
        es_anidado = False

    # Identificar pisos únicos
    pisos_unicos = set(item['piso'] for item in elementos)
    
    # Agregar los baños a la lista de elementos
    for piso in pisos_unicos:
        # Tomamos el pabellón del primer elemento del mismo piso para ser consistentes
        pabellon_piso = next((item.get('pabellon', 'General') for item in elementos if item.get('piso') == piso), 'General')
        
        bano_hombre = {
            'ambiente': 'Baño de hombres',
            'largo': 2.0,
            'ancho': 7.5,
            'pabellon': pabellon_piso,
            'piso': piso,
            'polygon': None
        }
        
        bano_mujer = {
            'ambiente': 'Baño de mujeres',
            'largo': 2.1,
            'ancho': 7.5,
            'pabellon': pabellon_piso,
            'piso': piso,
            'polygon': None
        }
        
        elementos.extend([bano_hombre, bano_mujer])

    # Mantener el formato de salida según como entró (anidado o plano)
    return [elementos] if es_anidado else elementos

def agregar_banos_pabellon(data_pabellon, name_pabellon = ""):
    # Detectar si la lista viene anidada [[{...}]] o plana [{...}]
    if data_pabellon and isinstance(data_pabellon[0], list):
        elementos = [item for sublista in data_pabellon for item in sublista]
        es_anidado = True
    else:
        elementos = list(data_pabellon)
        es_anidado = False

    # Identificar pisos únicos en la estructura dada
    pisos_unicos = set(item['Piso'] for item in elementos)

    for piso in pisos_unicos:
        # Obtener datos de referencia del piso actual
        referencia = next((item for item in elementos if item.get('Piso') == piso), {})
        id_piso = referencia.get('ID_Piso', f'PISO_{piso}')
        largo_total = referencia.get('Largo_Total_Piso', None)

        bano_hombre = {
            'Piso': piso,
            'Ambiente': f'SSHH - Hombres {name_pabellon}',
            'Largo_Individual': 2.0,  # Asignar medida real si aplica
            'Ancho_Individual': 7.5,
            'Largo_Total_Piso': largo_total,
            'ID_Piso': id_piso
        }

        bano_mujer = {
            'Piso': piso,
            'Ambiente': f'SSHH - Mujeres {name_pabellon}',
            'Largo_Individual': 2.1,
            'Ancho_Individual': 7.5,
            'Largo_Total_Piso': largo_total,
            'ID_Piso': id_piso
        }

        elementos.extend([bano_hombre, bano_mujer])

    return [elementos] if es_anidado else elementos