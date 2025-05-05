from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/", tags=["Health"])
async def health_check():
    return JSONResponse(content={"status": "ok"})
