from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ResumeDataSchema(BaseModel):
    name: Optional[str] = None
    skills: List[str] = []
    experience_years: float = 0.0
    education: List[str] = []
    tools: List[str] = []
    job_roles: List[str] = []
    error: Optional[str] = None

class MatchRequest(BaseModel):
    job_description: str
    min_score: float = 0.0

class MatchResult(BaseModel):
    filename: str
    score: float
    raw_distance: float
    # New AI Scoring fields
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    ai_explanation: str = ""

class MatchResponse(BaseModel):
    matches: List[MatchResult]

class UploadResponse(BaseModel):
    filename: str
    message: str
    extracted_data: ResumeDataSchema
