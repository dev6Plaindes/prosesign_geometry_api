import json

from sqlalchemy import text
from src.bim.schemas import Project
from src.connection_db import connection_db

engine = connection_db()

def insert_new_project_school(project_data: dict) -> int:
    project = Project(**project_data)

    query = text("""
            INSERT projects (name, zone, distrito, provincia, departamento, ubication, user_id, manager, parent_id, client, created_at, updated_at)
            VALUES
            (:name, :zone, :distrito, :provincia, :departamento, :ubication, :user_id, :manager, :parent_id, :cliente, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """)
    
    data_insert = {
                "name": project.name,
                "zone": project.zone,
                "distrito": project.distrito,
                "provincia": project.provincia,
                "departamento": project.departamento,
                "ubication": project.departamento,
                "user_id": 3,
                "manager": project.responsable,
                "parent_id": 0,
                "cliente": project.cliente
            }

    with engine.begin() as conn:
        result_project = conn.execute(
            query,
            data_insert
        )

        id_project = result_project.lastrowid
        
        data_insert["parent_id"] = id_project
        v1_project = conn.execute(
            query,
            data_insert
        )
        id_v1_project = v1_project.lastrowid
    return id_v1_project


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


def get_project_by_id(id):
    query = text("""
        SELECT * FROM projects
        WHERE id = :id
        LIMIT 1
    """)

    with engine.begin() as conn:
        result = conn.execute(query, {"id": id})
        row = result.fetchone()

        if row:
            return row._asdict()
        return None

def get_all_project():
    query = text("""
        SELECT * FROM projects
    """)

    with engine.begin() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

        return [row._asdict() for row in rows]

def update_vertices_project(id, vertices: list) -> bool:
    query = text("""
        UPDATE projects 
        SET vertices = :vertices
        WHERE id = :id
    """)

    print("Actualizando vértices del proyecto con ID:", id)
    with engine.begin() as conn:
        result = conn.execute(query, {"vertices": json.dumps(vertices), "id": id})
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