from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/", tags=["Report"])
async def generate_report():
    return JSONResponse(content={"report": "Generated successfully"})
