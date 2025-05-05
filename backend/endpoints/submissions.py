from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/", tags=["Submissions"])
async def submit_data(request: Request):
    data = await request.json()
    # In real usage, save to S3 or DB
    return JSONResponse(content={"message": "Submission received", "data": data})