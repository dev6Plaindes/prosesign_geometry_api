from pydantic import BaseModel
from typing import Optional

class ProjectPDFResponse(BaseModel):
    status: str
    url_pdf: str