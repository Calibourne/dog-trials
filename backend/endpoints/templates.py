from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/", tags=["Templates"])
async def get_templates():
    return JSONResponse(content={"templates": ["sit", "stay", "come"]})
