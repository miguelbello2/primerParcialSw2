/**
 * Resolución de la URL del backend en tiempo de ejecución.
 *
 * Create React App congela process.env.REACT_APP_* durante el build, así que un
 * backend con URL cambiante (ngrok/Colab) obligaría a redeployar Vercel en cada
 * sesión. Aquí la URL se resuelve en el navegador, con este orden de prioridad:
 *
 *   1. ?api=https://xxxx.ngrok-free.app  (se guarda y luego se limpia de la URL)
 *   2. localStorage                       (lo guardado por el paso 1 o por la UI)
 *   3. REACT_APP_API_URL                  (build de Vercel, backend estable)
 *   4. http://localhost:5000              (desarrollo local)
 */

import axios from 'axios';

const STORAGE_KEY = 'stadiumVision.apiUrl';
const BUILD_TIME_URL = process.env.REACT_APP_API_URL || '';
const DEFAULT_URL = 'http://localhost:5000';

function normalize(url) {
  const trimmed = (url || '').trim();
  if (!trimmed) return '';
  return trimmed.replace(/\/+$/, '');
}

function readOverride() {
  try {
    return normalize(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return ''; // localStorage bloqueado (modo privado / cookies deshabilitadas)
  }
}

// Consume ?api= una sola vez, al cargar el módulo, y lo persiste.
function consumeQueryParam() {
  try {
    const fromQuery = normalize(new URLSearchParams(window.location.search).get('api'));
    if (!fromQuery) return;

    window.localStorage.setItem(STORAGE_KEY, fromQuery);

    // Quita ?api= de la barra de direcciones para no compartirlo por accidente.
    const url = new URL(window.location.href);
    url.searchParams.delete('api');
    window.history.replaceState({}, '', url.toString());
  } catch {
    // Sin window (SSR) o localStorage bloqueado: se ignora el override.
  }
}

consumeQueryParam();

export function getApiUrl() {
  return readOverride() || normalize(BUILD_TIME_URL) || DEFAULT_URL;
}

export function setApiUrl(url) {
  const normalized = normalize(url);
  try {
    if (normalized) {
      window.localStorage.setItem(STORAGE_KEY, normalized);
    } else {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // Sin persistencia: el cambio solo dura hasta recargar.
  }
  return normalized || normalize(BUILD_TIME_URL) || DEFAULT_URL;
}

/** true si la URL activa viene de un override manual y no del build. */
export function hasOverride() {
  return Boolean(readOverride());
}

/** Construye una URL absoluta del backend. Útil para <img src> y <video src>. */
export function apiUrl(path) {
  return `${getApiUrl()}${path}`;
}

// Instancia de axios que resuelve baseURL en cada request, no al importarse.
const api = axios.create({
  headers: { 'ngrok-skip-browser-warning': 'true' },
});

api.interceptors.request.use((config) => {
  config.baseURL = getApiUrl();
  return config;
});

export default api;
