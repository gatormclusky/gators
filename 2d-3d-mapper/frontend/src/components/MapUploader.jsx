import React, { useState } from 'react';
import { Upload, AlertCircle } from 'lucide-react';
import axios from 'axios';

function MapUploader({ onMapUpload }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [mapType, setMapType] = useState('elevation');

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', mapType);

      const response = await axios.post('/api/maps/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      onMapUpload(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="uploader">
      <div className="map-type-selector">
        <label>Map Type:</label>
        <select value={mapType} onChange={(e) => setMapType(e.target.value)}>
          <option value="elevation">Elevation Map</option>
          <option value="satellite">Satellite Imagery</option>
          <option value="terrain">Terrain Map</option>
          <option value="custom">Custom Map</option>
        </select>
      </div>

      <div className="upload-area">
        <input
          type="file"
          id="file-input"
          onChange={handleFileSelect}
          accept=".png,.jpg,.jpeg,.tiff,.tif,.bmp,.webp"
          disabled={loading}
          className="file-input"
        />
        <label htmlFor="file-input" className="upload-label">
          <Upload size={32} />
          <span>{loading ? 'Uploading...' : 'Click or drag to upload'}</span>
          <small>PNG, JPG, TIFF, BMP (max 100MB)</small>
        </label>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={20} />
          {error}
        </div>
      )}
    </div>
  );
}

export default MapUploader;
