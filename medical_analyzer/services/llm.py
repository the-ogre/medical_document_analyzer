"""
Document handling services
"""

import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
from typing import List
import uuid

from medical_analyzer.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class DocumentService:
    """Service for handling document operations"""
    
    @staticmethod
    def save_uploaded_file(file_content, original_filename: str) -> str:
        """
        Save an uploaded file to the data directory
        
        Args:
            file_content: File content (bytes)
            original_filename: Original filename
            
        Returns:
            str: Path to the saved file
        """
        # Create a unique filename to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{timestamp}_{unique_id}_{original_filename}"
        
        file_path = Path(settings.DATA_DIR) / safe_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
            
        logger.info(f"Saved uploaded file to {file_path}")
        return str(file_path)
    
    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """
        Validate if file has an allowed extension
        
        Args:
            filename: Filename to validate
            
        Returns:
            bool: True if extension is allowed, False otherwise
        """
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        return extension in settings.ALLOWED_EXTENSIONS
    
    @staticmethod
    def list_saved_files() -> List[dict]:
        """
        List all saved files in the data directory
        
        Returns:
            List[dict]: List of file information dictionaries
        """
        files = []
        data_dir = Path(settings.DATA_DIR)
        
        for file_path in data_dir.glob("*.*"):
            if file_path.suffix.lstrip('.').lower() in settings.ALLOWED_EXTENSIONS:
                # Get file stats
                stats = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": stats.st_size,
                    "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                })
                
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    
    @staticmethod
    def delete_file(filename: str) -> bool:
        """
        Delete a file from the data directory
        
        Args:
            filename: Name of file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            file_path = Path(settings.DATA_DIR) / filename
            
            # Security check - ensure the file is within the data directory
            if settings.DATA_DIR not in str(file_path.resolve()):
                logger.error(f"Attempted to delete file outside data directory: {filename}")
                return False
            
            # Delete the file if it exists
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {filename}")
                return True
            else:
                logger.warning(f"File not found: {filename}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {str(e)}")
            return False