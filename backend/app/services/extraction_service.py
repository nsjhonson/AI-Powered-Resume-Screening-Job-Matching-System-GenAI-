import logging
import os
import os
from typing import Optional, List
# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the structure we want to extract
class ResumeData(BaseModel):
    name: str = Field(description="Full name of the candidate")
    skills: List[str] = Field(description="List of technical and soft skills")
    experience_years: float = Field(description="Total years of professional experience (numeric)")
    education: List[str] = Field(description="List of degrees and universities")
    tools: List[str] = Field(description="Specific tools, libraries, or frameworks used")
    job_roles: List[str] = Field(description="List of job titles or roles held")

class ExtractionService:
    def __init__(self):
        # Support both keys for flexibility, prioritize Google for now as requested
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("No API Key found (OPENAI_API_KEY or GOOGLE_API_KEY). Validation will fail.")
            self.llm = None
        else:
            # Check which key is present and initialize appropriate model
            if os.getenv("GOOGLE_API_KEY"):
                # Using 2.0-flash as confirmed by list_models
                print("--- INITIALIZING GEMINI 2.0 FLASH ---")
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", 
                    temperature=0, 
                    google_api_key=os.getenv("GOOGLE_API_KEY"),
                    max_retries=6, # Built-in retry for LangChain Google GenAI
                    request_timeout=60
                )
            else:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            
            self.structured_llm = self.llm.with_structured_output(ResumeData)

    def extract_data(self, text: str) -> Optional[dict]:
        """
        Extracts structured data from resume text using LLM.
        """
        if not self.llm:
            logger.error("Cannot extract data: OPENAI_API_KEY is missing.")
            return {
                "error": "OpenAI API Key missing. Data extraction disabled.",
                "name": "Unknown",
                "skills": [],
                "experience_years": 0.0,
                "education": [],
                "tools": [],
                "job_roles": []
            }

        try:
            # We truncate text to avoid token limits if the resume is huge, 
            # but usually resumes fit in context.
            truncated_text = text[:10000] 
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert resume parser. Extract the following information from the resume text."),
                ("user", "{text}")
            ])
            
            chain = prompt | self.structured_llm
            result = chain.invoke({"text": truncated_text})
            
            return result.dict()
            
        except Exception as e:
            logger.error(f"Error extracting data with LLM: {e}")
            
            # --- IMPROVED FALLBACK LOGIC ---
            import re
            
            # 1. Try to find Email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
            email = email_match.group(0) if email_match else "Unknown Email"
            
            # 2. Try to guess Name (First non-empty line)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            name = lines[0] if lines else "Unknown Candidate"
            
            # 3. Simple Keyword Extraction for Skills
            common_skills = ["Python", "Java", "C++", "JavaScript", "React", "Angular", "Vue", "Node.js", "Django", "FastAPI", "Flask", "SQL", "NoSQL", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Machine Learning", "Deep Learning", "NLP", "Git", "Communication", "Leadership", "Problem Solving"]
            found_skills = [skill for skill in common_skills if skill.lower() in text.lower()]
            
            return {
                "error": f"Extraction failed (using fallback): {str(e)}",
                "name": name,
                "skills": found_skills if found_skills else ["No skills found"],
                "experience_years": 0.0,
                "education": [],
                "tools": [],
                "job_roles": [email] # storing email in roles for visibility
            }

extraction_service = ExtractionService()
