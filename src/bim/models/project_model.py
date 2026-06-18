from sqlalchemy import Column, Integer, String, DateTime, JSON, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ProjectDB(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    zone = Column(String)
    tipologia = Column(String)
    departamento = Column(String)
    provincia = Column(String)
    distrito = Column(String)
    manager = Column(String)
    client = Column(String)
    ubication = Column(String)
    tipo = Column(String)
    vertices_terreno_utm = Column(JSON)
    aforo = Column(JSON)
    parent_id = Column(Integer, default=0)
    user_id = Column(Integer, default=3)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

