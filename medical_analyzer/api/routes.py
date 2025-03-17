"""
API routes for the Medical Document Analyzer
"""

from fastapi import APIRouter, UploadFile, File, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
from pathlib import Path
from datetime import datetime
import os
import logging

from medical_analyzer.core.config import settings
from medical_analyzer.core.processor import process_medical_document
from medical_analyzer.core.llm_chain import create_medical_analysis_chain
from medical_analyzer.api.schemas import AnalysisResponse, ErrorResponse, SystemStatusResponse
from medical_analyzer.services.document import DocumentService
from medical_analyzer.services.ocr import check_ocr_dependencies
from medical_analyzer.services.llm import download_models

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Setup templates
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# Initialize document service
document_service = DocumentService()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render home page with graph visualization"""
    # Generate the graph visualization when loading the page
    _, graph_base64 = create_medical_analysis_chain()
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "graph_base64": graph_base64,
            "llm_backend": settings.LLM_BACKEND,
            "ocr_engine": settings.OCR_ENGINE
        }
    )

@router.post(
    "/analyze-medical-document", 
    response_model=AnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Analyze uploaded medical document"""
    try:
        # Validate file extension
        if not document_service.validate_file_extension(file.filename):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Only {', '.join(settings.ALLOWED_EXTENSIONS)} files are supported"}
            )
        
        # Validate file size
        if file.size > settings.MAX_FILE_SIZE:
            max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"File size exceeds maximum allowed ({max_size_mb:.1f} MB)"}
            )
        
        # Read file content
        file_content = await file.read()
        
        # Save the file
        file_path = document_service.save_uploaded_file(file_content, file.filename)
        
        # Process the document (this can take time)
        result = process_medical_document(file_path)
        
        # Add cleanup task in the background if requested
        if background_tasks:
            # Schedule cleanup for temporary files if needed
            pass
        
        return AnalysisResponse(
            status="success",
            analysis=result["analysis"],
            summary=result["summary"],
            validation=result["validation"],
            graph=result["graph"],
            llm_backend=settings.LLM_BACKEND,
            ocr_engine=settings.OCR_ENGINE
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "An error occurred while processing the document"}
        )

@router.delete("/cleanup")
async def cleanup_old_files():
    """Clean up files older than the retention period"""
    try:
        current_time = datetime.now()
        data_dir = Path(settings.DATA_DIR)
        deleted_count = 0
        
        for file_path in data_dir.glob("*.*"):
            if file_path.suffix.lstrip('.').lower() in settings.ALLOWED_EXTENSIONS:
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days >= settings.FILE_RETENTION_DAYS:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")
                
        return JSONResponse(
            content={
                "status": "success", 
                "message": f"Cleanup completed. {deleted_count} files removed."
            }
        )
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Cleanup failed: {str(e)}"}
        )

@router.get("/system-status", response_model=SystemStatusResponse)
async def system_status():
    """Check the status of all system components"""
    status = {
        "status": "ok",
        "components": {
            "ocr": {"status": "ok", "engine": settings.OCR_ENGINE},
            "llm": {"status": "ok", "backend": settings.LLM_BACKEND}
        },
        "warnings": []
    }
    
    # Check OCR dependencies
    ocr_issues = check_ocr_dependencies()
    if ocr_issues:
        status["components"]["ocr"]["status"] = "warning"
        status["warnings"].extend(ocr_issues)
    
    # If we have serious issues, change the overall status
    if status["warnings"]:
        if any("Error" in warning for warning in status["warnings"]):
            status["status"] = "error"
        else:
            status["status"] = "warning"
    
    return SystemStatusResponse(**status)