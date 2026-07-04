import React from 'react';

function ConversionSettings({ settings, onSettingsChange }) {
  const handleChange = (key, value) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  return (
    <div className="settings-panel">
      <div className="setting-group">
        <label>Vertical Exaggeration</label>
        <input
          type="range"
          min="0.5"
          max="5"
          step="0.1"
          value={settings.exaggeration}
          onChange={(e) => handleChange('exaggeration', parseFloat(e.target.value))}
        />
        <span className="value">{settings.exaggeration.toFixed(1)}x</span>
      </div>

      <div className="setting-group">
        <label>Horizontal Scale</label>
        <input
          type="range"
          min="0.1"
          max="2"
          step="0.1"
          value={settings.scale}
          onChange={(e) => handleChange('scale', parseFloat(e.target.value))}
        />
        <span className="value">{settings.scale.toFixed(1)}x</span>
      </div>

      <div className="setting-group">
        <label>Resolution</label>
        <select
          value={settings.resolution}
          onChange={(e) => handleChange('resolution', parseInt(e.target.value))}
        >
          <option value={256}>Low (256x256)</option>
          <option value={512}>Medium (512x512)</option>
          <option value={1024}>High (1024x1024)</option>
          <option value={2048}>Very High (2048x2048)</option>
        </select>
      </div>

      <div className="setting-group">
        <label>Output Format</label>
        <select
          value={settings.format}
          onChange={(e) => handleChange('format', e.target.value)}
        >
          <option value="glb">GLB (Recommended)</option>
          <option value="gltf">GLTF</option>
          <option value="obj">OBJ</option>
          <option value="ply">PLY</option>
          <option value="stl">STL</option>
        </select>
      </div>

      <div className="setting-group checkbox">
        <input
          type="checkbox"
          id="smooth"
          checked={settings.smooth}
          onChange={(e) => handleChange('smooth', e.target.checked)}
        />
        <label htmlFor="smooth">Apply Smoothing</label>
      </div>

      <div className="setting-group checkbox">
        <input
          type="checkbox"
          id="colors"
          checked={settings.colors}
          onChange={(e) => handleChange('colors', e.target.checked)}
        />
        <label htmlFor="colors">Apply Original Colors</label>
      </div>
    </div>
  );
}

export default ConversionSettings;
