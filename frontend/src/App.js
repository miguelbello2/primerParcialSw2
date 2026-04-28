import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import UploadPanel from './components/UploadPanel';
import AnalysisResults from './components/AnalysisResults';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [taskId, setTaskId] = useState(null);
  const [fileId, setFileId] = useState(null);

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <h1>🏟️ Stadium Vision System</h1>
            <p>Análisis Inteligente de Tribunas con IA</p>
          </div>
          <nav className="app-nav">
            <button
              className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              Dashboard
            </button>
            <button
              className={`nav-btn ${currentPage === 'upload' ? 'active' : ''}`}
              onClick={() => setCurrentPage('upload')}
            >
              Subir Archivo
            </button>
            <button
              className={`nav-btn ${currentPage === 'results' ? 'active' : ''}`}
              onClick={() => setCurrentPage('results')}
            >
              Resultados
            </button>
          </nav>
        </div>
      </header>

      <main className="app-main">
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'upload' && <UploadPanel setCurrentPage={setCurrentPage} setTaskId={setTaskId} setFileId={setFileId} />}
        {currentPage === 'results' && <AnalysisResults taskId={taskId} fileId={fileId} />}
      </main>

      <footer className="app-footer">
        <p>Stadium Vision System © 2026 | Powered by YOLOv8n nano</p>
      </footer>
    </div>
  );
}

export default App;
