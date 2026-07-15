import os, math

def save_render_image(fig, filename="render.png", folder="renders", tipo="3d"):
    """
    Guarda un Figure de Plotly como imagen PNG.
    """

    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, tipo + "_" + filename)
    
    if tipo == "3d":
        # --- PARÁMETROS INTUITIVOS ---
        angulo_grados = 60  # Ángulo de rotación en Z (por defecto Plotly usa 45)
        distancia = 3     # Controla el zoom. Mayor número = MENOS zoom (más lejos)
        altura_z = 1.4      # Qué tan arriba está la cámara mirando hacia abajo

        # Convertimos el ángulo a radianes para las funciones trigonométricas
        angulo_rad = math.radians(angulo_grados)

        # Calculamos las posiciones X e Y exactas usando seno y coseno
        nuevo_x = distancia * math.cos(angulo_rad)
        nuevo_y = distancia * math.sin(angulo_rad)

        # Aplicamos los cambios a tu figura
        fig.update_layout(
            scene_camera=dict(
                eye=dict(
                    x=nuevo_x,
                    y=nuevo_y,
                    z=altura_z
                )
            )
        )

    fig.write_image(
        path,
        format="png",
        width=1920,
        height=1080,
        scale=2
    )

    return path

