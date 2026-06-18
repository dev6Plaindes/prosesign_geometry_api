from pydantic import BaseModel
from typing import Optional

class ProjectPDFResponse(BaseModel):
    status: str
    url_pdf: str
    
class GenerateProjectPDFResponse(BaseModel):
    status: str
    url_pdf: str
    id_project: int
    
class ResponseGenerateProject(BaseModel):
    project_id : int
    job_id : str
    
class ResponseGetJob(BaseModel):
    id : str
    status : str