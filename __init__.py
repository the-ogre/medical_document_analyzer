"""
Medical Document Analyzer Package
"""

__version__ = "1.0.0"

# Add imports to make modules accessible
from medical_analyzer.core.config import settings
from medical_analyzer.core.processor import process_medical_document
from medical_analyzer.core.llm_chain import create_medical_analysis_chain
from medical_analyzer.services.ocr import extract_text_from_pdf, check_ocr_dependencies
from medical_analyzer.services.llm import get_llm_client, download_models
from medical_analyzer.services.document import DocumentService