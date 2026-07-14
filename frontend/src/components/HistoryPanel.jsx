import React from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

export default function HistoryPanel({ history }) {
  return (
    <div className="card history-card">
      <h2>Detection History</h2>
      {history.length === 0 && <p className="muted">No scans yet.</p>}
      <div className="history-list">
        {history.map((item) => (
          <div key={item.id} className="history-item">
            <img src={`${API_BASE}/uploads/${item.image_filename}`} alt="scan" />
            <div className="history-meta">
              <span>{new Date(item.created_at).toLocaleString()}</span>
              <span>
                🦠 {item.disease_count} · 🐛 {item.pest_count} · 🌿 {item.weed_count}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}