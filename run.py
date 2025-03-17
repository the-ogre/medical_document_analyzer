#!/usr/bin/env python3
"""
Startup script for the Medical Document Analyzer application
"""

import os
import sys
import argparse
import logging
import uvicorn
from pathlib import Path

def setup_environment():
    """Set up the environment for the application"""
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Medical Document Analyzer")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                        help="Logging level")
    parser.add_argument("--check", action="store_true", help="Check system dependencies and exit")
    parser.add_argument("--download-models", action="store_true", help="Download models and exit")
    parser.add_argument("--ocr-engine", choices=["tesseract", "paddle"], 
                        help="Override OCR engine from .env")
    parser.add_argument("--llm-backend", choices=["ollama", "llamacpp"], 
                        help="Override LLM backend from .env")
    
    return parser.parse_args()

def configure_logging(log_level):
    """Configure logging for the application"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

def check_dependencies():
    """Check system dependencies"""
    from medical_analyzer.services.ocr import check_ocr_dependencies
    
    print("\n" + "=" * 60)
    print(" System Dependency Check ".center(60, "="))
    print("=" * 60)
    
    # Check OCR dependencies
    print("\nChecking OCR dependencies:")
    ocr_issues = check_ocr_dependencies()
    
    if ocr_issues:
        print("  ❌ OCR issues found:")
        for issue in ocr_issues:
            print(f"    • {issue}")
    else:
        print("  ✅ OCR dependencies OK")
    
    # Check LLM backend
    print("\nChecking LLM backend:")
    from medical_analyzer.core.config import settings
    
    if settings.LLM_BACKEND == "ollama":
        import subprocess
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            print(f"  ✅ Ollama is installed")
            print("    Available models:")
            if result.stdout:
                for line in result.stdout.splitlines()[1:]:  # Skip header
                    if line.strip():
                        print(f"      • {line.split()[0]}")
            else:
                print("      No models found")
        except FileNotFoundError:
            print("  ❌ Ollama not found in PATH")
            print("    Install from: https://ollama.ai/download")
    elif settings.LLM_BACKEND == "llamacpp":
        try:
            # Check if models exist
            from pathlib import Path
            models_dir = Path(settings.MODELS_DIR)
            summary_model_path = models_dir / settings.LLAMACPP_SUMMARY_MODEL
            analyzer_model_path = models_dir / settings.LLAMACPP_ANALYZER_MODEL
            
            print(f"  Checking LlamaCpp models in: {models_dir}")
            if summary_model_path.exists():
                print(f"  ✅ Summary model found: {settings.LLAMACPP_SUMMARY_MODEL}")
            else:
                print(f"  ❌ Summary model not found: {settings.LLAMACPP_SUMMARY_MODEL}")
            
            if analyzer_model_path.exists():
                print(f"  ✅ Analyzer model found: {settings.LLAMACPP_ANALYZER_MODEL}")
            else:
                print(f"  ❌ Analyzer model not found: {settings.LLAMACPP_ANALYZER_MODEL}")
        except Exception as e:
            print(f"  ❌ Error checking LlamaCpp models: {e}")
    
    print("\n" + "=" * 60)
    
def download_models():
    """Download models"""
    from medical_analyzer.services.llm import download_models as dl_models
    
    print("\n" + "=" * 60)
    print(" Model Download ".center(60, "="))
    print("=" * 60 + "\n")
    
    try:
        dl_models()
        print("\n✅ Model download process completed\n")
    except Exception as e:
        print(f"\n❌ Error downloading models: {e}\n")
    
    print("=" * 60)

def main():
    """Main entry point"""
    # Set up environment
    setup_environment()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging
    configure_logging(args.log_level)
    
    # Set environment variables from command line arguments
    if args.ocr_engine:
        os.environ["OCR_ENGINE"] = args.ocr_engine
    
    if args.llm_backend:
        os.environ["LLM_BACKEND"] = args.llm_backend
    
    # Import here to ensure environment variables are set
    from medical_analyzer.core.config import settings
    
    # Handle special commands
    if args.check:
        check_dependencies()
        return 0
    
    if args.download_models:
        download_models()
        return 0
    
    # Show banner
    print("\n" + "=" * 60)
    print(" Medical Document Analyzer ".center(60, "="))
    print("=" * 60)
    print(f" OCR Engine: {settings.OCR_ENGINE}".ljust(60))
    print(f" LLM Backend: {settings.LLM_BACKEND}".ljust(60))
    print("=" * 60 + "\n")
    
    # Start the server
    print(f"Starting server at http://{args.host}:{args.port}")
    uvicorn.run(
        "medical_analyzer.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level.lower()
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())