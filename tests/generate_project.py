from src.bim.services import service_generate_project
from src.bim.schemas.project_schema import ProjectRequest

# request_data = {
#     "name": "PROJECT",
#     "tipologia": "Educación",
#     "zone": "Urbano",
#     "tipo": "UNIDOCENTE",
#     "departamento": "HUANUCO",
#     "provincia": "HUACAYBAMBA",
#     "distrito": "COCHABAMBA",
#     "responsable": "RESPONSABLE",
#     "cliente": "EMPRESA SAC",
#     "aforo": [
#         {"grado": "INICIAL", "aforo_por_grado": 20, "cantidad_aulas": 2},
#         {"grado": "PRIMARIA", "aforo_por_grado": 20, "cantidad_aulas": 6},
#         {"grado": "SECUNDARIA", "aforo_por_grado": 10, "cantidad_aulas": 5},
#     ],
#     "vertices": [
#         {
#             "vertice": "V1",
#             "x": 301678.281,
#             "y": 8932998.195
#         },
#         {
#             "vertice": "V2",
#             "x": 301772.175,
#             "y": 8933023.353
#         },
#         {
#             "vertice": "V3",
#             "x": 301788.096,
#             "y": 8932963.935
#         },
#         {
#             "vertice": "V4",
#             "x": 301726.859,
#             "y": 8932932.563
#         },
#         {
#             "vertice": "V5",
#             "x": 301678.904,
#             "y": 8932941.29
#         }
#     ],
#     "vertices_rectangle": [
#         [
#             301693.4981041939,
#             8932939.354030397
#         ],
#         [
#             301787.5850093572,
#             8932963.68655853
#         ],
#         [
#             301772.3951095247,
#             8933022.421543121
#         ],
#         [
#             301678.30820436147,
#             8932998.089014988
#         ]
#     ],
#     "ambientes": [
#         {"ambienteComplementario": "Cocina escolar", "capacidad": 0},
#         {"ambienteComplementario": "Sala de Usos Múltiples (SUM)", "capacidad": 0},
#         {"ambienteComplementario": "Comedor", "capacidad": 0},
#         {"ambienteComplementario": "Patio Inicial", "capacidad": 0},
#     ],
#     "user_id": 7,
# }

request_data = {
    "name": "NUEVO PROYECYO",
    "tipologia": "Educación",
    "zone": "Urbano",
    "tipo": "UNIDOCENTE",
    "number_floors": "1",
    "departamento": "LAMBAYEQUE",
    "provincia": "FERREÑAFE",
    "distrito": "CAÑARIS",
    "responsable": "JOSE JOSE",
    "cliente": "EMPRES SAC",
    "width": 43.916196196572855,
    "height": 49.78106187470257,
    "vertices_rectangle": [
        [
            296280.83649883093,
            8939939.134825742
        ],
        [
            296309.93625087215,
            8939972.026112119
        ],
        [
            296272.65243979415,
            8940005.012041738
        ],
        [
            296243.55268775293,
            8939972.120755361
        ]
    ],
    "angle": 48.5,
    "excluded_vertices": [],
    "aforo": [
        {
            "grado": "INICIAL",
            "aforo_por_grado": 0,
            "cantidad_aulas": 0
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
            "x": 296287.32,
            "y": 8939934.03
        },
        {
            "vertice": "V2",
            "x": 296296.18,
            "y": 8939947.84
        },
        {
            "vertice": "V3",
            "x": 296309.97,
            "y": 8939969.55
        },
        {
            "vertice": "V4",
            "x": 296309.84,
            "y": 8939981.56
        },
        {
            "vertice": "V5",
            "x": 296315.69,
            "y": 8939993.88
        },
        {
            "vertice": "V6",
            "x": 296301.56,
            "y": 8940009.1
        },
        {
            "vertice": "V7",
            "x": 296293.93,
            "y": 8940009.74
        },
        {
            "vertice": "V8",
            "x": 296289.26,
            "y": 8940009.89
        },
        {
            "vertice": "V9",
            "x": 296282.3,
            "y": 8940010.05
        },
        {
            "vertice": "V10",
            "x": 296282.07,
            "y": 8940007.58
        },
        {
            "vertice": "V11",
            "x": 296278.58,
            "y": 8940004.61
        },
        {
            "vertice": "V12",
            "x": 296275.87,
            "y": 8940004.28
        },
        {
            "vertice": "V13",
            "x": 296270.45,
            "y": 8940005.52
        },
        {
            "vertice": "V14",
            "x": 296256.73,
            "y": 8939999.75
        },
        {
            "vertice": "V15",
            "x": 296253.88,
            "y": 8940000.13
        },
        {
            "vertice": "V16",
            "x": 296250.12,
            "y": 8939997.66
        },
        {
            "vertice": "V17",
            "x": 296244.39,
            "y": 8939991.32
        },
        {
            "vertice": "V18",
            "x": 296242.64,
            "y": 8939985.86
        },
        {
            "vertice": "V19",
            "x": 296243.27,
            "y": 8939973.23
        },
        {
            "vertice": "V20",
            "x": 296244.73,
            "y": 8939967.4
        },
        {
            "vertice": "V21",
            "x": 296254.3,
            "y": 8939959.83
        }
    ],
    "ambientes": [
        {
            "ambienteComplementario": "Sala de Usos Múltiples (SUM)",
            "capacidad": 0
        },
        {
            "ambienteComplementario": "Cocina escolar",
            "capacidad": 0
        }
    ],
    "user_id": 7
}

data_project: ProjectRequest = ProjectRequest(**request_data)
service_generate_project(request_data=data_project)
