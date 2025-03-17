"""
Main application entry point for the Medical Document Analyzer
"""

import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from pathlib import Path
import sys

from medical_analyzer.api.routes import router
from medical_analyzer.core.config import settings
from medical_analyzer.services.ocr import check_ocr_dependencies
from medical_analyzer.services.llm import download_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create required directories if they don't exist
static_dir = Path(settings.STATIC_DIR)
data_dir = Path(settings.DATA_DIR)
models_dir = Path(settings.MODELS_DIR)
for directory in [static_dir, data_dir, models_dir]:
    directory.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Medical Document Analyzer",
    description="API for analyzing medical documents using Open Source LLMs and LangGraph",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API routes
app.include_router(router)

# Add endpoint for checking system status
@app.get("/system-status")
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
    
    # Return the system status
    if status["warnings"]:
        return JSONResponse(
            status_code=200 if status["status"] == "ok" else 207,
            content=status
        )
    return status

@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup"""
    logger.info("Starting Medical Document Analyzer")
    
    # Check OCR dependencies
    ocr_issues = check_ocr_dependencies()
    if ocr_issues:
        for issue in ocr_issues:
            logger.warning(f"OCR Issue: {issue}")
    
    # Download/check LLM models
    try:
        download_models()
    except Exception as e:
        logger.error(f"Error initializing LLM models: {e}")
        
    logger.info("Initialization complete")

def main():
    """Entry point for the application when run from command line"""
    host = "0.0.0.0"
    port = 8000
    
    # Show banner
    print("\n" + "=" * 60)
    print(" Medical Document Analyzer ".center(60, "="))
    print("=" * 60)
    print(f" OCR Engine: {settings.OCR_ENGINE}".ljust(60))
    print(f" LLM Backend: {settings.LLM_BACKEND}".ljust(60))
    print("=" * 60 + "\n")
    
    # Check for any critical issues
    ocr_issues = check_ocr_dependencies()
    if ocr_issues:
        print("WARNING: OCR dependency issues detected:")
        for issue in ocr_issues:
            print(f" - {issue}")
        print()
    
    try:
        print(f"Starting server at http://{host}:{port}")
        uvicorn.run("medical_analyzer.app:app", host=host, port=port, reload=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)

if __name__ == "__main__":
    main()