"""
Configuration settings for the Medical Document Analyzer
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    # Base directories
    BASE_DIR: str = str(Path(__file__).parent.parent.parent)
    STATIC_DIR: str = os.path.join(BASE_DIR, "medical_analyzer/static")
    DATA_DIR: str = os.path.join(BASE_DIR, "medical_analyzer/data")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "medical_analyzer/templates")
    MODELS_DIR: str = os.path.join(BASE_DIR, "medical_analyzer/models")
    
    # Model settings - open source SLMs
    LLM_BACKEND: str = os.getenv("LLM_BACKEND", "ollama")  # 'ollama' or 'llamacpp'
    
    # Ollama model names
    OLLAMA_SUMMARY_MODEL: str = "phi3"  # Phi-3 Mini
    OLLAMA_ANALYZER_MODEL: str = "llama3"  # Llama 3 8B
    
    # LlamaCpp model paths (relative to MODELS_DIR)
    LLAMACPP_SUMMARY_MODEL: str = "phi-3-mini-4k-instruct.Q4_K_M.gguf"
    LLAMACPP_ANALYZER_MODEL: str = "llama-3-8b-instruct.Q4_K_M.gguf"
    
    # LlamaCpp model parameters
    LLAMACPP_THREADS: int = os.getenv("LLAMACPP_THREADS", 4)
    LLAMACPP_CONTEXT_SIZE: int = os.getenv("LLAMACPP_CONTEXT_SIZE", 4096)
    
    # OCR settings
    OCR_ENGINE: str = os.getenv("OCR_ENGINE", "tesseract")  # 'tesseract' or 'paddle'
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "tesseract")
    
    # File settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list = ["pdf"]
    FILE_RETENTION_DAYS: int = 1
    
    # Performance settings
    BATCH_SIZE: int = 4  # For processing large documents in chunks
    
    class Config:
        env_file = ".env"

settings = Settings()