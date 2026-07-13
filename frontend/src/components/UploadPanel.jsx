import React, { useRef, useState } from 'react';

export default function UploadPanel({ onDetect, loading }) {
  const inputRef = useRef(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file) => {
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    onDetect(file);
  };

  return (
    <div className="card upload-card">
      <h2>1. Upload Crop Image</h2>
      <div
        className={`dropzone ${dragging ? 'dragging' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFile(e.dataTransfer.files?.[0]);
        }}
      >
        {preview ? (
          <img src={preview} alt="preview" className="preview-img" />
        ) : (
          <div className="dropzone-hint">
            <div className="dropzone-icon">📷</div>
            <p>Click or drag & drop a crop image</p>
            <span>JPG, PNG, WEBP</span>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>
      {loading && <div className="loading-bar">Analyzing image…</div>}
    </div>
  );
}
