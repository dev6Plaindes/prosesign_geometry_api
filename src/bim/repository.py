from dataclasses import dataclass
import json

from sqlalchemy import func, insert, text
from src.bim.models.project_model import ProjectDB
from src.bim.schemas.project_schema import ProjectRequest
from src.bim.schemas.schema_dto import Project, ProjectUpdateDTO
from src.connection_db import connection_db
from src.utils.logger import logger

engine = connection_db()

def ensure_content_svg_column():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE niveles_step ADD COLUMN content_svg LONGTEXT NULL"))
            logger.info("Columna content_svg añadida a niveles_step")
    except Exception:
        logger.info("Columna content_svg ya existe en niveles_step")

def ensure_content_pdf_column():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE projects ADD COLUMN content_pdf MEDIUMBLOB NULL"))
            logger.info("Columna content_pdf añadida a projects")
    except Exception:
        logger.info("Columna content_pdf ya existe en projects")

def ensure_custom_rectangle_columns():
    # [DOCUMENTACIÓN] Se añaden automáticamente las columnas para soportar el rectángulo máximo
    # seleccionado en el frontend y los vértices excluidos.
    columns = [
        ("vertices_rectangle", "JSON"),
        ("angle", "DOUBLE"),
        ("excluded_vertices", "JSON")
    ]
    for col_name, col_type in columns:
        try:
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type} NULL"))
                logger.info(f"Columna {col_name} añadida a projects")
        except Exception:
            logger.info(f"Columna {col_name} ya existe en projects")

def update_content_pdf(id: int, pdf_binary: bytes) -> bool:
    query = text("""
        UPDATE projects SET content_pdf = :content_pdf WHERE id = :id
    """)
    with engine.begin() as conn:
        result = conn.execute(query, {"content_pdf": pdf_binary, "id": id})
        return result.rowcount > 0

def get_content_pdf(id: int):
    try:
        query = text("""
            SELECT content_pdf FROM projects WHERE id = :id
        """)
        with engine.connect() as conn:
            row = conn.execute(query, {"id": id}).fetchone()
            if row:
                return row[0]
            return None
    except Exception as e:
        logger.warning(f"Columna content_pdf no disponible en projects: {e}")
        return None

def get_content_step(id_project : int):
    query = text("""
        SELECT * FROM niveles_step
        WHERE id_project = :id_project             
    """)
    
    with engine.connect() as conn:
        result = conn.execute(
            query, {"id_project": id_project}
        )
        rows = result.fetchall()

        return [row._asdict() for row in rows]


def save_content_step(id_project : int, content_step : str, nivel : int, content_svg : str = None) -> None:
    query = text("""
        INSERT niveles_step (content_step, id_project, nivel, content_svg)
        VALUES
        (:content_step, :id_project, :nivel, :content_svg)             
    """)
    
    data_insert = {
        "content_step" : content_step,
        "id_project" : id_project,
        "nivel" : nivel,
        "content_svg" : content_svg
    }
    
    with engine.begin() as conn:
        response_save = conn.execute(
            query, data_insert
        )

def update_content_svg(id_project: int, nivel: int, content_svg: str) -> bool:
    query = text("""
        UPDATE niveles_step
        SET content_svg = :content_svg
        WHERE id_project = :id_project AND nivel = :nivel
    """)
    with engine.begin() as conn:
        result = conn.execute(query, {
            "content_svg": content_svg,
            "id_project": id_project,
            "nivel": nivel
        })
        return result.rowcount > 0
        

def insert_new_project_school(project: ProjectRequest, parent_id=None) -> int:
    data_req = project.model_dump()
    
    data_req["vertices_terreno_utm"] = data_req.pop("vertices")
    data_req["client"] = data_req.pop("cliente")
    data_req["manager"] = data_req.pop("responsable")
    data_req["ubication"] = data_req.get("departamento")
    
    data_req["created_at"] = func.now()
    data_req["updated_at"] = func.now()
    if parent_id != None:
        
        data_req["parent_id"] = parent_id
    
    # [DOCUMENTACIÓN] Se filtran las claves de data_req para incluir únicamente las que corresponden a columnas válidas en ProjectDB. Esto evita errores de compilación de SQLAlchemy (CompileError: Unconsumed column names) cuando se añaden campos adicionales al esquema Pydantic (como ambientes y number_floors).
    valid_columns = {c.name for c in ProjectDB.__table__.columns}
    data_req = {k: v for k, v in data_req.items() if k in valid_columns}
    
    with engine.begin() as conn:
        logger.info("GUARDANDO DATOS INICIALES DEL PROYECTO COLEGIO...")
        
        stmt = insert(ProjectDB).values(**data_req)
        result = conn.execute(stmt)
        
        id_new_project = result.inserted_primary_key[0]
        
        logger.info("DATOS INICIALES GUARDADO")
        logger.info(f"ID DEL NUEVO PROYECTO: {id_new_project}")
        
    return id_new_project

def create_new_version_project(project: ProjectRequest, parent_id : int):
    logger.info(f"GUARDANDO NUEVA VERSION DEL PROYECTO ID: {parent_id}")
    id_new = insert_new_project_school(project, parent_id=parent_id)
    return id_new


def update_status_job_project(id, status, job_id=None) -> bool:

    if job_id != None:
        query = text("""
            UPDATE projects 
            SET status_job = :status_job,
            job_id = :job_id
            WHERE id = :id
        """)

        with engine.begin() as conn:
            result = conn.execute(
                query, {"status_job": status, "id": id, "job_id": job_id}
            )
            return result.rowcount > 0
    else:
        query = text("""
            UPDATE projects 
            SET status_job = :status_job
            WHERE id = :id
        """)

        with engine.begin() as conn:
            result = conn.execute(query, {"status_job": status, "id": id})
            return result.rowcount > 0


# [DOCUMENTACIÓN] Se actualizaron las consultas SELECT de get_project_by_id y get_all_project para incluir las columnas:
# vertices, status_job, job_id, resumen_ambientes, tipo_institucion, region, url_pdf, ambientes,
# vertices_rectangle, angle y excluded_vertices.
def get_project_by_id(id):
    query = text("""
        SELECT id, name, zone, tipologia, departamento, provincia, distrito,
               manager, client, ubication, tipo, vertices_terreno_utm, aforo,
               number_floors, user_id, parent_id, created_at, updated_at,
               vertices, status_job, job_id, resumen_ambientes, tipo_institucion, region, url_pdf, ambientes,
               vertices_rectangle, angle, excluded_vertices
        FROM projects
        WHERE id = :id
        LIMIT 1
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"id": id})
        row = result.fetchone()

        if row:
            project_dict = row._asdict()
            
            # Columnas propensas a venir como string JSON que necesitas parsear
            json_columns = ["ambientes", "aforo", "vertices", "resumen_ambientes"]
            
            for col in json_columns:
                if col in project_dict and isinstance(project_dict[col], str):
                    try:
                        # Convertimos el string serializado a un objeto Python real (list o dict)
                        project_dict[col] = json.loads(project_dict[col])
                    except (json.JSONDecodeError, TypeError):
                        logger.warning(f"No se pudo parsear como JSON la columna: {col}")
                        # En caso de que falle o venga vacío, puedes dejarlo como estaba o poner un default []
                        pass
                        
            return project_dict
        return None

def get_all_project():
    query = text("""
        SELECT id, name, zone, tipologia, departamento, provincia, distrito,
               manager, client, ubication, tipo, vertices_terreno_utm, aforo,
               number_floors, user_id, parent_id, created_at, updated_at,
               vertices, status_job, job_id, resumen_ambientes, tipo_institucion, region, url_pdf, ambientes,
               vertices_rectangle, angle, excluded_vertices
        FROM projects
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

        return [row._asdict() for row in rows]


def update_data_project(id: int, data_project: ProjectUpdateDTO) -> bool:
    query = text("""
        UPDATE projects 
        SET vertices = :vertices,
            resumen_ambientes = :resumen_ambientes,
            tipo_institucion = :tipo_institucion,
            aforo = :aforo,
            region = :region
            
        WHERE id = :id
    """)

    print("Actualizando proyecto ID:", id)

    with engine.begin() as conn:
        result = conn.execute(query, {
            "id": id,
            "vertices": json.dumps(data_project["vertices"]),
            "resumen_ambientes": json.dumps(data_project["resumen_ambientes"]),
            "tipo_institucion": json.dumps(data_project["tipo_institucion"]),
            "aforo" : json.dumps(data_project["aforo"]),
            "region" : data_project["region"]
        })
        
        return result.rowcount > 0
    
def update_url_pdf_project(id, url_pdf: str) -> bool:
    query = text("""
        UPDATE projects 
        SET url_pdf = :url_pdf
        WHERE id = :id
    """)

    print("Actualizando URL del PDF del proyecto con ID:", id)
    with engine.begin() as conn:
        result = conn.execute(query, {"url_pdf": url_pdf, "id": id})
        return result.rowcount > 0

def update_data_calculo_costos_project(id, data_calculo_costos : list[dict]):

    query = text("""
        UPDATE projects 
        SET data_calculo_costos = :data_calculo_costos
        WHERE id = :id
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"data_calculo_costos": data_calculo_costos, "id": id})
        return result.rowcount > 0
    
def create_data_calculo_costos_project(id, data_calculo_costos : list[dict]):

    query = text("""
        INSERT INTO costos_project (id_project, data_calculo_costos)
        VALUES (:id_project, :data_calculo_costos)
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"data_calculo_costos": data_calculo_costos, "id_project": id})
        return result.rowcount > 0

def get_data_calculo_costos_project(id : int):
    query = text("""
        SELECT data_calculo_costos, id_project
        FROM costos_project 
        WHERE id_project = :id_project
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"id_project": id})
        rows = result.fetchall()
        
        processed_rows = []
        for row in rows:
            row_dict = row._asdict()
            # Convertimos la columna de texto a formato JSON (lista/dict de Python)
            if row_dict['data_calculo_costos']:
                row_dict['data_calculo_costos'] = json.loads(row_dict['data_calculo_costos'])
            
            processed_rows.append(row_dict)
            
        return processed_rows