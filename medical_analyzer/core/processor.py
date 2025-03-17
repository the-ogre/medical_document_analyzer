"""
Main document processing logic
"""

from typing import Dict, Any
from pathlib import Path
import logging

from medical_analyzer.core.llm_chain import create_medical_analysis_chain
from medical_analyzer.services.ocr import extract_text_from_pdf

# Configure logging
logger = logging.getLogger(__name__)

def process_medical_document(document_path: str) -> Dict[str, Any]:
    """
    Process a medical document through the analysis pipeline
    
    Args:
        document_path: Path to the document file
        
    Returns:
        Dict containing analysis results
    """
    try:
        # Validate the file exists
        if not Path(document_path).exists():
            raise ValueError(f"Document not found at path: {document_path}")
            
        logger.info(f"Processing document: {document_path}")
        
        # Create the chain and get graph visualization
        chain, graph_viz = create_medical_analysis_chain()
        
        # Validate the document is a PDF before processing
        if not document_path.lower().endswith('.pdf'):
            raise ValueError("Only PDF documents are supported")
        
        # Process the document
        result = chain.invoke({"file_name": document_path})
        
        # Clean up result keys if needed
        analysis = result.get("analysis_result", "")
        summary = result.get("summary", "")
        validation = result.get("validation_result", "")
        
        logger.info(f"Document processed successfully: {document_path}")
        
        return {
            "analysis": analysis,
            "summary": summary,
            "validation": validation,
            "graph": graph_viz
        }
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise