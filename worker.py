from rq import SimpleWorker, Queue
from redis_conn import redis_conn

queue_school = Queue("prodesign:bim:school", connection=redis_conn)
queue_pdf = Queue("prodesign:bim:pdf", connection=redis_conn)

# Import worker functions so RQ can resolve them
from src.bim.services import run_pdf_pipeline
from src.bim.pipeline.project_school.create.main_pipeline import generate_project_school_pipeline

worker = SimpleWorker(
    [queue_school, queue_pdf],
    connection=redis_conn
)

print("Worker BIM iniciado (school + pdf)...")
worker.work()