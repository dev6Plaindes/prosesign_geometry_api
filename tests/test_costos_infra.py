import json

from src.bim.repository import get_project_by_id
from src.bim.schemas.schema_dto import DataFormCostosInfra, ProjectDataForCostos
from src.bim.pipeline.project_school.costos.main_pipeline import calculate_costos_pipeline
from src.bim.schemas.schema_request import CostosRequest

data_req : DataFormCostosInfra = {
    "muros_y_columnas": "A",
    "techos": "A",
    "pisos": "A",
    "puertas_y_ventanas": "A",
    "revestimientos": "A",
    "banos": "A",
    "instalaciones": "A"
}

project_data = get_project_by_id(786)

data_req_model = CostosRequest(**data_req)

project_data["aforo"] = json.loads(project_data["aforo"])
project_data["resumen_ambientes"] = json.loads(project_data["resumen_ambientes"])
project_data_model = ProjectDataForCostos(**project_data)

calculate_costos_pipeline(
    data_req=data_req_model,
    data_project=project_data_model
)
