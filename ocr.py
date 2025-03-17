"""
OCR service for extracting text from PDF documents using open-source libraries
"""

import os
import logging
import tempfile
from pathlib import Path
import subprocess
from medical_analyzer.core.config import settings

# Try to import PDF libraries but don't fail if not installed
try:
    import pytesseract
    import pdf2image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import paddleocr
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False

try:
    import pymupdf
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF document using open-source OCR
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text content
    """
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        # First try to extract text directly without OCR
        if PYMUPDF_AVAILABLE:
            text = _extract_text_with_pymupdf(pdf_path)
            
            # If we got meaningful text, return it
            if text and len(text) > 100:  # Arbitrary threshold for "meaningful" text
                logger.info(f"Successfully extracted {len(text)} characters from PDF using PyMuPDF")
                return text
        
        # If direct extraction failed or returned minimal text, try OCR
        if settings.OCR_ENGINE == "tesseract":
            if not TESSERACT_AVAILABLE:
                raise ImportError("pytesseract and pdf2image are required for Tesseract OCR")
            text = _extract_text_with_tesseract(pdf_path)
        elif settings.OCR_ENGINE == "paddle":
            if not PADDLE_AVAILABLE:
                raise ImportError("paddleocr is required for PaddleOCR")
            text = _extract_text_with_paddleocr(pdf_path)
        else:
            raise ValueError(f"Unsupported OCR engine: {settings.OCR_ENGINE}")
        
        logger.info(f"Successfully extracted {len(text)} characters from PDF using {settings.OCR_ENGINE}")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

def _extract_text_with_pymupdf(pdf_path: str) -> str:
    """Extract text directly from PDF using PyMuPDF"""
    text_parts = []
    doc = pymupdf.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_parts.append(page.get_text())
    
    return "\n\n".join(text_parts)

def _extract_text_with_tesseract(pdf_path: str) -> str:
    """Extract text from PDF using Tesseract OCR"""
    # Set tesseract command if specified in settings
    if settings.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    # Convert PDF to images
    images = pdf2image.convert_from_path(pdf_path)
    
    # Process each image with Tesseract
    text_parts = []
    for i, image in enumerate(images):
        logger.info(f"Processing page {i+1}/{len(images)} with Tesseract")
        text = pytesseract.image_to_string(image, lang='eng')
        text_parts.append(text)
    
    return "\n\n".join(text_parts)

def _extract_text_with_paddleocr(pdf_path: str) -> str:
    """Extract text from PDF using PaddleOCR"""
    # Initialize PaddleOCR
    ocr = paddleocr.PaddleOCR(use_angle_cls=True, lang='en')
    
    # Convert PDF to images
    images = pdf2image.convert_from_path(pdf_path)
    
    # Process each image with PaddleOCR
    text_parts = []
    for i, image in enumerate(images):
        logger.info(f"Processing page {i+1}/{len(images)} with PaddleOCR")
        
        # Save image to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp:
            image_path = temp.name
            image.save(image_path, 'JPEG')
        
        # Process with PaddleOCR
        try:
            result = ocr.ocr(image_path, cls=True)
            
            # Extract text from result
            page_text = []
            for line in result:
                for word_info in line:
                    if isinstance(word_info, list) and len(word_info) >= 2:
                        # Extract text and confidence
                        text, confidence = word_info[1]
                        page_text.append(text)
            
            text_parts.append(" ".join(page_text))
        finally:
            # Clean up temporary file
            if os.path.exists(image_path):
                os.unlink(image_path)
    
    return "\n\n".join(text_parts)

def check_ocr_dependencies():
    """Check if OCR dependencies are installed and working"""
    issues = []
    
    # Check PyMuPDF
    if not PYMUPDF_AVAILABLE:
        issues.append("PyMuPDF is not installed. Install with: pip install pymupdf")
    
    # Check OCR engine dependencies
    if settings.OCR_ENGINE == "tesseract":
        if not TESSERACT_AVAILABLE:
            issues.append("Tesseract dependencies are not installed. Install with: pip install pytesseract pdf2image")
        
        # Check if tesseract binary is available
        try:
            tesseract_version = subprocess.check_output([settings.TESSERACT_CMD, "--version"], text=True)
            logger.info(f"Tesseract version: {tesseract_version.splitlines()[0] if tesseract_version else 'Unknown'}")
        except (subprocess.SubprocessError, FileNotFoundError):
            issues.append(f"Tesseract binary not found at: {settings.TESSERACT_CMD}")
            issues.append("Install Tesseract from: https://github.com/tesseract-ocr/tesseract")
    
    elif settings.OCR_ENGINE == "paddle":
        if not PADDLE_AVAILABLE:
            issues.append("PaddleOCR is not installed. Install with: pip install paddleocr")
    
    return issues