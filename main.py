from typing import Union
from src.auth.middleware import verify_token
from fastapi import APIRouter, FastAPI, Request
from src.auto_plano.route import router as project_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.middleware("http")(verify_token)

router_v1 = APIRouter(prefix="/api/v1")

router_v1.include_router(project_router)

app.include_router(router_v1)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router_v1.get("/perfil")
async def get_perfil(request: Request):
    # Accedemos al ID que el middleware rescató del JWT
    current_user_id = request.state.user_id
    return {
        "mensaje": "Ruta protegida alcanzada",
        "id_user": current_user_id
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
