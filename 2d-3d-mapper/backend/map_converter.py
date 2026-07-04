"""
Core 2D to 3D Map Conversion Engine
"""

import numpy as np
import cv2
from PIL import Image
import logging
from typing import Dict, Tuple, Optional
import os
import trimesh
from scipy.ndimage import gaussian_filter
from scipy.spatial import Delaunay

logger = logging.getLogger(__name__)


class MapTo3DConverter:
    """Main converter class for 2D to 3D map conversion"""
    
    def __init__(self, output_dir: str = './models'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def convert(self, input_path: str, model_id: str,
                scale: float = 1.0,
                exaggeration: float = 2.0,
                resolution: int = 256,
                output_format: str = 'glb',
                smooth: bool = False,
                apply_colors: bool = True,
                decimation: float = 1.0) -> Dict:
        """Convert 2D map to 3D model
        
        Args:
            input_path: Path to 2D map image
            model_id: Unique model identifier
            scale: Horizontal scaling factor
            exaggeration: Vertical exaggeration factor
            resolution: Output resolution (mesh density)
            output_format: Output 3D format (glb, gltf, obj, ply, stl)
            smooth: Apply smoothing to heightmap
            apply_colors: Apply original colors to mesh
            decimation: Mesh decimation ratio (0-1)
        
        Returns:
            Dictionary with mesh information
        """
        logger.info(f"Starting conversion: {input_path}")
        
        try:
            # Load image
            image = cv2.imread(input_path)
            if image is None:
                raise ValueError(f"Cannot load image: {input_path}")
            
            # Resize to specified resolution
            image_resized = cv2.resize(image, (resolution, resolution))
            
            # Generate heightmap
            heightmap = self._generate_heightmap(
                image_resized,
                scale=scale,
                exaggeration=exaggeration,
                smooth=smooth
            )
            
            # Create mesh from heightmap
            vertices, faces, colors = self._create_mesh(
                heightmap,
                image_resized,
                apply_colors=apply_colors
            )
            
            # Create trimesh object
            mesh = trimesh.Trimesh(
                vertices=vertices,
                faces=faces,
                vertex_colors=colors if apply_colors else None
            )
            
            # Apply decimation if specified
            if decimation < 1.0:
                target_count = int(len(mesh.vertices) * decimation)
                mesh = mesh.simplify_quadric_mesh_simplification(
                    target_count=target_count
                )
            
            # Calculate normals
            mesh.fix_normals()
            
            # Export mesh
            output_path = os.path.join(self.output_dir, f"{model_id}.{output_format}")
            
            if output_format == 'glb':
                mesh.export(output_path, file_type='glb')
            elif output_format == 'gltf':
                mesh.export(output_path, file_type='gltf')
            elif output_format == 'obj':
                mesh.export(output_path, file_type='obj')
            elif output_format == 'ply':
                mesh.export(output_path, file_type='ply')
            elif output_format == 'stl':
                mesh.export(output_path, file_type='stl')
            else:
                raise ValueError(f"Unsupported format: {output_format}")
            
            # Get file size
            file_size = os.path.getsize(output_path)
            
            logger.info(f"Conversion complete: {model_id}, vertices: {len(vertices)}, faces: {len(faces)}")
            
            return {
                'file_size': file_size,
                'vertices': len(vertices),
                'faces': len(faces),
                'output_path': output_path
            }
        
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise
    
    def _generate_heightmap(self, image: np.ndarray,
                           scale: float = 1.0,
                           exaggeration: float = 2.0,
                           smooth: bool = False) -> np.ndarray:
        """Generate heightmap from image
        
        Args:
            image: Input image (BGR)
            scale: Horizontal scaling
            exaggeration: Vertical exaggeration
            smooth: Apply Gaussian smoothing
        
        Returns:
            Heightmap array
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Normalize to 0-1 range
        heightmap = gray.astype(np.float32) / 255.0
        
        # Apply exaggeration
        heightmap = heightmap * exaggeration
        
        # Apply smoothing if requested
        if smooth:
            heightmap = gaussian_filter(heightmap, sigma=1.0)
        
        return heightmap
    
    def _create_mesh(self, heightmap: np.ndarray,
                     image: np.ndarray,
                     apply_colors: bool = True) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
        """Create 3D mesh from heightmap
        
        Args:
            heightmap: Height values (0-1)
            image: Original image for coloring
            apply_colors: Whether to apply colors from image
        
        Returns:
            Tuple of (vertices, faces, colors)
        """
        h, w = heightmap.shape
        
        # Create vertices
        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        xx, yy = np.meshgrid(x, y)
        
        # Stack into vertices array
        vertices = np.column_stack([xx.ravel(), yy.ravel(), heightmap.ravel()])
        
        # Create faces using grid triangulation
        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                # First triangle
                v1 = i * w + j
                v2 = i * w + j + 1
                v3 = (i + 1) * w + j
                faces.append([v1, v2, v3])
                
                # Second triangle
                v1 = i * w + j + 1
                v2 = (i + 1) * w + j + 1
                v3 = (i + 1) * w + j
                faces.append([v1, v2, v3])
        
        faces = np.array(faces, dtype=np.uint32)
        
        # Get colors from image if requested
        colors = None
        if apply_colors:
            # Resize image to match heightmap resolution
            image_resized = cv2.resize(image, (w, h))
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
            # Flatten to match vertices
            colors = image_rgb.reshape(-1, 3)
        
        return vertices, faces, colors
    
    def analyze_map(self, input_path: str) -> Dict:
        """Analyze 2D map properties
        
        Args:
            input_path: Path to map image
        
        Returns:
            Analysis results dictionary
        """
        try:
            image = cv2.imread(input_path)
            if image is None:
                raise ValueError(f"Cannot load image: {input_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate statistics
            min_val = np.min(gray)
            max_val = np.max(gray)
            mean_val = np.mean(gray)
            std_val = np.std(gray)
            
            # Detect edges for terrain complexity
            edges = cv2.Canny(gray, 50, 150)
            edge_ratio = np.sum(edges > 0) / edges.size
            
            analysis = {
                'min_elevation': int(min_val),
                'max_elevation': int(max_val),
                'mean_elevation': int(mean_val),
                'std_elevation': int(std_val),
                'terrain_complexity': float(edge_ratio),
                'dimensions': image.shape[:2],
                'file_size': os.path.getsize(input_path)
            }
            
            return analysis
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise
