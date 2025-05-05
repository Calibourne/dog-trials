from fastapi import FastAPI
from backend.endpoints import templates, submissions, report, health

app = FastAPI()

app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
app.include_router(report.router, prefix="/report", tags=["Report"])
app.include_router(health.router, prefix="/health", tags=["Health"])
