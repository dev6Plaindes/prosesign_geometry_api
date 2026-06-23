from pydantic import BaseModel, Field
from typing import TypedDict, List

class Aforo(TypedDict):
    grado : str
    aforo_por_grado : int
    cantidad_aulas : int
    
class Vertice(TypedDict):
    vertice : str
    x : float
    y : float
    
class TerrenoRequest(BaseModel):
    vertices: List[Vertice]

class DataVerticesMaxCuad(TypedDict):    
    terreno : list[list[float]]
    maximo_cuadrante : list[list[float]]
    
class DictTerrenoMaxCuad(TypedDict):
    angle_max_cuadrante: float
    area_m2: float
    vertices : DataVerticesMaxCuad

class ProjectRequest(BaseModel):
    name: str = Field(..., min_length=2)
    tipologia: str = Field(..., json_schema_extra={"example": "Educación"})
    zone: str = Field(..., json_schema_extra={"example": "Urbano"})
    tipo: str = Field(..., json_schema_extra={"example": "UNIDOCENTE"})
    departamento: str
    provincia: str
    distrito: str
    responsable: str
    cliente: str
    aforo: List[Aforo]
    vertices: List[Vertice]
    
class ProjectRequestMaxCuad(BaseModel):
    name: str = Field(..., min_length=2)
    tipologia: str = Field(..., json_schema_extra={"example": "Educación"})
    zone: str = Field(..., json_schema_extra={"example": "Urbano"})
    tipo: str = Field(..., json_schema_extra={"example": "UNIDOCENTE"})
    departamento: str
    provincia: str
    distrito: str
    responsable: str
    cliente: str
    aforo: List[Aforo]
    vertices: List[Vertice]
    terreno_maximo_cuadrante : DictTerrenoMaxCuad