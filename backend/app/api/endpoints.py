from fastapi import APIRouter, UploadFile, File, HTTPException
import zipfile
import io
from typing import List
from app.services.resume_parser import extract_text_from_pdf
from app.services.vector_db import vector_db
from app.services.matching_service import matching_service
from app.api.schemas import MatchRequest, MatchResponse, UploadResponse
from app.database import get_db
from app.models import Candidate
from sqlalchemy.orm import Session
from fastapi import Depends

router = APIRouter()

@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Read file content
    try:
        # Pypdf reads from a file-like object
        # SpooledTemporaryFile is supported by extract_text_from_pdf logic
        content = await file.read() # Reading to memory might be heavy for large files, but resumes are small.
        # However, PdfReader needs a stream. 
        # Ideally we pass file.file directly if possible, but let's wrap contents in BytesIO if needed
        # or just pass file.file (which behaves like a file).
        
        # Reset cursor just in case
        await file.seek(0)
        
        text = await extract_text_from_pdf(file.file)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
            
        # Extract structured data
        from app.services.extraction_service import extraction_service
        extracted_data = extraction_service.extract_data(text)
        
        # Store in Vector DB with structured data in metadata
        metadata = {"filename": file.filename}
        if extracted_data:
            # Flatten or store as JSON string if DB has issues, but InMemory/FAISS simple docstore handles dicts fine.
            metadata.update(extracted_data)

        vector_db.add_resume(text, metadata)
        
        # Save to SQLite
        try:
            db_candidate = Candidate(
                filename=file.filename,
                name=extracted_data.get("name", "Unknown"),
                email=extracted_data.get("job_roles", [""])[0] if "@" in extracted_data.get("job_roles", [""])[0] else None, # Hacky fallback from extraction service
                experience_years=extracted_data.get("experience_years", 0.0),
                skills=extracted_data.get("skills", []),
                education=extracted_data.get("education", []),
                extracted_text=text
            )
            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)
        except Exception as db_e:
            # If duplicate filename or other db error, log but don't fail the upload
            print(f"DB Save Error: {db_e}")
            db.rollback()
        
        return UploadResponse(
            filename=file.filename,
            message="Resume uploaded and processed successfully.",
            extracted_data=extracted_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-zip", response_model=List[UploadResponse])
async def upload_zip(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP files are supported.")
    
    import logging
    logger = logging.getLogger(__name__)

    try:
        content = await file.read()
        zip_buffer = io.BytesIO(content)
        
        results = []
        from app.services.extraction_service import extraction_service
        
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                # Skip directories and non-PDFs
                if filename.lower().endswith(".pdf") and not filename.startswith("__MACOSX") and not filename.endswith("/"):
                    try:
                        with zip_ref.open(filename) as pdf_file:
                            pdf_bytes = pdf_file.read()
                            pdf_io = io.BytesIO(pdf_bytes)
                            
                            # Extract text
                            text = await extract_text_from_pdf(pdf_io)
                            
                            if text:
                                # Extract Data
                                extracted_data = extraction_service.extract_data(text)
                                
                                # Index in Vector DB
                                metadata = {"filename": filename}
                                if extracted_data:
                                    metadata.update(extracted_data)
                                vector_db.add_resume(text, metadata)
                                
                                # Save to DB
                                try:
                                    db_cand = Candidate(
                                        filename=filename,
                                        name=extracted_data.get("name", "Unknown"),
                                        experience_years=extracted_data.get("experience_years", 0),
                                        skills=extracted_data.get("skills", []),
                                        education=extracted_data.get("education", []),
                                        extracted_text=text
                                    )
                                    db.add(db_cand)
                                    db.commit()
                                except Exception as dbe:
                                    print(f"DB Batch Error: {dbe}")
                                    db.rollback()
                                
                                results.append(UploadResponse(
                                    filename=filename,
                                    message="Processed successfully",
                                    extracted_data=extracted_data
                                ))
                            else:
                                logger.warning(f"Empty text for file: {filename}")
                    except Exception as inner_e:
                        logger.error(f"Error processing matching file {filename} in zip: {inner_e}")
                        continue
                        
        return results

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file.")
    except Exception as e:
        logger.error(f"Batch upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")

@router.post("/match-job", response_model=MatchResponse)
async def match_job(request: MatchRequest):
    results = matching_service.match_jobs(request.job_description, request.min_score)
    return MatchResponse(matches=results)

@router.get("/candidates")
def get_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    # Simple manual dictionary conversion or use Pydantic schema
    return [
        {
            "id": c.id,
            "name": c.name,
            "filename": c.filename,
            "skills": c.skills,
            "experience_years": c.experience_years,
            "extracted_data": {
                "name": c.name,
                "skills": c.skills,
                "experience_years": c.experience_years
            }
        }
        for c in candidates
    ]
