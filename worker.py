from rq import SimpleWorker, Queue
from redis_conn import redis_conn

queue = Queue(
    "prodesign:bim:school",
    connection=redis_conn
)

worker = SimpleWorker(
    [queue],
    connection=redis_conn
)

print("🚀 Worker BIM iniciado...")
worker.work()