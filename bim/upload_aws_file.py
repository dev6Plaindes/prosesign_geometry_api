import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
load_dotenv()

def subir_archivo_a_s3(archivo_binario, nombre_archivo: str, bucket_name: str) -> str:
    """
    Sube un archivo binario a un bucket de Amazon S3.
    
    :param archivo_binario: Objeto que contiene los bytes del archivo (ej. bytes, BytesIO, o un SpooledTemporaryFile)
    :param nombre_archivo: El nombre con el que se guardará el archivo en S3 (Key)
    :param bucket_name: El nombre del bucket de destino
    :return: La URL pública o confirmación del archivo subido
    """
    
    # 1. Cargar las variables de entorno de AWS
    # Boto3 busca automáticamente estas variables en el entorno del sistema
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-2") # Región por defecto si no se especifica
    aws_path_files = os.getenv("AWS_PATH_FILES", "prodesign/test/") # Ruta base en S3 para organizar archivos
    # 2. Inicializar el cliente de S3 pasando las credenciales explícitamente
    nombre_archivo_completo = f"{aws_path_files}{nombre_archivo}"
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # Asegurar que el puntero del archivo binario esté al inicio (por si fue leído antes)
        if hasattr(archivo_binario, "seek"):
            archivo_binario.seek(0)

        # 3. Subir el archivo binario usando upload_fileobj
        s3_client.upload_fileobj(
            archivo_binario,
            bucket_name,
            nombre_archivo_completo,
            # ExtraArgs={"ACL": "public-read"}  <-- Descomenta si necesitas que el archivo sea público
        )
        
        # Generar la URL del archivo subido
        url_archivo = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{nombre_archivo_completo}"
        print(f"🚀 Archivo '{nombre_archivo_completo}' subido con éxito a S3.")
        return url_archivo

    except NoCredentialsError:
        print("❌ Error: No se encontraron las credenciales de AWS.")
        raise Exception("Credenciales de AWS no configuradas.")
    except ClientError as e:
        print(f"❌ Error de AWS Client: {e}")
        raise e
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")
        raise e
    
from pathlib import Path

def obtener_archivo_en_binario(ruta_archivo: str) -> bytes:
    """
    Lee un archivo local desde su ruta y devuelve su contenido en formato binario.
    
    :param ruta_archivo: Ruta absoluta o relativa del archivo en el sistema.
    :return: Los bytes del archivo.
    """
    try:
        # Usamos Path para manejar rutas de forma limpia en cualquier Sistema Operativo (Windows/Linux/Mac)
        path = Path(ruta_archivo)
        
        # Verificamos si el archivo realmente existe antes de intentar abrirlo
        if not path.is_file():
            raise FileNotFoundError(f"El archivo no existe en la ruta especificada: {ruta_archivo}")
            
        # Abrimos en modo 'rb' (Lectura Binaria)
        with open(path, "rb") as archivo:
            contenido_binario = archivo.read()
            
        print(f"✅ Archivo '{path.name}' leído exitosamente. Tamaño: {len(contenido_binario)} bytes.")
        return contenido_binario

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        raise e
    except PermissionError:
        print(f"❌ Error: No tienes permisos para leer el archivo en '{ruta_archivo}'.")
        raise PermissionError(f"Permiso denegado para acceder a: {ruta_archivo}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al leer el archivo: {e}")
        raise e
    