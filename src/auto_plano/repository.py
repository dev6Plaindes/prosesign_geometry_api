import json
import os
from sqlalchemy import create_engine, text

# Configuramos la URL de conexión usando tus variables
DB_USER = "root"
DB_PASS = "rootpassword"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "db_arquitectura"

# Cadena de conexión para MySQL
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def actualizar_vectores_proyecto(id_proyecto, vectores):
    """
    Toma el df_global, lo limpia y actualiza la columna JSON en db_arquitectura.
    """
    # 1. Preparar los datos (convertir Polygons a listas de coordenadas)
    # Usamos la función de limpieza que definimos antes
    json_payload = json.dumps(vectores)

    # 2. Crear motor de base de datos
    engine = create_engine(DATABASE_URL)

    # 3. Sentencia de actualización
    # Ajusta 'nombre_tabla' y 'columna_json' según tu esquema real
    query = text("""
        UPDATE projects 
        SET vertices_generadas = :vectores, 
            updated_at = NOW() 
        WHERE id = :id
    """)

    try:
        with engine.begin() as conn:
            result = conn.execute(query, {"id": id_proyecto, "vectores": json_payload})
            
            if result.rowcount > 0:
                print(f"✅ [DB] Proyecto {id_proyecto} actualizado en {DB_NAME}")
                return True
            else:
                print(f"⚠️ [DB] No se encontró el ID {id_proyecto} para actualizar.")
                return False
                
    except Exception as e:
        print(f"❌ [DB] Error en la conexión a {DB_HOST}: {e}")
        return False
    
    
def obtener_proyecto_por_id(id_proyecto):
    """
    Realiza un SELECT * de la tabla proyectos filtrando por ID.
    Retorna un diccionario con los datos o None si no existe.
    """
    engine = create_engine(DATABASE_URL)
    
    # Consulta SQL con parámetros seguros
    query = text("SELECT * FROM projects WHERE id = :id LIMIT 1")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"id": id_proyecto}).mappings().first()
            
            if result:
                # Convertimos el objeto RowMapping a un diccionario común
                proyecto_dict = dict(result)
                
                # Si la columna JSON viene como string (depende de la versión del driver),
                # la parseamos a objeto Python para que sea fácil de usar.
                if isinstance(proyecto_dict.get("vertices_generadas"), str):
                    proyecto_dict["vertices_generadas"] = json.loads(proyecto_dict["vertices_generadas"])
                
                print(f"✅ [DB] Datos del proyecto {id_proyecto} recuperados.")
                return proyecto_dict
            else:
                print(f"⚠️ [DB] No se encontró el proyecto con ID {id_proyecto}.")
                return None
                
    except Exception as e:
        print(f"❌ [DB] Error al consultar la base de datos: {e}")
        return None