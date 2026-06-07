import os
import io
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv
load_dotenv()

def descargar_archivo_de_s3(nombre_archivo: str, bucket_name: str) -> io.BytesIO:
    """
    Descarga un archivo desde un bucket de S3 y lo retorna como un objeto binario en memoria.
    
    :param nombre_archivo: La ruta/nombre del archivo dentro del bucket (Key)
    :param bucket_name: El nombre del bucket de AWS S3
    :return: Un objeto io.BytesIO que contiene los bytes del archivo
    """
    
    # 1. Cargar las variables de entorno de AWS
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    aws_path_files = os.getenv("AWS_PATH_FILES", "prodesign/test/") # Ruta base en S3 para organizar archivos
    # 2. Inicializar el cliente de S3 pasando las credenciales explícitamente
    nombre_archivo_completo = f"{aws_path_files}{nombre_archivo}"

    # 2. Inicializar el cliente de S3
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
        
        # 3. Crear un contenedor de bytes vacío en memoria
        archivo_en_memoria = io.BytesIO()

        # 4. Descargar el archivo directamente al contenedor
        print(f"⏳ Descargando '{nombre_archivo}' desde el bucket '{bucket_name}'...")
        s3_client.download_fileobj(bucket_name, nombre_archivo_completo, archivo_en_memoria)
        
        # 5. Resetear el puntero al inicio del archivo para que esté listo para ser leído
        archivo_en_memoria.seek(0)
        
        print(f"✅ Archivo descargado con éxito. Tamaño: {len(archivo_en_memoria.getvalue())} bytes.")
        return archivo_en_memoria

    except NoCredentialsError:
        print("❌ Error: No se encontraron las credenciales de AWS.")
        raise Exception("Credenciales de AWS no configuradas.")
    except ClientError as e:
        # Si el archivo no existe, AWS arrojará un error 404
        if e.response['Error']['Code'] == "404":
            print(f"❌ Error: El archivo '{nombre_archivo}' no existe en el bucket.")
        else:
            print(f"❌ Error de AWS Client: {e}")
        raise e
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado al descargar: {e}")
        raise e