from dataclasses import dataclass
from bim.capas import FactoryCapas
from src.bim.schemas.project_schema import ProjectRequest
from typing import TypedDict

class TypeSteps(TypedDict):
    nivel : int
    step : str
    

@dataclass
class PipelineContext:
    id_project: int # id de la version del proyecto
    request: ProjectRequest
    region: str | None = None
    ambientes : list[dict] | None = None
    resumen_ambientes : list[dict] | None = None
    factory_capas: FactoryCapas | None = None
    vertices_plano : list[dict] | None = None
    id_version_project: int | None = None # id de la version del proyecto
    