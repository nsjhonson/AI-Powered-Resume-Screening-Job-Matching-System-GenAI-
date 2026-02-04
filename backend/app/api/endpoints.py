from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import extract_text_from_pdf
from app.services.vector_db import vector_db
from app.services.matching_service import matching_service
from app.api.schemas import MatchRequest, MatchResponse, UploadResponse

router = APIRouter()

@router.post("/upload-resume", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
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
        
        return UploadResponse(
            filename=file.filename,
            message="Resume uploaded and processed successfully.",
            extracted_data=extracted_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-job", response_model=MatchResponse)
async def match_job(request: MatchRequest):
    results = matching_service.match_jobs(request.job_description, request.min_score)
    return MatchResponse(matches=results)
