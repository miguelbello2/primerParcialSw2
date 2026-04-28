import React, { useState } from 'react';
import axios from 'axios';
import './UploadPanel.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export default function UploadPanel({ setCurrentPage, setTaskId, setFileId }) {
  const [file, setFile] = useState(null);
  const [analysisType, setAnalysisType] = useState('crowd');
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage(null);
    }
  };

  const handleUploadAndAnalyze = async (e) => {
    e.preventDefault();

    if (!file) {
      setMessage({ type: 'error', text: 'Por favor selecciona un archivo' });
      return;
    }

    setLoading(true);
    setUploadProgress(0);

    try {
      let fileId;

      // Upload file
      const formData = new FormData();
      formData.append('file', file);

      const fileType = file.type.startsWith('video') ? 'video' : 'image';
      const uploadEndpoint = fileType === 'video' ? '/api/upload/video' : '/api/upload/image';

      const uploadResponse = await axios.post(`${API_URL}${uploadEndpoint}`, formData, {
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });
      fileId = uploadResponse.data.file_id;
      setMessage({ type: 'success', text: `Archivo subido: ${fileId}` });

      // Start analysis
      const analysisEndpoint = analysisType === 'crowd' ? '/api/analyze/video/crowd' : '/api/analyze/video/incidents';
      const analysisResponse = await axios.post(`${API_URL}${analysisEndpoint}`, { file_id: fileId });

      const taskId = analysisResponse.data.task_id;
      setTaskId(taskId);
      setFileId(fileId);

      setMessage({
        type: 'info',
        text: `Análisis iniciado. ID de tarea: ${taskId}`,
      });

      // Redirect to dashboard after 2 seconds to view the live stream
      setTimeout(() => {
        setCurrentPage('dashboard');
      }, 2000);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Error al procesar el archivo',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-panel">
      <h2 className="page-title">Subir y Analizar Archivo</h2>

      <div className="upload-container">
        <form onSubmit={handleUploadAndAnalyze} className="upload-form">



          <div className="form-group">
            <label>Tipo de Análisis</label>
            <div className="analysis-options">
              <label className="radio-label">
                <input
                  type="radio"
                  value="crowd"
                  checked={analysisType === 'crowd'}
                  onChange={(e) => setAnalysisType(e.target.value)}
                />
                <span>Análisis de Multitudes</span>
                <small>Densidad, capacidad y flujos</small>
              </label>
              <label className="radio-label">
                <input
                  type="radio"
                  value="incidents"
                  checked={analysisType === 'incidents'}
                  onChange={(e) => setAnalysisType(e.target.value)}
                />
                <span>Detección de Incidentes</span>
                <small>Anomalías y alertas de seguridad</small>
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Selecciona un archivo (video o imagen)</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                id="fileInput"
                onChange={handleFileChange}
                accept="video/*,image/*"
                disabled={loading}
              />
              <label htmlFor="fileInput" className="file-input-label">
                {file ? `${file.name}` : '📁 Arrastra un archivo aquí o haz clic'}
              </label>
            </div>
            {file && (
              <p className="file-info">
                Tamaño: {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            )}
          </div>

          {uploadProgress > 0 && uploadProgress < 100 && (
            <div className="progress-container">
              <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
              <p className="progress-text">{uploadProgress}%</p>
            </div>
          )}

          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !file}
          >
            {loading ? 'Procesando...' : 'Subir y Analizar'}
          </button>
        </form>

        {message && (
          <div className={`message message-${message.type}`}>
            <span className={`icon ${message.type}`}>
              {message.type === 'success' ? '✓' : message.type === 'error' ? '✕' : 'ℹ'}
            </span>
            <p>{message.text}</p>
          </div>
        )}
      </div>

      <div className="info-section">
        <h3>Formatos Soportados</h3>
        <ul>
          <li><strong>Video:</strong> MP4, AVI, MOV, MKV</li>
          <li><strong>Imagen:</strong> JPG, PNG</li>
          <li><strong>Tamaño máximo:</strong> 500 MB</li>
        </ul>
      </div>

      <div className="tips-section">
        <h3>📋 Recomendaciones</h3>
        <ul>
          <li>Utiliza videos de al menos 640x480 de resolución</li>
          <li>La duración recomendada es entre 30 segundos y 5 minutos</li>
          <li>Asegúrate de buena iluminación para mejores resultados</li>
          <li>El sistema analizará automáticamente el contenido</li>
        </ul>
      </div>
    </div>
  );
}
