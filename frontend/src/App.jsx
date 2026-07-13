import React, { useEffect, useState, useCallback } from 'react';
import UploadPanel from './components/UploadPanel.jsx';
import ResultsPanel from './components/ResultsPanel.jsx';
import StatsPanel from './components/StatsPanel.jsx';
import HistoryPanel from './components/HistoryPanel.jsx';
import { detectImage, fetchHistory, fetchStats, fetchWeather } from './api.js';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [weather, setWeather] = useState(null);
  const [history, setHistory] = useState([]);

  const refreshDashboard = useCallback(async () => {
    const [s, h] = await Promise.all([fetchStats(), fetchHistory(10)]);
    setStats(s);
    setHistory(h);
  }, []);

  useEffect(() => {
    refreshDashboard();
    fetchWeather().then(setWeather).catch(() => {});
  }, [refreshDashboard]);

  const handleDetect = async (file) => {
    setLoading(true);
    setError(null);
    try {
      const res = await detectImage(file);
      setResult(res);
      await refreshDashboard();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>🌾 Agri-AI: Smart Crop & Pest Detection System</h1>
        <p>AI-Powered Detection · Real-time Results · Smart Recommendations</p>
      </header>

      {error && <div className="error-banner">⚠️ {error}</div>}

      <main className="app-grid">
        <UploadPanel onDetect={handleDetect} loading={loading} />
        <ResultsPanel result={result} />
        <StatsPanel stats={stats} weather={weather} />
      </main>

      <section className="app-history">
        <HistoryPanel history={history} />
      </section>

      <footer className="app-footer">
        Built with YOLOv8 · FastAPI · React — Agri-AI Project
      </footer>
    </div>
  );
}
