import json

import pytest
from src.bim.pipeline.project_school.create.main_pipeline import generate_project_school_pipeline
from src.bim.repository import create_new_version_project, insert_new_project_school, update_status_job_project
from src.bim.schemas.project_schema import ProjectRequest
from src.bim.schemas.schema_dto import ProjectDataForReport
from src.bim.pipeline.project_school.report_pdf.main_pipeline import report_pdf_pipeline

def test_integration_generate_project(project_payload):
    request_data : ProjectRequest = ProjectRequest(**project_payload)
    id_new_project = insert_new_project_school(request_data)
    
    id_new_v_project = create_new_version_project(request_data, id_new_project)

    generate_project_school_pipeline(
        request_data=request_data,
        id_parent_project= id_new_project,
        id_version_project=id_new_v_project
    )

def test_integration_generate_pdf_project(project_payload_for_report_pdf):
    data_project = project_payload_for_report_pdf
    data_project["aforo"] = json.loads(data_project["aforo"])
    data_project["resumen_ambientes"] = json.loads(data_project["resumen_ambientes"])
    data_for_report = ProjectDataForReport(**data_project)
    url_resultado = report_pdf_pipeline(data_for_report)