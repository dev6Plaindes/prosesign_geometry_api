from typing import TypedDict

from src.bim.schemas.schema_dto import ProjectDataForReport


class ReturnPipeline(TypedDict):
    status : bool
    message : str

class PipelineContextReport(ProjectDataForReport):
    path_temp_steps : str | None = None
    pisos_pabellon: dict | None = None
    total_alumnos: int | None = None
    resumen_ambientes_raw : list[list[str | float | int]] | None = None
    url_pdf : str | None = None