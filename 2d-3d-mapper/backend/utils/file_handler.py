"""
File handling utilities
"""

import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime


class FileHandler:
    """File management utilities"""
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self.maps_dir = os.path.join(upload_dir, 'maps')
        self.models_dir = os.path.join(upload_dir, 'models')
        
        os.makedirs(self.maps_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
    
    def save_file(self, file, file_id: str, filename: str) -> str:
        """Save uploaded file
        
        Args:
            file: File object
            file_id: Unique file ID
            filename: Original filename
        
        Returns:
            Path to saved file
        """
        # Create subdirectory for this file
        file_dir = os.path.join(self.maps_dir, file_id)
        os.makedirs(file_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(file_dir, filename)
        file.save(filepath)
        
        return filepath
    
    def get_file_path(self, file_id: str) -> str:
        """Get path to saved file"""
        file_dir = os.path.join(self.maps_dir, file_id)
        
        if not os.path.exists(file_dir):
            return None
        
        # Return first file in directory
        files = os.listdir(file_dir)
        if files:
            return os.path.join(file_dir, files[0])
        
        return None
    
    def get_model_path(self, model_id: str, format: str) -> str:
        """Get path to 3D model"""
        return os.path.join(self.models_dir, f"{model_id}.{format}")
    
    def get_file_info(self, filepath: str) -> dict:
        """Get file information"""
        if not os.path.exists(filepath):
            return None
        
        # Get dimensions
        image = cv2.imread(filepath)
        if image is not None:
            height, width = image.shape[:2]
        else:
            height, width = 0, 0
        
        # Get file size
        size = os.path.getsize(filepath)
        
        return {
            'dimensions': (width, height),
            'size': size,
            'modified': datetime.fromtimestamp(os.path.getmtime(filepath))
        }
