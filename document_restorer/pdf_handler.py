"""
PDF document handling and processing.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
import logging

try:
    from pdf2image import convert_from_path, pil_to_cv2
except ImportError:
    raise ImportError("pdf2image is required. Install with: pip install pdf2image")

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow is required. Install with: pip install Pillow")

import numpy as np
from PyPDF2 import PdfWriter, PdfReader
import cv2

logger = logging.getLogger(__name__)


class PDFHandler:
    """Handle PDF conversion and reconstruction."""
    
    def __init__(self, dpi: int = 300):
        """Initialize PDF handler.
        
        Args:
            dpi: Resolution for PDF to image conversion
        """
        self.dpi = dpi
    
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to images.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of images (numpy arrays)
        """
        try:
            pil_images = convert_from_path(pdf_path, dpi=self.dpi)
            images = [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in pil_images]
            logger.info(f"Converted {len(images)} pages from {pdf_path}")
            return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise
    
    def images_to_pdf(self, images: List[np.ndarray], output_path: str, 
                      quality: int = 95) -> None:
        """Convert images to PDF.
        
        Args:
            images: List of images (numpy arrays)
            output_path: Path to save PDF
            quality: Image quality (0-100)
        """
        try:
            # Convert numpy arrays to PIL Images
            pil_images = []
            for img in images:
                # Convert BGR to RGB for PIL
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_img)
                # Convert to RGB mode if necessary
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                pil_images.append(pil_img)
            
            # Save as PDF
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            pil_images[0].save(
                output_path,
                save_all=True,
                append_images=pil_images[1:],
                quality=quality
            )
            
            logger.info(f"Saved {len(images)} pages to PDF: {output_path}")
        except Exception as e:
            logger.error(f"Error converting images to PDF: {e}")
            raise
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """Get PDF metadata and info.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            reader = PdfReader(pdf_path)
            return {
                'num_pages': len(reader.pages),
                'metadata': reader.metadata,
                'is_encrypted': reader.is_encrypted,
            }
        except Exception as e:
            logger.error(f"Error reading PDF info: {e}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF (if available).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
