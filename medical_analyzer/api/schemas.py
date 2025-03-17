"""
Pydantic schemas for request and response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union, Any

class ErrorResponse(BaseModel):
    """Error response schema"""
    status: str = "error"
    message: str

class AnalysisResponse(BaseModel):
    """Medical document analysis response schema"""
    status: str = "success"
    analysis: str = Field(..., description="Detailed analysis of the medical document")
    summary: str = Field(..., description="Summary of key findings")
    validation: str = Field(..., description="Validation of diagnosis and treatment")
    graph: str = Field(..., description="Base64 encoded graph visualization")
    llm_backend: Optional[str] = Field(None, description="LLM backend used for processing")
    ocr_engine: Optional[str] = Field(None, description="OCR engine used for processing")

class ComponentStatus(BaseModel):
    """System component status"""
    status: str = Field(..., description="Status of the component (ok, warning, error)")
    engine: Optional[str] = Field(None, description="Engine used by the component")
    backend: Optional[str] = Field(None, description="Backend used by the component")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details about the component")

class SystemStatusResponse(BaseModel):
    """System status response schema"""
    status: str = Field(..., description="Overall system status (ok, warning, error)")
    components: Dict[str, ComponentStatus] = Field(..., description="Status of individual components")
    warnings: List[str] = Field(default_factory=list, description="Warning messages if any")

class FileInfo(BaseModel):
    """Information about a file in the data directory"""
    filename: str = Field(..., description="Name of the file")
    path: str = Field(..., description="Path to the file")
    size: int = Field(..., description="Size of the file in bytes")
    created: str = Field(..., description="Creation timestamp")
    modified: str = Field(..., description="Last modification timestamp")

class FilesListResponse(BaseModel):
    """Response for listing files"""
    status: str = "success"
    files: List[FileInfo] = Field(..., description="List of files")
    count: int = Field(..., description="Total number of files")