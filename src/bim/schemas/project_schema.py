# [DOCUMENTACIÓN] Se agregaron campos number_floors y ambientes para la Tarea 5&6 de complementarios y balcones.
from pydantic import BaseModel, Field
from typing import Dict, TypedDict, List, Optional

class Aforo(TypedDict):
    grado : str
    aforo_por_grado : int
    cantidad_aulas : int
    aulas: Dict[str, int]
    
class Vertice(TypedDict):
    vertice : str
    x : float
    y : float

class AmbienteRequest(TypedDict):
    ambienteComplementario: str
    capacidad: int

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
    number_floors: int = 1
    ambientes: List[AmbienteRequest] = []
    vertices_rectangle: Optional[List[List[float]]] = None
    angle: Optional[float] = None
    excluded_vertices: Optional[List[List[float]]] = None
    user_id : int