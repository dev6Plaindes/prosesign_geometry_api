import os
from redis import Redis
from dotenv import load_dotenv

load_dotenv()

redis_conn = Redis(
    host=os.getenv("REDIS_HOST", "redis_bim"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", "prodesign123"),
    decode_responses=False
)