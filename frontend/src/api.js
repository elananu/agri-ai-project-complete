const BASE_URL = import.meta.env.VITE_API_URL || '';

export async function detectImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/api/detect`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Detection failed' }));
    throw new Error(err.detail || 'Detection failed');
  }
  return res.json();
}

export async function fetchHistory(limit = 20) {
  const res = await fetch(`${BASE_URL}/api/history?limit=${limit}`);
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${BASE_URL}/api/stats`);
  return res.json();
}

export async function fetchWeather() {
  const res = await fetch(`${BASE_URL}/api/weather`);
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/api/health`);
  return res.json();
}