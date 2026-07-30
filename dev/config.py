# from dataclasses import dataclass
from typing import TypedDict

class ConfigProject(TypedDict):
    largo_cuadrante : float
    ancho_cuadrante : float
    ancho_aula: float
    alto_nivel: float
    e_muro: float
    e_techo: float
    ancho_col: float
    espesor_piso: float
    ancho_puerta: float
    alto_puerta: float
    mocheta_puerta: float
    ancho_pasadiso: float
    ancho_escalera: float
    zona_climatica : str
    ancho_viga: float


CONFIG_PROYECTO : ConfigProject = {
    'largo_cuadrante': None,
    'ancho_cuadrante': None,
    'ancho_aula': 8.0,
    'alto_nivel': 2.7,
    'e_muro': 0.20,
    'e_techo': 0.20,
    'ancho_col': 0.3,
    "espesor_piso" : 0.20,
    'ancho_puerta' : 0.90,
    'alto_puerta' : 2.10,
    'mocheta_puerta' : 0.30,
    'ancho_pasadiso' : 1.8,
    "ancho_escalera" : 1.0,
    "zona_climatica" : "z1",
    "ancho_viga": 0.3
}
