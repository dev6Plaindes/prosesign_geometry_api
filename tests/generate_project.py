from src.bim.services import service_generate_project
from src.bim.schemas.project_schema import ProjectRequest

request_data = {
    "name": "PROJECT",
    "tipologia": "Educación",
    "zone": "Urbano",
    "tipo": "UNIDOCENTE",
    "departamento": "HUANUCO",
    "provincia": "HUACAYBAMBA",
    "distrito": "COCHABAMBA",
    "responsable": "RESPONSABLE",
    "cliente": "EMPRESA SAC",
    "aforo": [
        {
            "grado": "INICIAL",
            "aforo_por_grado": 20,
            "cantidad_aulas": 2
        },
        {
            "grado": "PRIMARIA",
            "aforo_por_grado": 20,
            "cantidad_aulas": 6
        },
        {
            "grado": "SECUNDARIA",
            "aforo_por_grado": 10,
            "cantidad_aulas": 5
        }
    ],
    "vertices": [
        {
            "vertice": "V1",
            "x": 301686.819,
            "y": 8933010.389
        },
        {
            "vertice": "V2",
            "x": 301784.025,
            "y": 8933010.389
        },
        {
            "vertice": "V3",
            "x": 301784.025,
            "y": 8932948.875
        },
        {
            "vertice": "V4",
            "x": 301716.755,
            "y": 8932934.421
        },
        {
            "vertice": "V5",
            "x": 301672.692,
            "y": 8932955.262
        }
    ]
}

data_project : ProjectRequest = ProjectRequest(**request_data)
service_generate_project(request_data=data_project)