"""
Main document restoration interface with PDF and image support.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
import logging
from concurrent.futures import ThreadPoolExecutor

import pytesseract
from PIL import Image

from .core import ImageRestorer
from .pdf_handler import PDFHandler

logger = logging.getLogger(__name__)


class DocumentRestorer:
    """Main document restoration interface."""
    
    def __init__(self, config: Optional[dict] = None, dpi: int = 300):
        """Initialize document restorer.
        
        Args:
            config: Restoration configuration
            dpi: DPI for PDF processing
        """
        self.image_restorer = ImageRestorer(config)
        self.pdf_handler = PDFHandler(dpi=dpi)
        self.config = config or {}
    
    def restore(self, input_path: str, output_path: str, 
                techniques: Optional[List[str]] = None,
                quality: int = 95) -> dict:
        """Restore a single image document.
        
        Args:
            input_path: Path to input image
            output_path: Path to save restored image
            techniques: Restoration techniques to apply
            quality: Output quality (0-100)
            
        Returns:
            Dictionary with restoration info
        """
        if techniques is None:
            techniques = ['denoise', 'contrast', 'sharpen', 'binarize']
        
        try:
            # Load image
            image = self.image_restorer.load_image(input_path)
            logger.info(f"Loaded image: {input_path}")
            
            # Apply restoration
            restored = self.image_restorer.restore(image, techniques)
            
            # Save restored image
            self.image_restorer.save_image(restored, output_path, quality=quality)
            
            return {
                'status': 'success',
                'input': input_path,
                'output': output_path,
                'techniques': techniques,
            }
        except Exception as e:
            logger.error(f"Error restoring image: {e}")
            return {
                'status': 'error',
                'input': input_path,
                'error': str(e),
            }
    
    def restore_pdf(self, input_path: str, output_path: str,
                    techniques: Optional[List[str]] = None,
                    quality: int = 95) -> dict:
        """Restore a PDF document.
        
        Args:
            input_path: Path to input PDF
            output_path: Path to save restored PDF
            techniques: Restoration techniques to apply
            quality: Output quality (0-100)
            
        Returns:
            Dictionary with restoration info
        """
        if techniques is None:
            techniques = ['denoise', 'contrast', 'sharpen']
        
        try:
            # Convert PDF to images
            logger.info(f"Converting PDF to images: {input_path}")
            images = self.pdf_handler.pdf_to_images(input_path)
            
            # Restore each page
            restored_images = []
            for i, image in enumerate(images):
                logger.info(f"Restoring page {i+1}/{len(images)}")
                restored = self.image_restorer.restore(image, techniques)
                restored_images.append(restored)
            
            # Convert back to PDF
            logger.info(f"Creating restored PDF: {output_path}")
            self.pdf_handler.images_to_pdf(restored_images, output_path, quality=quality)
            
            return {
                'status': 'success',
                'input': input_path,
                'output': output_path,
                'pages_processed': len(images),
                'techniques': techniques,
            }
        except Exception as e:
            logger.error(f"Error restoring PDF: {e}")
            return {
                'status': 'error',
                'input': input_path,
                'error': str(e),
            }
    
    def extract_text(self, image_path: str, language: str = 'eng') -> str:
        """Extract text from restored image using OCR.
        
        Args:
            image_path: Path to image file
            language: OCR language code (default: 'eng')
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=language)
            logger.info(f"Extracted text from {image_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str, language: str = 'eng') -> str:
        """Extract text from restored PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            language: OCR language code
            
        Returns:
            Extracted text from all pages
        """
        try:
            images = self.pdf_handler.pdf_to_images(pdf_path)
            full_text = ""
            
            for i, image in enumerate(images):
                pil_image = Image.fromarray(image[:, :, ::-1])
                text = pytesseract.image_to_string(pil_image, lang=language)
                full_text += f"\n--- Page {i+1} ---\n{text}"
            
            logger.info(f"Extracted text from {len(images)} pages")
            return full_text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""


class BatchRestorer:
    """Batch process multiple documents."""
    
    def __init__(self, num_workers: int = 4, config: Optional[dict] = None):
        """Initialize batch restorer.
        
        Args:
            num_workers: Number of parallel workers
            config: Restoration configuration
        """
        self.num_workers = num_workers
        self.restorer = DocumentRestorer(config)
    
    def restore_directory(self, input_dir: str, output_dir: str,
                         file_types: Optional[List[str]] = None,
                         techniques: Optional[List[str]] = None,
                         preserve_structure: bool = True) -> dict:
        """Restore all documents in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            file_types: File types to process (e.g., ['pdf', 'jpg', 'png'])
            techniques: Restoration techniques
            preserve_structure: Keep directory structure in output
            
        Returns:
            Summary of batch processing
        """
        if file_types is None:
            file_types = ['pdf', 'jpg', 'jpeg', 'png', 'tiff']
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find all matching files
        files_to_process = []
        for file_type in file_types:
            files_to_process.extend(input_path.rglob(f'*.{file_type}'))
            files_to_process.extend(input_path.rglob(f'*.{file_type.upper()}'))
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        results = {
            'total': len(files_to_process),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        # Process files
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            
            for input_file in files_to_process:
                if preserve_structure:
                    relative_path = input_file.relative_to(input_path)
                    output_file = output_path / relative_path
                else:
                    output_file = output_path / input_file.name
                
                output_file = output_file.with_suffix('.png')
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                if input_file.suffix.lower() == '.pdf':
                    future = executor.submit(
                        self.restorer.restore_pdf,
                        str(input_file),
                        str(output_file.with_suffix('.pdf')),
                        techniques
                    )
                else:
                    future = executor.submit(
                        self.restorer.restore,
                        str(input_file),
                        str(output_file),
                        techniques
                    )
                futures.append(future)
            
            # Collect results
            for future in futures:
                try:
                    result = future.result()
                    results['details'].append(result)
                    if result['status'] == 'success':
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    logger.error(f"Error in batch processing: {e}")
                    results['failed'] += 1
        
        logger.info(f"Batch processing complete: {results['successful']} successful, {results['failed']} failed")
        return results
