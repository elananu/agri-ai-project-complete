import React from 'react';

export default function StatsPanel({ stats, weather }) {
  return (
    <div className="card stats-card">
      <h2>3. Track & Improve</h2>
      <div className="stats-grid">
        <StatBox label="Total Scans" value={stats?.total_scans ?? 0} icon="📊" />
        <StatBox label="Diseases Detected" value={stats?.total_diseases ?? 0} icon="🦠" />
        <StatBox label="Pests Detected" value={stats?.total_pests ?? 0} icon="🐛" />
        <StatBox label="Weeds Detected" value={stats?.total_weeds ?? 0} icon="🌿" />
      </div>

      {weather && (
        <div className="weather-box">
          <h3>Field Conditions</h3>
          <div className="weather-grid">
            <span>🌡️ {weather.temperature_c}°C</span>
            <span>💧 {weather.humidity_pct}%</span>
            <span>🌬️ {weather.wind_kmh} km/h</span>
            <span>🌧️ {weather.rainfall_mm} mm</span>
          </div>
          <span className="muted">{weather.condition}</span>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value, icon }) {
  return (
    <div className="stat-box">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}
