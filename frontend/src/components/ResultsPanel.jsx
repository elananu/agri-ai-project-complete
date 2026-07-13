import React, { useRef, useEffect } from 'react';

const CATEGORY_COLORS = {
  disease: '#ef4444',
  pest: '#f59e0b',
  weed: '#10b981',
  healthy: '#3b82f6',
  unknown: '#a855f7',
};

export default function ResultsPanel({ result }) {
  const canvasRef = useRef(null);
  const imgRef = useRef(null);

  useEffect(() => {
    if (!result) return;
    const img = new Image();
    img.src = result.image_url;
    img.onload = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const maxW = 520;
      const scale = Math.min(1, maxW / img.width);
      canvas.width = img.width * scale;
      canvas.height = img.height * scale;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      result.detections.forEach((det) => {
        const [x1, y1, x2, y2] = det.box;
        const color = CATEGORY_COLORS[det.category] || CATEGORY_COLORS.unknown;
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(x1 * scale, y1 * scale, (x2 - x1) * scale, (y2 - y1) * scale);
        const label = `${det.label} ${det.confidence}%`;
        ctx.font = 'bold 13px sans-serif';
        const textWidth = ctx.measureText(label).width;
        ctx.fillStyle = color;
        ctx.fillRect(x1 * scale, y1 * scale - 20, textWidth + 10, 20);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, x1 * scale + 5, y1 * scale - 5);
      });
    };
  }, [result]);

  if (!result) {
    return (
      <div className="card results-card empty-state">
        <h2>2. Detection Results</h2>
        <p className="muted">Upload an image to see AI detection results here.</p>
      </div>
    );
  }

  const detections = result.detections;
  const allHealthy = detections.length > 0 && detections.every((d) => d.category === 'healthy');

  // For an all-healthy result, summarize instead of repeating a card per leaf.
  let summary = null;
  if (allHealthy) {
    const best = detections.reduce((a, b) => (b.confidence > a.confidence ? b : a));
    const cropName = best.label.replace(/_/g, ' ');
    summary = {
      crop: cropName,
      confidence: best.confidence,
      advice: best.advice,
      count: detections.length,
    };
  }

  return (
    <div className="card results-card">
      <h2>2. Detection Results</h2>
      <span className={`mode-badge ${result.model_mode}`}>
        {result.model_mode === 'yolo' ? '🎯 Custom YOLOv8 Model' : '🔬 Real-Time CV Analysis'}
      </span>
      {result.model_mode === 'cv_heuristic' && (
        <p className="mode-note">
          Analyzing actual image pixels (color &amp; texture) to locate dark
          lesions and yellowing patches. For exact pest/disease species ID,
          train and add a custom YOLOv8 model — see README.
        </p>
      )}
      <canvas ref={canvasRef} className="result-canvas" />
      <img ref={imgRef} hidden alt="" />

      <div className="detections-list">
        {detections.length === 0 && (
          <p className="muted">No pests, diseases, or weeds detected. Crop looks clean!</p>
        )}

        {summary ? (
          <div className="detection-item risk-none summary-card">
            <div className="detection-header">
              <span className="detection-label">✅ Status: Healthy</span>
              <span className="detection-confidence">{summary.confidence}%</span>
            </div>
            <p className="advice">
              <strong>Crop:</strong> {summary.crop}
              {summary.count > 1 && ` (${summary.count} leaves detected)`}
              <br />
              <strong>Disease:</strong> None detected
              <br />
              {summary.advice}
            </p>
          </div>
        ) : (
          detections.map((det, i) => (
            <div key={i} className={`detection-item risk-${det.risk}`}>
              <div className="detection-header">
                <span className="detection-label">{det.label.replace(/_/g, ' ')}</span>
                <span className="detection-confidence">{det.confidence}%</span>
              </div>
              <span className={`category-pill ${det.category}`}>{det.category}</span>

              {det.disease_type && (
                <p className="disease-type">
                  <strong>Type:</strong> {det.disease_type}
                </p>
              )}

              {det.cause && (
                <p className="cause">
                  <strong>Cause:</strong> {det.cause}
                </p>
              )}

              <p className="advice">{det.advice}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}