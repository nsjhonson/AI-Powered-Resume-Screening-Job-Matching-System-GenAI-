import logging
from typing import List, Dict, Any
from .vector_db import vector_db
from .scoring_service import scoring_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchingService:
    def __init__(self):
        self.vector_db = vector_db
        self.scoring_service = scoring_service

    def match_jobs(self, job_description: str, min_score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Matches a job description against stored resumes.
        First gets candidates via vector search (Retrieval), then re-scores with LLM (Analysis).
        """
        # 1. Retrieval Phase
        # Get top 5 candidates based on semantic similarity of the full text
        raw_results = self.vector_db.search_similar(job_description, k=5)
        
        matches = []
        for metadata, vector_distance in raw_results:
            # 2. Analysis Phase
            # Use the structured data we saved in metadata to perform detailed scoring
            
            # Fallback if no structured data exists
            candidate_json = metadata 
            
            # Call LLM for scoring
            score_result = self.scoring_service.score_candidate(candidate_json, job_description)
            
            # Combine results
            # We prioritize the LLM score if available, otherwise fallback to vector distance conversion
            final_score = score_result.match_score
            
            if final_score < min_score_threshold:
                continue

            result = {
                "filename": metadata.get("filename"),
                "score": final_score,
                "raw_distance": vector_distance,
                # New fields
                "matched_skills": score_result.matched_skills,
                "missing_skills": score_result.missing_skills,
                "ai_explanation": score_result.reasoning
            }
            matches.append(result)
            
        return sorted(matches, key=lambda x: x['score'], reverse=True)

matching_service = MatchingService()
