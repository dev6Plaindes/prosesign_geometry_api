from pydantic import BaseModel
from src.bim.schemas.project_schema import Aforo
from src.bim.schemas.schema_dto import ProjectDataForCostos
from src.bim.schemas.schema_request import CostosRequest

class PipelineContextCostos(BaseModel):
    data_req : CostosRequest
    data_project : ProjectDataForCostos
    data_calculo_costos : list[dict] | None = None
