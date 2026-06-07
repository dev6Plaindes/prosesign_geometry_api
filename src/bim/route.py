import base64
import io
import json

from build123d import vertices
from fastapi import APIRouter, Body
from fastapi.responses import HTMLResponse
from rq import Queue
from src.bim.schema import ProjectPDFResponse
from bim.upload_aws_file import obtener_archivo_en_binario, subir_archivo_a_s3
from src.bim.download_file_aws import descargar_archivo_de_s3
from bim.export_pdf import exportar_niveles_a_pdf
from bim.render_2d import (
    render_2d,
    render_2d_shapely,
    render_2d_shapely_automatico_regex,
)
from bim.render_3d import render_3d
from bim.render_wrap import wrap_plotly_figure_in_html
from bim.utils.step_to_json import datos_to_shapely
from src.motor.services.gemini_nanobanana import GeminiNanoBananaService
from src.motor.render import save_render_image
from src.bim.repository import (
    get_all_project,
    get_project_by_id,
    insert_new_project_school,
    update_status_job_project,
    update_url_pdf_project,
)
from src.bim.engine.school import generate_bim
from redis_conn import redis_conn
from rq.job import Job
from fastapi import APIRouter, HTTPException, status
import os
from botocore.exceptions import ClientError

q = Queue("prodesign:bim:school", connection=redis_conn)

router = APIRouter()


@router.post("/generate-project")
def generate_project(data: dict = Body(...)):

    id_v1_project_school = insert_new_project_school(data)
    print(id_v1_project_school)

    job = q.enqueue(generate_bim, data, id_v1_project_school, job_timeout=150)

    update_status_job_project(
        id=id_v1_project_school, status="processing", job_id=job.id
    )

    return {"job_id": job.id, "project_id": id_v1_project_school}


from rq.exceptions import NoSuchJobError


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        # 1. Intentar buscar el trabajo en Redis
        job = Job.fetch(job_id, connection=redis_conn)

    except NoSuchJobError:
        # Si el ID no existe en Redis, devolvemos un 404 limpio
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El job con ID '{job_id}' no fue encontrado o ya expiró.",
        )
    except ConnectionError:
        # Si Redis se cayó o no conecta
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar al servicio de mensajería (Redis).",
        )
    except Exception as e:
        # Cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado al consultar el job: {str(e)}",
        )

    # 2. Controlar el estado interno del Job por si falló la tarea de fondo
    job_status = job.get_status()

    # Si el trabajo falló, es buena práctica avisar al frontend por qué falló
    if job_status == "failed":
        return {
            "id": job.id,
            "status": job_status,
            "error": job.exc_info,  # Contiene el traceback del error en el worker
        }

    # 3. Respuesta exitosa (en progreso o finalizado)
    return {
        "id": job.id,
        "status": job_status,
        "result": job.result if job.is_finished else None,
    }


@router.get("/project/{project_id}", status_code=status.HTTP_200_OK)
def get_project(project_id: int):
    project_data = get_project_by_id(project_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return {"status": "success", "data": project_data}


@router.get(
    "/project/pdf/{project_id}", 
    status_code=status.HTTP_200_OK,
    response_model=ProjectPDFResponse
    )
def get_project_pdf_url(project_id: int):
    project_data = get_project_by_id(project_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    return {
        "status": "success",
        "url_pdf": project_data["url_pdf"] if "url_pdf" in project_data else None,
    }


@router.get("/project-render/{item_id}", response_class=HTMLResponse)
def get_project_render(item_id: int, render: str):
    project_data = get_project_by_id(item_id)

    # If the project doesn't exist, return a proper 404 error
    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {item_id} not found",
        )
    vertices = project_data.get("vertices", [])
    vertices = json.loads(vertices) if isinstance(vertices, str) else vertices

    if render == "3d":
        fig_3d = render_3d(vertices)
        html = wrap_plotly_figure_in_html(fig_3d)
        return HTMLResponse(content=html)

    elif render == "2d":
        vertices = datos_to_shapely(vertices)
        vertices_for_nivel = render_2d_shapely_automatico_regex(vertices)

        html_all_niveles = ""
        for nivel, grafico in vertices_for_nivel.items():
            html = wrap_plotly_figure_in_html(grafico)
            html_all_niveles += html

        return HTMLResponse(content=html_all_niveles)

    elif render == "render ia":
        fig_3d = render_3d(vertices)
        ruta_3d = save_render_image(fig_3d, tipo="3d")
        print(f"Render 3D guardado en: {ruta_3d}")

        service = GeminiNanoBananaService(api_key=os.getenv("GEMINI_API_KEY"))

        print("Generando render con IA...")

        result = service.generate_architecture_render(images_path=[ruta_3d])

        if result.get("success") and result.get("binary_image"):
            # Tomamos la primera imagen generada de la lista
            image_bytes = result["binary_image"]

            # Convertimos los bytes a una cadena Base64
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # Construimos un HTML limpio para mostrar el resultado
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Render Generado</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f9;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        text-align: center;
                        max-width: 90%;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 4px;
                        margin-top: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Resultado del Render de Arquitectura</h2>
                    <img src="data:image/png;base64,{base64_image}" alt="Render de Arquitectura">
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content, status_code=200)

    return {"status": "success", "data": vertices}


# @router.get("/project/generate-proinvierte/{project_id}", status_code=status.HTTP_200_OK)
# def generate_pdf_for_proinvierte(project_id : int):
#     project_data = get_project_by_id(project_id)

#     if not project_data:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Project with id {project_id} not found"
#         )

#     vertices = project_data.get("vertices", [])
#     vertices = json.loads(vertices) if isinstance(vertices, str) else vertices

#     # 1. Definimos el nombre del archivo (para usar el mismo en todos lados)
#     nombre_archivo_step = f"plane_{project_id}.step"

#     file_step_project = descargar_archivo_de_s3(nombre_archivo_step, bucket_name="plaindes")

#     with open(nombre_archivo_step, "wb") as f:
#         f.write(file_step_project.getvalue())

#     nombre_archivo_pdf = f"plane_{project_id}.pdf"
#     exportar_niveles_a_pdf(nombre_archivo_step, pdf_salida=f"plane_{project_id}.pdf")

#     file_bytes = obtener_archivo_en_binario(nombre_archivo_pdf)
#     archivo_binario_stream = io.BytesIO(file_bytes)

#     url_resultado = subir_archivo_a_s3(
#         archivo_binario=archivo_binario_stream,
#         nombre_archivo=nombre_archivo_pdf,
#         bucket_name="plaindes"
#     )

#     return {
#         "status": "success",
#         "url_pdf": url_resultado,
#         "id_project": project_id
#     }


@router.get(
    "/project/generate-proinvierte/{project_id}", status_code=status.HTTP_200_OK
)
def generate_pdf_for_proinvierte(project_id: int):
    project_data = get_project_by_id(project_id)

    if not project_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Definición de nombres de archivos locales
    nombre_archivo_step = f"plane_{project_id}.step"
    nombre_archivo_pdf = f"plane_{project_id}.pdf"
    bucket_name = "plaindes"

    try:
        # 1. Intentar descargar el archivo STEP desde S3
        try:
            file_step_project = descargar_archivo_de_s3(
                nombre_archivo_step, bucket_name=bucket_name
            )
        except ClientError as e:
            if (
                e.response["Error"]["Code"] == "404"
                or e.response["Error"]["Code"] == "NoSuchKey"
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El archivo CAD '{nombre_archivo_step}' no existe en el bucket de S3.",
                )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error al conectar con AWS S3 para descargar el archivo: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inesperado al obtener archivo de S3: {str(e)}",
            )

        # 2. Intentar escribir el archivo STEP en el disco duro local
        try:
            with open(nombre_archivo_step, "wb") as f:
                f.write(file_step_project.getvalue())
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error de permisos o espacio en disco al guardar el archivo STEP: {str(e)}",
            )

        # 3. Intentar procesar y generar el PDF
        try:
            exportar_niveles_a_pdf(nombre_archivo_step, pdf_salida=nombre_archivo_pdf)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El motor de geometría falló al procesar el STEP o generar el PDF: {str(e)}",
            )

        # 4. Intentar leer el PDF generado localmente
        try:
            file_bytes = obtener_archivo_en_binario(nombre_archivo_pdf)
            archivo_binario_stream = io.BytesIO(file_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No se pudo leer el archivo PDF generado en el sistema local: {str(e)}",
            )

        # 5. Intentar subir el PDF final a S3
        try:
            url_resultado = subir_archivo_a_s3(
                archivo_binario=archivo_binario_stream,
                nombre_archivo=nombre_archivo_pdf,
                bucket_name=bucket_name,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"El PDF se generó pero no se pudo subir a AWS S3: {str(e)}",
            )

        try:
            update_url_pdf_project(project_id, url_resultado)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar la URL del PDF en la base de datos: {str(e)}",
            )

        # Si todo sale bien, retornamos la respuesta exitosa
        return {"status": "success", "url_pdf": url_resultado, "id_project": project_id}

    finally:
        # Borra los archivos locales para mantener el servidor limpio.
        if os.path.exists(nombre_archivo_step):
            try:
                os.remove(nombre_archivo_step)
            except Exception:
                pass  # Evita interrumpir si el sistema operativo bloqueó el archivo un milisegundo

        if os.path.exists(nombre_archivo_pdf):
            try:
                os.remove(nombre_archivo_pdf)
            except Exception:
                pass


@router.get("/projects", status_code=status.HTTP_200_OK)
def get_allproject():
    project_data = get_all_project()

    return {"status": "success", "data": project_data}
