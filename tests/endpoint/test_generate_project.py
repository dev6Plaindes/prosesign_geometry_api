import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

from src.bim.pipeline.project_school.create.main_pipeline import generate_project_school_pipeline

client = TestClient(app)

@patch("src.bim.route.service_generate_project")
def test_route_project_success(mock_service, project_payload):
    mock_service.return_value = {"project_id": 123, "job_id": "job_999"}
    
    # 2. Ejecutar
    response = client.post("/api/v3/generate-project", json=project_payload)
    
    # 3. Validar
    assert response.status_code == 200
    
    # Validar estructura y tipos usando el mismo modelo de respuesta (ResponseGenerateProject)
    data = response.json()
    assert isinstance(data["project_id"], int)
    assert isinstance(data["job_id"], str)
    assert data["project_id"] == 123
    
    mock_service.assert_called_once()
