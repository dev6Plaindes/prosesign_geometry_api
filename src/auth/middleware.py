from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

app = FastAPI()

async def verify_token(request: Request, call_next):
    # 1. Excluir rutas públicas (importante para que el login funcione)
    path = request.url.path
    if path in ["/api/v1/login", "/docs", "/openapi.json"]:
        return await call_next(request)

    # 2. Obtener el header Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(status_code=401, content={"detail": "Token no proporcionado"})

    try:
        # 3. Extraer el token (Bearer <token>)
        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return JSONResponse(status_code=401, content={"detail": "Formato de token inválido"})
        
        token = parts[1]

        # 4. Decodificar el payload (Aquí es donde extraemos tu 'id')
        # PyJWT verifica automáticamente la expiración (exp) si existe en el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 5. Guardar el ID en el estado de la petición para usarlo en las rutas
        request.state.user_id = payload.get("id")
        
        if request.state.user_id is None:
            return JSONResponse(status_code=401, content={"detail": "Token no contiene un ID válido"})

    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"detail": "El token ha expirado"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=401, content={"detail": "Token inválido o mal formado"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error interno: {str(e)}"})

    # 6. Continuar con la ejecución de la ruta
    return await call_next(request)