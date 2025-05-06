from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from backend.models.submission import Submission
from backend.utils.s3 import save_submission_s3
router = APIRouter()

@router.post("/", tags=["Submissions"])
async def submit_data(submission: Submission):
    # Now `submission` is a properly validated object with structured command data
    s3_path = save_submission_s3(submission)

    return JSONResponse(content={
        "status": "success",
        "s3_path": s3_path,
        "message": "Submission received",
        "dog": submission.dog_name,
        "commands_count": sum(len(trial.commands) for trial in submission.trials)
    })