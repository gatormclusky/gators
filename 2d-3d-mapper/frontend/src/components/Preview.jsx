import React from 'react';

function Preview({ title, mapId, dimensions }) {
  return (
    <div className="preview">
      <div className="preview-header">
        <h3>{title}</h3>
        <span className="dimensions">{dimensions?.[0]} × {dimensions?.[1]}px</span>
      </div>
      <div className="preview-content">
        <img 
          src={`/api/maps/${mapId}/preview`}
          alt="Map preview"
          className="preview-image"
        />
      </div>
    </div>
  );
}

export default Preview;
