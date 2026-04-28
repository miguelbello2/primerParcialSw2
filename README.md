# 🏟️ Stadium Vision System

Sistema inteligente de análisis de tribunas usando visión artificial (Computer Vision) e inteligencia artificial. Este proyecto utiliza las tecnologías propuestas en el documento "Vision Artificial Tribunas" para crear una solución completa de monitoreo, análisis y seguridad en estadios.

## 🎯 Características Principales

### 1. **Análisis de Multitudes**
- Cálculo de densidad por región
- Estimación de capacidad utilizada
- Detección de anomalías de distribución
- Seguimiento de flujos y movimiento
- Análisis espacial en grillas 4x4

### 2. **Detección de Incidentes**
- Detección de movimientos bruscos/pánico
- Identificación de objetos cayendo
- Análisis de cambios de iluminación
- Verificación de integridad de barreras
- Detección de patrones anómalos

### 3. **Procesamiento de Video e Imagen**
- Soporte para múltiples formatos (MP4, AVI, MOV, MKV, JPG, PNG)
- Procesamiento en tiempo real
- Análisis de bordes y contornos
- Detección de personas con cascadas de Haar
- Análisis de flujo óptico

### 4. **Dashboard Interactivo**
- Interfaz web moderna y responsive
- Gráficos en tiempo real
- Sistema de alertas
- Visualización de métricas
- Exportación de reportes

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask**: Framework web Python
- **OpenCV**: Procesamiento de imágenes y visión artificial
- **NumPy**: Computación numérica
- **scikit-learn**: Análisis estadístico
- **Python 3.11**: Lenguaje de programación

### Frontend
- **React 18**: Framework JavaScript
- **Recharts**: Visualización de datos
- **Axios**: Cliente HTTP
- **CSS3**: Estilos avanzados

### DevOps
- **Docker**: Containerización
- **Docker Compose**: Orquestación
- **Nginx**: Servidor web

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Mínimo 2GB de RAM disponible
- 500MB de espacio en disco
- Conexión a internet (para descargar imágenes base)

## 🚀 Instalación Rápida

### 1. Clonar o descargar el proyecto

```bash
cd stadium-vision-system
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

### 3. Construir las imágenes Docker

```bash
docker-compose build
```

### 4. Iniciar los servicios

```bash
docker-compose up -d
```

### 5. Acceder a la aplicación

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📖 Guía de Uso

### Subir un archivo para análisis

1. Navega a la sección "Subir Archivo"
2. Selecciona el tipo de análisis:
   - **Análisis de Multitudes**: Densidad, capacidad, flujos
   - **Detección de Incidentes**: Anomalías y alertas
3. Selecciona un video o imagen
4. Haz clic en "Subir y Analizar"
5. Espera a que se complete el procesamiento
6. Visualiza los resultados en "Resultados"

### API REST Endpoints

#### Upload Endpoints

```bash
# Subir video
POST /api/upload/video
Content-Type: multipart/form-data
Body: file

# Subir imagen
POST /api/upload/image
Content-Type: multipart/form-data
Body: file
```

#### Analysis Endpoints

```bash
# Análisis de multitudes en video
POST /api/analyze/video/crowd
Content-Type: application/json
Body: { "file_id": "filename" }

# Detección de incidentes
POST /api/analyze/video/incidents
Content-Type: application/json
Body: { "file_id": "filename" }

# Análisis de imagen (multitudes)
POST /api/analyze/image/crowd
Content-Type: application/json
Body: { "file_id": "filename" }
```

#### Results Endpoints

```bash
# Obtener estado de tarea
GET /api/task/<task_id>

# Obtener resultados
GET /api/results/<task_id>

# Estadísticas del sistema
GET /api/stats/overview

# Health check
GET /api/health
```

## 📊 Estructura del Proyecto

```
stadium-vision-system/
├── backend/
│   ├── app.py                 # API Flask principal
│   ├── vision_analyzer.py     # Módulo de visión base
│   ├── crowd_analyzer.py      # Análisis de multitudes
│   ├── incident_detector.py   # Detección de incidentes
│   └── analytics_engine.py    # Motor de análisis
├── frontend/
│   ├── src/
│   │   ├── App.js            # Componente principal
│   │   ├── components/
│   │   │   ├── Dashboard.js  # Dashboard
│   │   │   ├── UploadPanel.js # Panel de subida
│   │   │   └── AnalysisResults.js # Resultados
│   │   └── index.js
│   ├── public/
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── requirements.txt
└── README.md
```

## 🔧 Configuración Avanzada

### Cambiar puertos

Edita `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "5000:5000"  # Cambiar primer puerto
  frontend:
    ports:
      - "3000:80"    # Cambiar primer puerto
```

### Aumentar límites de archivos

En `app.py`:

```python
MAX_FILE_SIZE = 1024 * 1024 * 1024  # 1GB en lugar de 500MB
```

### Ajustar parámetros de análisis

En `crowd_analyzer.py`:

```python
GRID_DIVISIONS = 6  # Cambiar granularidad del análisis
FRAME_LIMIT = 600  # Más frames para analizar
```

## 📈 Metricas y Resultados

### Análisis de Multitudes
- Densidad promedio (personas/m²)
- Densidad máxima
- Distribución espacial
- Flujo de movimiento
- Estado de capacidad

### Detección de Incidentes
- Incidentes totales detectados
- Alertas críticas
- Advertencias
- Tipos de incidente
- Frames afectados

## 🚨 Sistema de Alertas

| Densidad | Estado | Color | Acción |
|----------|--------|-------|--------|
| < 2 | Normal | 🟢 | Monitoreo normal |
| 2-5 | Moderado | 🟡 | Incrementar vigilancia |
| 5-8 | Alto | 🟠 | Preparar controles |
| > 8 | Crítico | 🔴 | Protocolos de emergencia |

## 📝 Logs y Debugging

### Ver logs del backend

```bash
docker-compose logs backend -f
```

### Ver logs del frontend

```bash
docker-compose logs frontend -f
```

### Acceder a la terminal del contenedor

```bash
docker-compose exec backend bash
docker-compose exec frontend bash
```

## 🔐 Seguridad

- Rate limiting activado (200 req/día, 50 req/hora)
- Validación de archivos
- Sanitización de nombres de archivo
- CORS configurado
- Límite de tamaño de archivo: 500MB

## 📦 Detener y Limpiar

```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes
docker-compose down -v

# Eliminar imágenes
docker rmi stadium-vision-backend stadium-vision-frontend
```

## 📚 Documentación Técnica

### Algoritmos Implementados

1. **Detección de Personas**: Cascadas de Haar (faces, upper bodies)
2. **Detección de Movimiento**: Diferencia de frames + Canny edges
3. **Análisis de Densidad**: Grilla espacial + conteo por región
4. **Flujo Óptico**: Farneback optical flow
5. **Detección de Anomalías**: Z-score en distribución espacial

### Modelos de IA Incluidos

- Cascadas Haar (OpenCV built-in)
- Modelos YOLO (opcional para expansión)
- Redes neuronales (TensorFlow - opcional)

## 🤝 Contribuciones

Este proyecto está basado en las propuestas del documento "Sistema de Visión Artificial para Control y Monitoreo en Tribunas del Estadio Municipal".

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisar los logs
2. Verificar configuración de Docker
3. Validar formatos de archivo
4. Consultar documentación técnica

## 📄 Licencia

Proyecto educativo/comercial para análisis de estadios y sistemas de seguridad.

## 🎓 Referencia Académica

Fundamentado en:
- Inteligencia Artificial y Visión Artificial
- Procesamiento de Imágenes Digital
- Análisis Estadístico de Multitudes
- Sistemas de Seguridad Deportiva

---

**Stadium Vision System v1.0** | Desarrollado con OpenCV, Python y React
