import logging
import os
import os
from typing import List, Optional
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Output structure for the scoring agent
class AIScoreResult(BaseModel):
    match_score: float = Field(description="Relevance score between 0 and 100")
    matched_skills: List[str] = Field(description="Skills from the resume that match the job description")
    missing_skills: List[str] = Field(description="Key skills required by the job that are missing in the resume")
    reasoning: str = Field(description="Short natural language explanation of the score")

class ScoringService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if self.api_key:
            if os.getenv("GOOGLE_API_KEY"):
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", 
                    temperature=0, 
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    max_retries=6
                )
            else:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
                
            self.structured_llm = self.llm.with_structured_output(AIScoreResult)
        else:
            self.llm = None

    def score_candidate(self, resume_data: dict, job_description: str) -> AIScoreResult:
        """
        Compares a candidate's structured data against a job description.
        """
        # Fallback Logic (Local Scoring)
        def local_score():
            logger.warning("Using local keyword scoring fallback.")
            jd_lower = job_description.lower()
            skills = resume_data.get('skills', [])
            matched = [s for s in skills if s.lower() in jd_lower]
            missing = [s for s in skills if s.lower() not in jd_lower]
            
            # Simple score: (matched / total_skills) * 100
            # Plus some base points for vector similarity context (handled in matching_service, but we mimic here)
            score = 0
            if skills:
                score = (len(matched) / len(skills)) * 100
            
            return AIScoreResult(
                match_score=round(score, 2),
                matched_skills=matched,
                missing_skills=missing,
                reasoning="Scored using local keyword matching (AI Service Error: Check Console Logs)."
            )

        if not self.llm:
            return local_score()

        try:
            # Prepare a concise summary of the candidate for the prompt
            candidate_summary = f"""
            Name: {resume_data.get('name', 'Unknown')}
            Skills: {', '.join(resume_data.get('skills', []))}
            Experience: {resume_data.get('experience_years', 0)} years
            Current Role: {', '.join(resume_data.get('job_roles', []))}
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert HR AI. specificy. You must evaluate the candidate for the job based on: Skill match (highest weight), Experience relevance, Tool/technology overlap, Role similarity."),
                ("user", "JOB DESCRIPTION:\n{job_description}\n\nCANDIDATE PROFILE:\n{candidate_summary}")
            ])
            
            chain = prompt | self.structured_llm
            result = chain.invoke({"job_description": job_description, "candidate_summary": candidate_summary})
            
            return result
        except Exception as e:
            logger.error(f"Error evaluating candidate: {e}")
            # On 429 or other errors, use fallback
            return local_score()

scoring_service = ScoringService()
