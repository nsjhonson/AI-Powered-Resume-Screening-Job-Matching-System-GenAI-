import sys
import os
import asyncio
from dotenv import load_dotenv

# Ensure we can import from app
sys.path.append(os.getcwd())

load_dotenv()

from app.services.extraction_service import extraction_service

def test_extraction():
    print("Testing Extraction Service...")
    
    # Dummy resume text
    text = """
    JOHN DOE
    Software Engineer
    
    Email: john.doe@example.com
    Phone: 123-456-7890
    
    EXPERIENCE
    Software Engineer | Tech Corp | 2020 - Present
    - Built scalable APIS using Python and FastAPI.
    - Managed AWS infrastructure.
    
    SKILLS
    Python, Java, Docker, Kubernetes, SQL
    
    EDUCATION
    B.S. Computer Science | University of Tech | 2016-2020
    """
    
    print(f"Input Text (truncated): {text[:100]}...")
    
    try:
        result = extraction_service.extract_data(text)
        print("\n--- Extraction Result ---")
        print(result)
        
        if "error" in result:
            print(f"\n[FAIL] Extraction returned error: {result['error']}")
        else:
            print("\n[SUCCESS] Extraction successful.")
            
    except Exception as e:
        print(f"\n[CRITICAL FAIL] Exception during test: {e}")

if __name__ == "__main__":
    test_extraction()
