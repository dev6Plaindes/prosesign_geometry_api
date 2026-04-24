from typing import Union
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Asegúrate de que estas importaciones sean correctas en tu estructura de carpetas
from src.auth.middleware import verify_token
from src.auto_plano.route import router as project_router
from src.motor.route import router as route_motor

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
router_v1 = APIRouter(prefix="/api/v1")
router_v2 = APIRouter(prefix="/api/v2") # Cambiado a v2 para diferenciar

router_v1.include_router(project_router)
router_v2.include_router(route_motor)

# 4. Inclusión de Routers (Llamadas independientes)
app.include_router(router_v1)
app.include_router(router_v2)

@router_v1.get("/perfil")
async def get_perfil(request: Request):
    # El middleware debe setear request.state.user_id
    current_user_id = getattr(request.state, "user_id", None)
    return {
        "mensaje": "Ruta protegida alcanzada",
        "id_user": current_user_id
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}