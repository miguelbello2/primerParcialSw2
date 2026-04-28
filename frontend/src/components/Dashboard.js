import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function Dashboard() {
  const [stats, setStats] = useState({
    people_per_minute: 0,
    density: 0,
    mood: 'N/A',
    timestamp: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 2000); // Refresh every 2 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/results/latest`);
      const newStats = response.data;
      setStats(newStats);
      setError(null);
      
      // Update history for chart
      setHistory(prev => {
        const timeStr = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const newData = [...prev, { time: timeStr, density: newStats.density, ppm: newStats.people_per_minute }];
        return newData.slice(-15); // Keep last 15 data points
      });
    } catch (err) {
      setError('No se pudo conectar con el servidor');
      console.error('Stats fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStopAnalysis = async () => {
    try {
      await axios.post(`${API_URL}/api/stream/stop`);
      // Immediately reset local state to stop video stream
      setStats(prev => ({ ...prev, active_file_id: null }));
    } catch (err) {
      console.error('Error stopping analysis:', err);
    }
  };

  const streamUrl = stats.active_file_id 
    ? `${API_URL}/api/stream/video?filename=${encodeURIComponent(stats.active_file_id)}`
    : null;

  return (
    <div className="dashboard">
      <h2 className="page-title">Métricas de Video en Tiempo Real</h2>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-split-layout">
        <div className="dashboard-left">
          {streamUrl ? (
            <div className="dashboard-video-section">
              <div className="video-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span className="live-badge badge-live">EN VIVO</span>
                  <span className="video-filename">{stats.active_file_id}</span>
                </div>
                <button 
                  onClick={handleStopAnalysis}
                  className="stop-btn"
                  style={{
                    background: 'rgba(244, 67, 54, 0.2)',
                    border: '1px solid #f44336',
                    color: '#ff9999',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    transition: 'all 0.2s'
                  }}
                  onMouseOver={(e) => e.target.style.background = 'rgba(244, 67, 54, 0.4)'}
                  onMouseOut={(e) => e.target.style.background = 'rgba(244, 67, 54, 0.2)'}
                >
                  ⏹ Detener
                </button>
              </div>
              <div className="video-wrapper">
                <img src={streamUrl} alt="Video Stream" className="video-stream" />
              </div>
            </div>
          ) : (
            <div className="dashboard-video-placeholder">
              <p>No hay video activo. Sube un archivo en la pestaña "Subir Archivo" para comenzar el análisis.</p>
            </div>
          )}
        </div>

        <div className="dashboard-right">
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Personas / Minuto</h3>
              <p className="stat-value">{stats.people_per_minute}</p>
            </div>
            <div className="stat-card">
              <h3>Densidad</h3>
              <p className="stat-value">{stats.density} <span style={{fontSize: '1rem', fontWeight: 'normal'}}>/ m²</span></p>
            </div>
            <div className={`stat-card mood-${stats.mood?.toLowerCase().replace('ó', 'o').replace(' ', '-')}`}>
              <h3>Estado de Ánimo</h3>
              <p className="stat-value">{stats.mood}</p>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-container">
              <h3>Evolución de Multitud</h3>
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={history}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                  <XAxis dataKey="time" stroke="#999" />
                  <YAxis stroke="#999" />
                  <Tooltip contentStyle={{ background: '#222', border: '1px solid #667eea', borderRadius: '8px' }} />
                  <Legend />
                  <Line type="monotone" name="Personas/min" dataKey="ppm" stroke="#667eea" strokeWidth={3} />
                  <Line type="monotone" name="Densidad" dataKey="density" stroke="#764ba2" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
