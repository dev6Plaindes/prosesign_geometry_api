# [DOCUMENTACIÓN]
# Este archivo fue creado para realizar pruebas de conexión a los servicios externos e internos del sistema:
# 1. Base de datos MySQL local (utilizada para almacenar la información de los proyectos y las URLs de los PDFs).
# 2. Conectividad a AWS S3 (usado por ProInvierte para guardar los reportes PDF del proyecto).
# 3. Conectividad al endpoint de ProBudgets (sincronización de metadatos técnicos).
# Permite diagnosticar rápidamente la falta de variables de entorno y errores de autenticación.

import os
import sys
import json
import urllib.request
import urllib.error

# Añadir el directorio raíz al path para permitir ejecuciones directas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

def test_database_connection():
    print("\n=== 1. Probando Conexión a Base de Datos (MySQL) ===")
    try:
        from src.connection_db import connection_db
        from sqlalchemy import text
        
        engine = connection_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ [DB] Conexión establecida con éxito a MySQL.")
                return True
            else:
                print("❌ [DB] Respuesta inesperada del servidor de base de datos.")
                return False
    except Exception as e:
        print(f"❌ [DB] Error al conectar a la base de datos: {e}")
        return False

def test_aws_s3_connection():
    print("\n=== 2. Probando Conexión a AWS S3 (ProInvierte Storage) ===")
    
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    bucket_name = "plaindes"
    
    print(f"   - AWS_ACCESS_KEY_ID: {aws_access_key[:4] + '***' if aws_access_key else 'NO CONFIGURADO'}")
    print(f"   - AWS_SECRET_ACCESS_KEY: {'***' if aws_secret_key else 'NO CONFIGURADO'}")
    print(f"   - AWS_DEFAULT_REGION: {aws_region}")
    print(f"   - Bucket Name: {bucket_name}")
    
    if not aws_access_key or not aws_secret_key:
        print("⚠️  [S3] FALTAN CREDENCIALES: No se han configurado AWS_ACCESS_KEY_ID o AWS_SECRET_ACCESS_KEY en el archivo .env del backend.")
        print("   Por favor, agrégalas para completar la integración con ProInvierte.")
        return False
        
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Realizamos una operación liviana para verificar que las credenciales funcionen y que tengamos acceso
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ [S3] Conexión establecida. El bucket '{bucket_name}' es accesible.")
        return True
    except NoCredentialsError:
        print("❌ [S3] Error: No se encontraron las credenciales de AWS.")
        return False
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '403':
            print(f"❌ [S3] Error 403: Acceso denegado al bucket '{bucket_name}'. Revisa los permisos de la clave de AWS.")
        elif error_code == '404':
            print(f"❌ [S3] Error 404: El bucket '{bucket_name}' no existe en la región '{aws_region}'.")
        else:
            print(f"❌ [S3] Error del cliente de AWS: {e}")
        return False
    except Exception as e:
        print(f"❌ [S3] Ocurrió un error inesperado al conectar a S3: {e}")
        return False

def test_probudgets_connection():
    print("\n=== 3. Probando Conexión a la API de ProBudgets ===")
    
    # Intentamos leer de los archivos .env del proyecto
    # Buscamos primero en el .env de la aplicación frontend si existe
    probudgets_url = "https://apiprobudget.pro-invest.pe"
    probudgets_token = None
    
    # Buscar variables de entorno de ProBudgets (pueden venir del env del frontend o cargarse manualmente)
    frontend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prodesign", ".env"))
    if os.path.exists(frontend_env_path):
        try:
            with open(frontend_env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("VITE_URL_PROBUDGETS"):
                        probudgets_url = line.split("=")[1].strip()
                    if line.strip().startswith("VITE_PROBUDGETS_TOKEN"):
                        probudgets_token = line.split("=")[1].strip()
        except Exception as e:
            print(f"   (No se pudo leer el archivo .env del frontend: {e})")
            
    print(f"   - URL de ProBudgets: {probudgets_url}")
    print(f"   - Token de ProBudgets: {probudgets_token[:8] + '...' if probudgets_token else 'NO CONFIGURADO (Usando fallback local)'}")
        
    if not probudgets_token or probudgets_token == "TU_TOKEN_BEARER_AQUI":
        print("⚠️  [ProBudgets] ADVERTENCIA: No se detectó un Token de ProBudgets válido en prodesign/.env.")
        print("   Se intentará realizar una petición de prueba básica.")
    
    endpoint = f"{probudgets_url}/v1/integracion/sync"
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'ProDesign-Connection-Test'
    }
    if probudgets_token:
        headers['Authorization'] = f"Bearer {probudgets_token}"
        
    # Enviamos un payload mínimo para ver cómo reacciona el endpoint
    dummy_payload = {
        "nombreProyecto": "Test de Conexión ProDesign",
        "tipologia": "Educación",
        "cimentaciones": [],
        "ambientes": []
    }
    
    try:
        req = urllib.request.Request(
            endpoint, 
            data=json.dumps(dummy_payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            print(f"✅ [ProBudgets] Conexión establecida con éxito. Código de respuesta: {status_code}")
            return True
            
    except urllib.error.HTTPError as e:
        # 401/403 significa que el servidor está levantado y respondió, pero el token es inválido/insuficiente
        if e.code in [401, 403]:
            print(f"⚠️  [ProBudgets] Conectado al servidor, pero no autorizado (Código {e.code}).")
            print("   Esto confirma que la red funciona, pero necesitas ingresar un Token válido en prodesign/.env (VITE_PROBUDGETS_TOKEN).")
            return True
        elif e.code == 400:
            print("✅ [ProBudgets] Servidor contactado (Código 400 Bad Request).")
            print("   Esto es esperado ya que enviamos un payload vacío/incompleto para la prueba de ping.")
            return True
        else:
            print(f"❌ [ProBudgets] El servidor respondió con un error (Código {e.code}): {e.reason}")
            return False
    except urllib.error.URLError as e:
        print(f"❌ [ProBudgets] Error de conexión / DNS no alcanzable: {e.reason}")
        print("   Por favor verifica la conexión a internet y que el host sea correcto.")
        return False
    except Exception as e:
        print(f"❌ [ProBudgets] Error inesperado al probar conexión: {e}")
        return False

if __name__ == "__main__":
    print("=========================================================")
    print("      DIAGNÓSTICO DE CONEXIONES EXTERNAS PRODESIGN       ")
    print("=========================================================")
    
    db_ok = test_database_connection()
    s3_ok = test_aws_s3_connection()
    pb_ok = test_probudgets_connection()
    
    print("\n======================= RESUMEN =======================")
    print(f"1. Base de datos MySQL:  {'OK' if db_ok else 'FALLÓ'}")
    print(f"2. AWS S3 (ProInvierte): {'OK' if s3_ok else 'INCOMPLETO / SIN CREDENCIALES'}")
    print(f"3. API de ProBudgets:    {'OK' if pb_ok else 'FALLÓ / INACCESIBLE'}")
    print("=========================================================")
