from dataclasses import dataclass
from typing import TypedDict

from pydantic import BaseModel

class Project(BaseModel):
    name : str
    departamento: str
    provincia: str
    distrito : str
    zone: str
    responsable: str
    cliente: str

@dataclass
class NivelesStepDTO:
    id_nivel_step : int
    content_step : str
    id_project : int
    nivel : int

class ProjectUpdateDTO(TypedDict):
    vertices : list
    resumen_ambientes : list[dict]
    tipo_institucion : str
    aforo : list[dict]
    region : str