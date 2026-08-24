def determinar_posicion_puerta(
    pabellon_polygon, centro_layout, nombre_pabellon, eje_principal_division
):
    """
    Determina si la puerta debe estar en el lado 'top' o 'bottom' para que mire hacia el patio central.
    La lógica asume que los pabellones son más largos que anchos (verticales) y que la función
    create_structure los rotará 90 grados para trabajar. En esa rotación, el lado derecho (+X)
    se convierte en el lado superior (+Y, 'top'), y el izquierdo (-X) en el inferior (-Y, 'bottom').
    """
    centro_pabellon = pabellon_polygon.centroid

    if eje_principal_division == "x":
        # Pabellones a izquierda/derecha del centro.
        # Si el pabellón está a la izquierda del centro, su puerta debe estar en su lado derecho.
        # Lado derecho (+X) se convierte en 'top'.
        if centro_pabellon.x < centro_layout.x:
            return "top"
        # Si el pabellón está a la derecha del centro, su puerta debe estar en su lado izquierdo.
        # Lado izquierdo (-X) se convierte en 'bottom'.
        else:
            return "bottom"
    else:  # 'y'
        # Pabellones arriba/abajo del centro.
        # Si el pabellón está abajo del centro, su puerta debe estar en su lado superior.
        # Lado superior (+Y) se convierte en 'top'.
        if centro_pabellon.y < centro_layout.y:
            return "top"
        # Si el pabellón está arriba del centro, su puerta debe estar en su lado inferior.
        # Lado inferior (-Y) se convierte en 'bottom'.
        else:
            return "bottom"
