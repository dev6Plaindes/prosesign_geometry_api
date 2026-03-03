from fastapi import APIRouter
from typing import Union

router = APIRouter(prefix="/calcule")

@router.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
