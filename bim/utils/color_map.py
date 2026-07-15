# [DOCUMENTACIÓN] Mapa de colores centralizado para ambientes escolares.
# Este módulo es la única fuente de verdad para los colores de ambientes,
# usado por render_3d.py y render_2d.py para garantizar consistencia visual.
# [DOCUMENTACIÓN] Fix colores: Paleta actualizada a tonos pasteles suaves y coherentes
# con el diseño de Instituciones Educativas. Se eliminan colores neón/saturados.
import plotly.graph_objects as go


COLOR_MAP_AMBIENTES = {
    # Aulas y enseñanza → azul suave
    "Aula": {"fill": "rgba(180,215,240,0.65)", "line": "#4A90C4", "hex": "#B4D7F0"},
    # Biblioteca → verde salvia
    "Biblioteca": {"fill": "rgba(160,210,170,0.65)", "line": "#3A9055", "hex": "#A0D2AA"},
    # Innovación → lila suave
    "Innovacion": {"fill": "rgba(210,195,235,0.65)", "line": "#7B60B0", "hex": "#D2C3EB"},
    # Taller → amarillo ocre
    "Taller": {"fill": "rgba(240,215,140,0.65)", "line": "#C49A10", "hex": "#F0D78C"},
    # Laboratorio → rosa pálido
    "Laboratorio": {"fill": "rgba(240,180,185,0.65)", "line": "#C05560", "hex": "#F0B4B9"},
    # Tópico / Lactario → verde agua
    "Topico": {"fill": "rgba(170,230,215,0.65)", "line": "#1E8A80", "hex": "#AAE6D7"},
    "Lactario": {"fill": "rgba(170,230,215,0.65)", "line": "#1E8A80", "hex": "#AAE6D7"},
    # SS.HH → gris neutro
    "SSHH": {"fill": "rgba(205,205,205,0.65)", "line": "#888888", "hex": "#CDCDCD"},
    # Escalera → rojo ladrillo
    "Escalera": {"fill": "rgba(230,120,110,0.65)", "line": "#B03030", "hex": "#E67870"},
    # SUM → amarillo cálido
    "SUM": {"fill": "rgba(245,210,110,0.65)", "line": "#D09000", "hex": "#F5D26E"},
    # Cocina → naranja cálido
    "Cocina": {"fill": "rgba(240,175,115,0.65)", "line": "#C06040", "hex": "#F0AF73"},
    # EPT → terracota
    "EPT": {"fill": "rgba(220,130,100,0.65)", "line": "#A04020", "hex": "#DC8264"},
    # Dirección → teal suave
    "Direccion": {"fill": "rgba(150,205,208,0.65)", "line": "#007080", "hex": "#96CDD0"},
    # Sala → celeste
    "Sala": {"fill": "rgba(175,220,248,0.65)", "line": "#0270B0", "hex": "#AFDCF8"},
    # Área → lavanda
    "Área": {"fill": "rgba(215,185,225,0.65)", "line": "#7020A0", "hex": "#D7B9E1"},
    # Losa deportiva → verde intenso
    "Losa": {"fill": "rgba(90,170,90,0.40)", "line": "#2A6A2A", "hex": "#5AAA5A"},
    # Patio → verde pasto
    "Patio": {"fill": "rgba(110,185,110,0.40)", "line": "#307030", "hex": "#6EB96E"},
    # Psicomotricidad → ámbar
    "Psicomotricidad": {"fill": "rgba(245,180,80,0.65)", "line": "#D07800", "hex": "#F5B450"},
}

DEFAULT_STYLE = {"fill": "rgba(200,200,200,0.5)", "line": "#757575", "hex": "#CCCCCC"}


def get_ambiente_style(nombre: str) -> dict:
    """Devuelve el estilo (fill, line, hex) para un ambiente dado su nombre."""
    for clave, estilo in COLOR_MAP_AMBIENTES.items():
        if clave.lower() in nombre.lower():
            return estilo
    return DEFAULT_STYLE


def get_color_hex(nombre: str) -> str:
    """Devuelve solo el color hex para usar en Mesh3d."""
    return get_ambiente_style(nombre)["hex"]


def get_color_fill(nombre: str) -> str:
    """Devuelve el color fill (rgba) para usar en Scatter/shapes 2D."""
    return get_ambiente_style(nombre)["fill"]


def get_color_line(nombre: str) -> str:
    """Devuelve el color de línea para usar en bordes 2D."""
    return get_ambiente_style(nombre)["line"]
