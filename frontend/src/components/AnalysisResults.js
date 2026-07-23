import React, { useState, useEffect, useRef } from 'react';
import './AnalysisResults.css';
import api, { apiUrl } from '../api';

const POLL_INTERVAL = 2000;

export default function AnalysisResults({ taskId, fileId }) {
  const [status, setStatus] = useState('idle');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  // Poll analysis task status
  useEffect(() => {
    if (!taskId) return;

    setStatus('polling');
    setData(null);
    setError(null);

    intervalRef.current = setInterval(async () => {
      try {
        const { data: task } = await api.get(`/api/task/${taskId}`);
        if (task.status === 'completed') {
          clearInterval(intervalRef.current);
          const { data: results } = await api.get(`/api/results/${taskId}`);
          setData(results);
          setStatus('completed');
        } else if (task.status === 'failed') {
          clearInterval(intervalRef.current);
          setError(task.error || 'El análisis falló');
          setStatus('failed');
        }
      } catch (err) {
        clearInterval(intervalRef.current);
        setError('Error al obtener el estado del análisis');
        setStatus('failed');
      }
    }, POLL_INTERVAL);

    return () => clearInterval(intervalRef.current);
  }, [taskId]);



  const isVideo = fileId && /\.(mp4|avi|mov|mkv|webm|m4v|ts|flv)$/i.test(fileId);
  const streamUrl = isVideo
    ? apiUrl(`/api/stream/video?filename=${encodeURIComponent(fileId)}`)
    : null;

  if (!taskId && !fileId) {
    return (
      <div className="analysis-results">
        <h2 className="page-title">Resultados de Análisis</h2>
        <div className="empty-state">
          <p>No hay análisis disponible. Por favor, sube un archivo primero.</p>
        </div>
      </div>
    );
  }



  return (
    <div className="analysis-results">
      <h2 className="page-title">Análisis en Tiempo Real</h2>

      <div className={`analysis-layout ${!streamUrl ? 'no-video' : ''}`}>



        {/* ── Results panel column ── */}
        <div className="results-panel">
          {status === 'polling' && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Analizando video...</p>
              <small>Esto puede tardar unos minutos dependiendo del tamaño del archivo</small>
            </div>
          )}

          {status === 'failed' && (
            <div className="empty-state error">
              <p>El análisis falló: {error}</p>
            </div>
          )}

          {status === 'completed' && data && (
            <>
              <div className="tabs">
                <button className="tab-btn active">Resumen</button>
              </div>

              {true && (
                <div className="tab-content">
                  <div className="results-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                    <div className="result-card">
                      <h3>Total de Personas</h3>
                      <p className="metric-value">{Math.round((data.average_density || 0) * 50)}</p>
                      <p className="metric-desc">detectadas en promedio</p>
                    </div>
                    <div className="result-card">
                      <h3>Densidad Promedio</h3>
                      <p className="metric-value">{data.average_density?.toFixed(2) ?? 'N/A'}</p>
                      <p className="metric-desc">personas/m²</p>
                    </div>
                    <div className="result-card">
                      <h3>Estado de Ánimo</h3>
                      <p className="metric-value">
                        {(data.average_density || 0) < 0.3 ? 'Tranquilo' : (data.average_density || 0) < 0.8 ? 'Animado' : (data.average_density || 0) < 1.5 ? 'Eufórico' : 'Tenso'}
                      </p>
                      <p className="metric-desc">predominante</p>
                    </div>
                  </div>
                </div>
              )}


              <div className="actions">
                <button className="action-btn export">📥 Exportar Reporte</button>
                <button className="action-btn pdf">📄 Generar PDF</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
