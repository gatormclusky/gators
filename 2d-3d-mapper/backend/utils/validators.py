"""
Validation utilities
"""

def validate_file(file, allowed_extensions):
    """Validate uploaded file"""
    if not file:
        return False
    
    filename = file.filename.lower()
    ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
    
    return ext in allowed_extensions


def validate_conversion_params(params):
    """Validate conversion parameters"""
    try:
        # Validate scale
        scale = float(params.get('scale', 1.0))
        if scale <= 0:
            return False
        
        # Validate exaggeration
        exaggeration = float(params.get('exaggeration', 2.0))
        if exaggeration <= 0:
            return False
        
        # Validate resolution
        resolution = int(params.get('resolution', 256))
        if resolution < 64 or resolution > 4096:
            return False
        
        # Validate format
        format_type = params.get('format', 'glb').lower()
        if format_type not in ['glb', 'gltf', 'obj', 'ply', 'stl']:
            return False
        
        # Validate decimation
        decimation = float(params.get('decimation', 1.0))
        if decimation < 0 or decimation > 1:
            return False
        
        return True
    
    except (ValueError, TypeError):
        return False
