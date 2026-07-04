"""
2D to 3D Map Converter - Flask Application
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from werkzeug.utils import secure_filename
import uuid

from map_converter import MapTo3DConverter
from utils.validators import validate_file, validate_conversion_params
from utils.error_handler import handle_error, APIError
from utils.file_handler import FileHandler

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 104857600))  # 100MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'tif', 'geotiff', 'bmp', 'webp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize services
converter = MapTo3DConverter()
file_handler = FileHandler(UPLOAD_FOLDER)

logger = logging.getLogger(__name__)


# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': '2d-3d-mapper',
        'version': '1.0.0'
    }), 200


@app.route('/api/maps/upload', methods=['POST'])
def upload_map():
    """Upload a 2D map image
    
    Form Parameters:
        file: Image file (required)
        type: Map type - 'elevation', 'satellite', 'terrain', 'custom' (required)
        metadata: JSON metadata (optional)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            raise APIError('No file provided', 400)
        
        file = request.files['file']
        map_type = request.form.get('type', 'elevation')
        
        if not file or file.filename == '':
            raise APIError('No file selected', 400)
        
        # Validate file
        if not validate_file(file, ALLOWED_EXTENSIONS):
            raise APIError('Invalid file type. Allowed: ' + ', '.join(ALLOWED_EXTENSIONS), 400)
        
        # Save file
        filename = secure_filename(file.filename)
        map_id = str(uuid.uuid4())
        filepath = file_handler.save_file(file, map_id, filename)
        
        # Get file info
        file_info = file_handler.get_file_info(filepath)
        
        logger.info(f"Map uploaded: {map_id}, type: {map_type}, size: {file_info['size']}")
        
        return jsonify({
            'status': 'success',
            'map_id': map_id,
            'filename': filename,
            'type': map_type,
            'dimensions': file_info['dimensions'],
            'size': file_info['size']
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return handle_error(APIError('File upload failed', 500))


@app.route('/api/maps/<map_id>/preview', methods=['GET'])
def get_map_preview(map_id):
    """Get preview of uploaded map"""
    try:
        filepath = file_handler.get_file_path(map_id)
        
        if not filepath or not os.path.exists(filepath):
            raise APIError('Map not found', 404)
        
        return send_file(filepath, mimetype='image/png')
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return handle_error(APIError('Failed to get preview', 500))


@app.route('/api/maps/<map_id>/convert3d', methods=['POST'])
def convert_to_3d(map_id):
    """Convert 2D map to 3D model
    
    JSON Parameters:
        scale: Horizontal scale (optional, default: 1.0)
        exaggeration: Vertical exaggeration (optional, default: 2.0)
        resolution: Output resolution (optional, default: 256)
        format: Output format - glb, gltf, obj, ply, stl (optional, default: glb)
        smooth: Apply smoothing (optional, default: false)
        colors: Apply terrain coloring (optional, default: true)
    """
    try:
        params = request.get_json() or {}
        
        # Validate parameters
        if not validate_conversion_params(params):
            raise APIError('Invalid conversion parameters', 400)
        
        # Get map file
        filepath = file_handler.get_file_path(map_id)
        
        if not filepath or not os.path.exists(filepath):
            raise APIError('Map not found', 404)
        
        # Conversion parameters
        scale = float(params.get('scale', 1.0))
        exaggeration = float(params.get('exaggeration', 2.0))
        resolution = int(params.get('resolution', 256))
        output_format = params.get('format', 'glb').lower()
        smooth = params.get('smooth', False)
        colors = params.get('colors', True)
        decimation = float(params.get('decimation', 1.0))
        
        logger.info(f"Converting map {map_id}: resolution={resolution}, exaggeration={exaggeration}")
        
        # Convert map
        model_id = str(uuid.uuid4())
        mesh_info = converter.convert(
            filepath,
            model_id,
            scale=scale,
            exaggeration=exaggeration,
            resolution=resolution,
            output_format=output_format,
            smooth=smooth,
            apply_colors=colors,
            decimation=decimation
        )
        
        return jsonify({
            'status': 'success',
            'model_id': model_id,
            'format': output_format,
            'file_size': mesh_info['file_size'],
            'vertices': mesh_info['vertices'],
            'faces': mesh_info['faces'],
            'download_url': f'/api/models/{model_id}/download',
            'preview_url': f'/api/models/{model_id}/preview'
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return handle_error(APIError('3D conversion failed', 500))


@app.route('/api/models/<model_id>/download', methods=['GET'])
def download_model(model_id):
    """Download 3D model
    
    Query Parameters:
        format: Model format (optional, default: glb)
    """
    try:
        format = request.args.get('format', 'glb')
        filepath = file_handler.get_model_path(model_id, format)
        
        if not filepath or not os.path.exists(filepath):
            raise APIError('Model not found', 404)
        
        logger.info(f"Downloading model: {model_id}, format: {format}")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=f'map_model_{model_id}.{format}'
        )
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return handle_error(APIError('Download failed', 500))


@app.route('/api/maps/<map_id>/analyze', methods=['POST'])
def analyze_map(map_id):
    """Analyze map properties"""
    try:
        filepath = file_handler.get_file_path(map_id)
        
        if not filepath or not os.path.exists(filepath):
            raise APIError('Map not found', 404)
        
        logger.info(f"Analyzing map: {map_id}")
        
        analysis = converter.analyze_map(filepath)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return handle_error(APIError('Map analysis failed', 500))


@app.route('/api/maps/batch-upload', methods=['POST'])
def batch_upload():
    """Batch upload multiple maps"""
    try:
        if 'files' not in request.files:
            raise APIError('No files provided', 400)
        
        files = request.files.getlist('files')
        map_type = request.form.get('type', 'elevation')
        
        results = []
        
        for file in files:
            if not file or file.filename == '':
                continue
            
            if not validate_file(file, ALLOWED_EXTENSIONS):
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': 'Invalid file type'
                })
                continue
            
            try:
                filename = secure_filename(file.filename)
                map_id = str(uuid.uuid4())
                filepath = file_handler.save_file(file, map_id, filename)
                file_info = file_handler.get_file_info(filepath)
                
                results.append({
                    'filename': filename,
                    'map_id': map_id,
                    'status': 'success',
                    'dimensions': file_info['dimensions'],
                    'size': file_info['size']
                })
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })
        
        return jsonify({
            'status': 'success',
            'uploaded': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error']),
            'results': results
        }), 200
    
    except APIError as e:
        return handle_error(e)
    except Exception as e:
        logger.error(f"Batch upload error: {str(e)}")
        return handle_error(APIError('Batch upload failed', 500))


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
