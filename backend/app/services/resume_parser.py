import logging
from pypdf import PdfReader
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def extract_text_from_pdf(file_file) -> Optional[str]:
    """
    Extracts text from a PDF file-like object.
    
    Args:
        file_file: A file-like object (BytesIO or SpooledTemporaryFile) containing the PDF data.
        
    Returns:
        Extracted text as a single string, or None if extraction fails.
    """
    try:
        reader = PdfReader(file_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return None
