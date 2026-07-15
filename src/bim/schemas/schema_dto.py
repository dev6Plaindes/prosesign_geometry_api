from dataclasses import dataclass
from typing import TypedDict
from typing import TypedDict, Literal
from pydantic import BaseModel

from src.bim.schemas.project_schema import Aforo

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

OpcionesCategoria = Literal["A", "B", "C", "D", "E", "F", "G", "H", "I"]

class DataFormCostosInfra(TypedDict):
    muros_y_columnas : OpcionesCategoria
    techos : OpcionesCategoria
    puertas_y_ventanas : OpcionesCategoria
    revestimientos : OpcionesCategoria
    banos : OpcionesCategoria
    pisos : OpcionesCategoria
    instalaciones : OpcionesCategoria


OpcionesRegion = Literal["A", "B", "I"]


class ProjectDataForReport(BaseModel):
    id : int
    name : str
    departamento: str
    provincia: str
    distrito : str
    zone: str
    manager: str
    client: str
    aforo: list[dict]
    resumen_ambientes: list[dict]
    
class ProjectDataForCostos(BaseModel):
    id : int
    aforo: list[Aforo]
    resumen_ambientes: list[dict]
    region : str
    
