from typing import Union
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Asegúrate de que estas importaciones sean correctas en tu estructura de carpetas
from src.auth.middleware import verify_token
from src.bim.route import router as route_bim

app = FastAPI()

# 1. Configuración de CORS (Se recomienda ponerlo antes de los routers)
origins = [
    "http://localhost:5199",
    "http://192.168.18.200:5199",
    "https://*.ngrok-free.app",
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Middleware de autenticación global
app.middleware("http")(verify_token)

# 3. Definición de Routers
router_v3 = APIRouter(prefix="/api/v3")

router_v3.include_router(route_bim)

# 4. Inclusión de Routers
app.include_router(router_v3)

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}