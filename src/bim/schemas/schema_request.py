from pydantic import BaseModel

class CostosRequest(BaseModel):
    muros_y_columnas : str
    techos : str
    pisos : str
    puertas_y_ventanas : str
    revestimientos : str
    banos : str
    instalaciones: str