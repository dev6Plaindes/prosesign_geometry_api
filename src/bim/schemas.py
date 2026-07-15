
from pydantic import BaseModel


class Project(BaseModel):
    name : str
    departamento: str
    provincia: str
    distrito : str
    zone: str
    responsable: str
    cliente: str
    