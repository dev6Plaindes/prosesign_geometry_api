from typing import Union
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Asegúrate de que estas importaciones sean correctas en tu estructura de carpetas
from src.auth.middleware import verify_token
from src.bim.route import router as route_bim
from src.bim.repository import ensure_content_svg_column, ensure_content_pdf_column, ensure_custom_rectangle_columns

app = FastAPI()

@app.on_event("startup")
def startup():
    ensure_content_svg_column()
    ensure_content_pdf_column()
    ensure_custom_rectangle_columns()

# 1. Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5199",
        "http://192.168.18.200:5199",
        "https://prodesign.pro-invest.pe",
        "https://pyapiprodesign.pro-invest.pe",
        "https://apiprodesign.pro-invest.pe",
    ],
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