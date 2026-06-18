def optimizar_ejes_columnas(ejes, largo_max=8.0, umbral_proximidad=4.0, grosor_col = 0.3):
    """
    Evalúa ejes cercanos y los unifica, verificando que no se exceda
    el largo máximo de 8m entre los ejes resultantes.
    """
    if not ejes:
        return []

    ejes_optimizados = [ejes[0]] # Mantener el punto 0.0

    i = 1
    while i < len(ejes):
        punto_actual = ejes[i]
        punto_anterior = ejes_optimizados[-1]
        distancia = punto_actual - punto_anterior

        # Si hay un punto muy cerca del anterior (umbral personalizable, ej. < 2m)
        if i < len(ejes) - 1:
            punto_siguiente = ejes[i+1]
            distancia_al_siguiente = punto_siguiente - punto_actual

            # Si el punto actual está "apretado" entre dos
            if (punto_actual - punto_anterior) < umbral_proximidad:
                # Intentamos saltar este punto y ver si el siguiente cumple la regla de los 8m
                if (punto_siguiente - punto_anterior) <= largo_max:
                    # El punto actual se elimina porque el siguiente sigue respetando los 8m
                    pass
                else:
                    # Si al quitarlo excedemos los 8m, tenemos que dejarlo o promediarlo
                    ejes_optimizados.append(round(punto_actual, 3))
            else:
                ejes_optimizados.append(round(punto_actual, 3))
        else:
            # Es el último punto (44.5)
            ejes_optimizados.append(round(punto_actual, 3))

        i += 1
    ejes_optimizados[-1] -= grosor_col

    return sorted(list(set(ejes_optimizados)))

# Tus ejes actuales
# ejes_sucios = [0.0, 6.25, 6.562, 12.5, 13.125, 19.688, 20.5, 26.25, 28.5, 30.812, 35.375, 36.5, 39.938, 44.5]

# ejes_limpios = optimizar_ejes_columnas(ejes = ejes_sucios, grosor_col= 0.3)

# print(f"Ejes originales: {len(ejes_sucios)}")
# print(f"Ejes optimizados: {len(ejes_limpios)}")
# print(f"Nuevas coordenadas: {ejes_limpios}")

# # Verificación de luces (distancias)
# luces = [round(ejes_limpios[i] - ejes_limpios[i-1], 3) for i in range(1, len(ejes_limpios))]
# print(f"Luces resultantes: {luces}")
# print(f"¿Alguna luz supera los 8m?: {'SÍ' if any(l > 8 for l in luces) else 'NO'}")
