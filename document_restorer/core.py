"""
Core image processing
Core image processing engine with image processing and enhancement.
"""

import cv2
import numpy as np
from pathlib import Path
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class ImageRestorer:
    """Core image restoration engine."""
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize the restoration engine.
        
        Args:
            config: Configuration dictionary with restoration parameters
        """
        self.config = config or self._default_config()
        
    def _default_config(self) -> dict:
        """Get default restoration configuration."""
        return {
            'denoise_strength': 10,
            'contrast_limit': 2.0,
            'sharpening_kernel': 'unsharp',
            'bilateral_d': 9,
            'bilateral_sigma_color': 75,
            'bilateral_sigma_space': 75,
        }
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image as numpy array
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    def save_image(self, image: np.ndarray, output_path: str, quality: int = 95) -> None:
        """Save image to file.
        
        Args:
            image: Image as numpy array
            output_path: Path to save image
            quality: JPEG quality (0-100)
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.lower().endswith('.png'):
            cv2.imwrite(output_path, image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
        elif output_path.lower().endswith(('.jpg', '.jpeg')):
            cv2.imwrite(output_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        elif output_path.lower().endswith('.tiff'):
            cv2.imwrite(output_path, image)
        else:
            cv2.imwrite(output_path, image)
        
        logger.info(f"Saved image to {output_path}")
    
    def denoise(self, image: np.ndarray, strength: Optional[int] = None) -> np.ndarray:
        """Apply denoising to image.
        
        Args:
            image: Input image
            strength: Denoising strength (0-20)
            
        Returns:
            Denoised image
        """
        strength = strength or self.config['denoise_strength']
        
        # Apply bilateral filtering (edge-preserving)
        denoised = cv2.bilateralFilter(
            image,
            d=self.config['bilateral_d'],
            sigmaColor=self.config['bilateral_sigma_color'],
            sigmaSpace=self.config['bilateral_sigma_space']
        )
        
        logger.debug(f"Applied bilateral denoising (strength={strength})")
        return denoised
    
    def enhance_contrast(self, image: np.ndarray, method: str = 'clahe') -> np.ndarray:
        """Enhance contrast of image.
        
        Args:
            image: Input image
            method: Enhancement method ('clahe', 'histogram', 'levels')
            
        Returns:
            Contrast-enhanced image
        """
        if image.ndim == 3:
            # Convert BGR to LAB for better processing
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
        else:
            l = image
        
        if method == 'clahe':
            # Contrast Limited Adaptive Histogram Equalization
            clahe = cv2.createCLAHE(
                clipLimit=self.config['contrast_limit'],
                tileGridSize=(8, 8)
            )
            enhanced_l = clahe.apply(l)
        elif method == 'histogram':
            # Standard histogram equalization
            enhanced_l = cv2.equalizeHist(l)
        else:
            enhanced_l = l
        
        if image.ndim == 3:
            enhanced = cv2.merge([enhanced_l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            enhanced = enhanced_l
        
        logger.debug(f"Enhanced contrast using {method}")
        return enhanced
    
    def sharpen(self, image: np.ndarray, method: str = 'unsharp') -> np.ndarray:
        """Sharpen image.
        
        Args:
            image: Input image
            method: Sharpening method ('unsharp', 'laplacian')
            
        Returns:
            Sharpened image
        """
        if method == 'unsharp':
            # Unsharp masking
            gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
            sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        elif method == 'laplacian':
            # Laplacian sharpening
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            sharpened = cv2.convertScaleAbs(image + laplacian * 0.5)
        else:
            sharpened = image
        
        logger.debug(f"Applied {method} sharpening")
        return np.clip(sharpened, 0, 255).astype(np.uint8)
    
    def binarize(self, image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
        """Convert image to binary (black and white).
        
        Args:
            image: Input image (should be grayscale)
            method: Binarization method ('adaptive', 'otsu', 'niblack')
            
        Returns:
            Binary image
        """
        # Convert to grayscale if needed
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        if method == 'adaptive':
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        elif method == 'otsu':
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        logger.debug(f"Applied {method} binarization")
        return binary
    
    def restore(self, image: np.ndarray, techniques: List[str]) -> np.ndarray:
        """Apply a sequence of restoration techniques.
        
        Args:
            image: Input image
            techniques: List of techniques to apply in order
                       ('denoise', 'contrast', 'sharpen', 'binarize')
            
        Returns:
            Restored image
        """
        restored = image.copy()
        
        for technique in techniques:
            if technique == 'denoise':
                restored = self.denoise(restored)
            elif technique == 'contrast':
                restored = self.enhance_contrast(restored)
            elif technique == 'sharpen':
                restored = self.sharpen(restored)
            elif technique == 'binarize':
                restored = self.binarize(restored)
            else:
                logger.warning(f"Unknown restoration technique: {technique}")
        
        logger.info(f"Applied restoration techniques: {techniques}")
        return restored
