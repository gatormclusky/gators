# 2D to 3D Map Converter

A comprehensive tool that converts 2D maps into 3D visualizations with terrain modeling, elevation data, and interactive 3D exploration.

## Features

- **2D Map Input**
  - Support for various image formats (PNG, JPG, TIFF, GeoTIFF)
  - Georeferenced map support
  - Custom map uploads
  - Batch processing

- **3D Conversion Techniques**
  - Elevation data extraction from color/greyscale maps
  - Heightmap generation from grayscale intensity
  - Terrain mesh creation using Delaunay triangulation
  - Texture mapping with original 2D map
  - Normal map generation for realistic shading

- **3D Visualization**
  - WebGL-based real-time 3D rendering
  - Interactive camera controls (pan, zoom, rotate)
  - Adjustable lighting and shadows
  - Wireframe/solid/textured rendering modes
  - Terrain coloring and material properties

- **Advanced Features**
  - DEM (Digital Elevation Model) support
  - Custom scaling and exaggeration factors
  - Water body detection and rendering
  - Vegetation classification
  - Export to multiple 3D formats (OBJ, GLB, GLTF)
  - Height profile analysis
  - Slope calculation and visualization

- **Performance**
  - GPU-accelerated rendering
  - LOD (Level of Detail) optimization
  - Memory-efficient processing
  - Real-time interaction

## Technology Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **GDAL/OGR** - Geospatial data handling
- **OpenCV** - Image processing
- **NumPy/SciPy** - Numerical computing
- **Pillow** - Image manipulation
- **Rasterio** - Raster data processing
- **Trimesh** - 3D mesh operations

### Frontend
- **Three.js** - 3D WebGL rendering
- **React 18+** - UI framework
- **TailwindCSS** - Styling
- **Babylon.js** (optional) - Alternative 3D engine
- **Cesium.js** (optional) - Geographic visualization

## Installation

### Backend Setup

```bash
# Navigate to backend
cd 2d-3d-mapper/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install GDAL (required for geospatial data)
# On Ubuntu/Debian:
sudo apt-get install gdal-bin libgdal-dev

# On macOS:
brew install gdal

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
echo "FLASK_ENV=development" > .env
echo "MAX_FILE_SIZE=104857600" >> .env  # 100MB

# Run development server
flask run
```

### Frontend Setup

```bash
cd 2d-3d-mapper/frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Quick Start

### Upload and Convert a Map

```bash
# Upload a 2D map image
curl -X POST http://localhost:5000/api/maps/upload \
  -F "file=@map.png" \
  -F "type=elevation"

# Response includes map ID for conversion

# Convert to 3D
curl -X POST http://localhost:5000/api/maps/{map_id}/convert3d \
  -H "Content-Type: application/json" \
  -d '{
    "scale": 1.0,
    "exaggeration": 2.0,
    "resolution": 256,
    "format": "glb"
  }'
```

### Python API Usage

```python
from map_converter import MapTo3DConverter

# Initialize converter
converter = MapTo3DConverter()

# Load 2D map
map_2d = converter.load_map('elevation_map.png')

# Generate heightmap
heightmap = converter.generate_heightmap(map_2d, scale=1.0, exaggeration=2.0)

# Create 3D mesh
mesh = converter.create_mesh(heightmap, resolution=512)

# Apply textures
textured_mesh = converter.apply_texture(mesh, map_2d)

# Export to 3D format
converter.export_mesh(textured_mesh, 'output.glb')
```

## API Endpoints

### POST /api/maps/upload
Upload a 2D map image

**Parameters:**
- `file` (required): Image file (PNG, JPG, TIFF, GeoTIFF)
- `type` (required): Map type ('elevation', 'satellite', 'terrain', 'custom')
- `metadata` (optional): Additional map metadata (GeoJSON)

**Response:**
```json
{
  "status": "success",
  "map_id": "map_uuid_123",
  "filename": "map.png",
  "dimensions": [2048, 2048],
  "type": "elevation"
}
```

### POST /api/maps/{map_id}/convert3d
Convert 2D map to 3D

**Parameters:**
- `scale` (optional): Horizontal scale factor (default: 1.0)
- `exaggeration` (optional): Vertical exaggeration (default: 2.0)
- `resolution` (optional): Output resolution (default: 256, max: 4096)
- `format` (optional): Output format ('glb', 'gltf', 'obj', 'ply', 'stl')
- `colors` (optional): Apply terrain coloring
- `smooth` (optional): Apply Laplacian smoothing
- `decimation` (optional): Mesh decimation ratio (0-1)

**Response:**
```json
{
  "status": "success",
  "model_id": "model_uuid_123",
  "format": "glb",
  "file_size": 5242880,
  "vertices": 262144,
  "faces": 524288,
  "preview_url": "/api/models/model_uuid_123/preview"
}
```

### GET /api/maps/{map_id}/preview
Get preview image of 2D map

### GET /api/models/{model_id}/download
Download 3D model in specified format

### POST /api/maps/{map_id}/analyze
Analyze map properties

**Response:**
```json
{
  "min_elevation": 0,
  "max_elevation": 3500,
  "mean_elevation": 1200,
  "terrain_slopes": { "gentle": 45, "moderate": 35, "steep": 20 },
  "water_coverage": 5,
  "vegetation_coverage": 40
}
```

### POST /api/maps/batch-convert
Batch convert multiple maps

**Parameters:**
- `files` (required): Array of file objects
- `conversion_params` (optional): Shared conversion parameters

## Configuration

### Environment Variables (.env)

```bash
# Server
FLASK_ENV=development
PORT=5000

# File Upload
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_FOLDER=./uploads

# 3D Conversion
DEFAULT_RESOLUTION=256
MAX_RESOLUTION=4096
DEFAULT_EXAGGERATION=2.0

# Processing
USE_GPU=true
NUM_WORKERS=4
```

## Map Types

### Elevation Maps
- Grayscale intensity represents elevation
- Higher values = higher elevation
- Supports GeoTIFF with embedded georeferencing

### Satellite Maps
- RGB color imagery
- Derives elevation from terrain color codes
- Better for visual output

### Terrain Maps
- Topographic maps with contour lines
- Specialized contour extraction algorithms

### Custom Maps
- User-defined color-to-elevation mapping
- Custom scaling and interpretation

## Conversion Techniques

### Heightmap Generation
1. Load 2D map image
2. Convert to grayscale or extract color channel
3. Normalize pixel values to elevation range
4. Apply optional smoothing and filtering
5. Create heightmap texture

### Mesh Creation
1. Generate regular grid from heightmap
2. Apply Delaunay triangulation for optimization
3. Add terrain details via bump mapping
4. Apply LOD for performance
5. Calculate normals for lighting

### Texture Mapping
1. Stretch original 2D map to 3D mesh
2. Handle seams and wraparound
3. Apply material properties
4. Generate normal maps
5. Add specular information

## Export Formats

- **GLB** (Binary GLTF) - Recommended, smallest file size
- **GLTF** (JSON + Binary) - Standard 3D format
- **OBJ** - Widely compatible, ASCII format
- **PLY** (Polygon File) - Point cloud compatible
- **STL** - 3D printing ready
- **FBX** - Game engine compatible

## Performance Considerations

- **Resolution**: Higher resolution = more detail but slower processing
- **GPU Processing**: Enabled by default for faster conversion
- **LOD (Level of Detail)**: Automatically applied for real-time rendering
- **Decimation**: Reduces polygon count while maintaining visual quality
- **Streaming**: Large models streamed for faster loading

## File Structure

```
2d-3d-mapper/
├── README.md
├── backend/
│   ├── app.py
│   ├── map_converter.py          # Core conversion logic
│   ├── terrain_generator.py      # Terrain mesh generation
│   ├── image_processor.py        # Image processing utilities
│   ├── mesh_optimizer.py         # Mesh optimization
│   ├── routes/
│   │   ├── maps.py
│   │   ├── conversion.py
│   │   └── export.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── file_handler.py
│   │   └── error_handler.py
│   ├── requirements.txt
│   ├── .env.example
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── MapUploader.jsx
│   │   │   ├── ConversionSettings.jsx
│   │   │   ├── Viewer3D.jsx
│   │   │   ├── Preview.jsx
│   │   │   └── AnalysisPanel.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Editor.jsx
│   │   │   └── History.jsx
│   │   ├── hooks/
│   │   │   ├── useMapConverter.js
│   │   │   └── useFileUpload.js
│   │   ├── utils/
│   │   │   └── three-helpers.js
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── .env.example
├── docker-compose.yml
└── docs/
    ├── API.md
    ├── USAGE.md
    └── EXAMPLES.md
```

## Example Conversions

### Topographic Map to 3D Terrain
```python
converter.convert_topographic_map(
    'topo_map.png',
    scale=1.0,
    exaggeration=3.0,
    contour_interval=100
)
```

### Satellite Image to 3D Landscape
```python
converter.convert_satellite_image(
    'satellite.tiff',
    derive_elevation=True,
    color_from_original=True,
    resolution=512
)
```

### Custom 2D Map with Color Mapping
```python
color_mapping = {
    'blue': (0, 100),      # Ocean depth
    'green': (100, 500),   # Lowlands
    'brown': (500, 2000),  # Highlands
    'white': (2000, 4000)  # Mountains
}

converter.convert_with_color_mapping(
    'map.png',
    color_mapping=color_mapping
)
```

## Supported Input Formats

- **Images**: PNG, JPG/JPEG, TIFF, BMP, WebP
- **Geospatial**: GeoTIFF, HDF5, NetCDF
- **Point Clouds**: LAS, LAZ, XYZ
- **Maps**: Mapbox GL JSON, GeoJSON

## Output Formats

- **3D Models**: GLB, GLTF, OBJ, PLY, STL, FBX
- **Textures**: PNG, JPEG (normal maps, diffuse, specular)
- **Data**: JSON (mesh data, metadata)

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Small maps (256x256): <1 second
- Medium maps (1024x1024): 2-5 seconds
- Large maps (4096x4096): 10-30 seconds
- GPU acceleration recommended for large maps

## License

MIT License

## Contributing

Contributions welcome! See CONTRIBUTING.md

## Support

For issues and questions, open an issue on GitHub.
