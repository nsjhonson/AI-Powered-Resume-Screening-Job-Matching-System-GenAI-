from fastapi import FastAPI
from app.services.scoring_service import scoring_service
from app.api.endpoints import router as api_router
from pydantic import BaseModel
from typing import List, Optional
from app.database import engine, Base

class QuestionRequest(BaseModel):
    job_description: str
    resume_data: dict

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-Powered Resume Screening System")

from app.api.auth import router as auth_router

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")

@app.post("/api/generate-questions")
async def generate_questions(request: QuestionRequest):
    return scoring_service.generate_interview_questions(request.resume_data, request.job_description)

@app.post("/api/estimate-salary")
async def estimate_salary(request: QuestionRequest):
    return scoring_service.estimate_salary(request.resume_data, request.job_description)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI-Powered Resume Screening System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
