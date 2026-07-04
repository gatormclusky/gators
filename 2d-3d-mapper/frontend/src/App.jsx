import React, { useState } from 'react';
import { Upload, Play, Download } from 'lucide-react';
import './App.css';
import MapUploader from './components/MapUploader';
import ConversionSettings from './components/ConversionSettings';
import Viewer3D from './components/Viewer3D';
import Preview from './components/Preview';

function App() {
  const [uploadedMap, setUploadedMap] = useState(null);
  const [converted3DModel, setConverted3DModel] = useState(null);
  const [isConverting, setIsConverting] = useState(false);
  const [conversionSettings, setConversionSettings] = useState({
    scale: 1.0,
    exaggeration: 2.0,
    resolution: 256,
    format: 'glb',
    smooth: false,
    colors: true
  });

  const handleMapUpload = (mapData) => {
    setUploadedMap(mapData);
    setConverted3DModel(null);
  };

  const handleConvert = async () => {
    if (!uploadedMap) return;

    setIsConverting(true);
    try {
      const response = await fetch(`/api/maps/${uploadedMap.map_id}/convert3d`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(conversionSettings)
      });

      if (!response.ok) throw new Error('Conversion failed');

      const data = await response.json();
      setConverted3DModel(data);
    } catch (error) {
      console.error('Conversion error:', error);
      alert('Conversion failed: ' + error.message);
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🗺️ 2D to 3D Map Converter</h1>
        <p>Transform your 2D maps into interactive 3D models</p>
      </header>

      <main className="container">
        <div className="content-grid">
          {/* Left Panel - Upload & Settings */}
          <div className="left-panel">
            <section className="section">
              <h2>Step 1: Upload 2D Map</h2>
              <MapUploader onMapUpload={handleMapUpload} />
            </section>

            {uploadedMap && (
              <>
                <section className="section">
                  <h2>Step 2: Configure Conversion</h2>
                  <ConversionSettings
                    settings={conversionSettings}
                    onSettingsChange={setConversionSettings}
                  />
                </section>

                <section className="section">
                  <h2>Step 3: Convert to 3D</h2>
                  <button
                    onClick={handleConvert}
                    disabled={isConverting}
                    className="convert-btn"
                  >
                    <Play size={20} />
                    {isConverting ? 'Converting...' : 'Convert to 3D'}
                  </button>
                </section>
              </>
            )}
          </div>

          {/* Right Panel - Preview & Viewer */}
          <div className="right-panel">
            {uploadedMap && !converted3DModel && (
              <Preview
                title="2D Map Preview"
                mapId={uploadedMap.map_id}
                dimensions={uploadedMap.dimensions}
              />
            )}

            {converted3DModel && (
              <Viewer3D model={converted3DModel} />
            )}

            {!uploadedMap && (
              <div className="empty-state">
                <Upload size={48} />
                <p>Upload a 2D map to get started</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
