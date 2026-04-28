# 🏗️ Arquitectura del Sistema

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTE WEB                              │
│              (React Dashboard - Puerto 3000)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP/REST
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    NGINX Reverse Proxy                       │
│                   (Puerto 80 → 3000)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        │   API      │  Static    │
        │   /api/    │   Files    │
        │            │            │
┌───────▼──────────────────────────────────┐
│          FLASK BACKEND API                │
│         (Python - Puerto 5000)            │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │  Endpoints principales:             │ │
│  │  - /api/upload/*                    │ │
│  │  - /api/analyze/*                   │ │
│  │  - /api/results/*                   │ │
│  │  - /api/task/*                      │ │
│  │  - /api/stats/*                     │ │
│  └─────────────────────────────────────┘ │
└────────┬─────────────────────────────────┘
         │
    ┌────┴────────────────────────┬────────────────┐
    │                             │                │
┌───▼──────────────┐  ┌──────────▼──┐  ┌─────────▼──────┐
│ VISION ANALYZER  │  │   CROWD     │  │   INCIDENT     │
│  (OpenCV Base)   │  │  ANALYZER   │  │    DETECTOR    │
│                  │  │             │  │                │
│ • Person detect  │  │ • Density   │  │ • Panic detect │
│ • Motion detect  │  │ • Capacity  │  │ • Objects fall │
│ • Edge detect    │  │ • Anomalies │  │ • Light change │
│ • Contours       │  │ • Flow      │  │ • Barriers     │
│ • Histogram      │  │ • Tracking  │  │ • Patterns     │
└────┬─────────────┘  └──────┬──────┘  └────────┬───────┘
     │                       │                   │
     └───────────────────────┼───────────────────┘
                             │
                    ┌────────▼──────────┐
                    │  ANALYTICS ENGINE │
                    │                   │
                    │ • Reports         │
                    │ • Insights        │
                    │ • Recommendations │
                    │ • Statistics      │
                    └───────────────────┘

     ┌─────────────────────────────────────┐
     │        ALMACENAMIENTO LOCAL         │
     │                                     │
     │ • /uploads   - Archivos subidos    │
     │ • /results   - Resultados JSON     │
     │ • /models    - Modelos/Cascadas    │
     │ • /logs      - Registros del sistema
     └─────────────────────────────────────┘
```

## Componentes Principales

### 1. Frontend (React)
- **Puerto**: 3000
- **Servidor**: Nginx
- **Características**:
  - Dashboard interactivo
  - Upload de archivos
  - Visualización de resultados
  - Gráficos en tiempo real
  - Sistema de alertas

### 2. Backend (Flask)
- **Puerto**: 5000
- **Lenguaje**: Python 3.11
- **Responsabilidades**:
  - API REST
  - Autenticación (opcional)
  - Rate limiting
  - Procesamiento de archivos
  - Orquestación de análisis

### 3. Vision Analyzer (OpenCV)
- **Funciones**:
  - Detección de personas (Cascade Classifiers)
  - Análisis de movimiento
  - Detección de bordes
  - Extracción de contornos
  - Análisis de color

### 4. Crowd Analyzer
- **Análisis**:
  - Densidad por región (grilla 4x4)
  - Estimación de capacidad
  - Detección de anomalías
  - Seguimiento de flujos
  - Clasificación de estados

### 5. Incident Detector
- **Detecciones**:
  - Movimientos de pánico
  - Objetos cayendo
  - Cambios de iluminación
  - Integridad de barreras
  - Patrones anómalos

### 6. Analytics Engine
- **Genera**:
  - Reportes completos
  - Insights automáticos
  - Recomendaciones
  - Estadísticas y comparativas

## Flujo de Datos

### Análisis de Video

```
1. Usuario sube video
   ↓
2. Validación y almacenamiento
   ↓
3. Video decodificado con OpenCV
   ↓
4. Frame por frame:
   ├─ Redimensionamiento (640x480)
   ├─ Detección de personas
   ├─ Análisis de densidad
   ├─ Detección de incidentes
   └─ Generación de métricas
   ↓
5. Agregación de resultados
   ↓
6. Generación de recomendaciones
   ↓
7. Almacenamiento en JSON
   ↓
8. Usuario visualiza en dashboard
```

### Procesamiento Paralelo

- Cada frame se procesa independientemente
- Análisis en tiempo real (~30fps)
- Resultados agregados por intervalos
- Almacenamiento incremental

## Tecnologías de Visión Artificial Utilizadas

### OpenCV Algoritmos
1. **Cascade Classifiers** (detección de personas)
2. **Canny Edge Detection** (bordes)
3. **Contour Detection** (contornos)
4. **Optical Flow** (movimiento)
5. **Morphological Operations** (preprocesamiento)

### Procesamiento de Imágenes
- Conversión de espacios de color (BGR → Gray, HSV)
- Thresholding adaptativo
- Operaciones morfológicas
- Filtrado Gaussiano

### Análisis Estadístico
- Media, desviación estándar
- Z-score para anomalías
- Distribuciones espaciales
- Análisis de varianza

## Escalabilidad

### Horizontal
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Backend 1  │────│  Load Balancer│────│   Backend 2  │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Vertical
- Aumentar CPU para procesamiento más rápido
- Aumentar RAM para análisis simultáneo
- Usar GPU para aceleración (CUDA)

## Performance

### Optimizaciones Implementadas
- Redimensionamiento de frames
- Análisis parcial (cada N frames)
- Caché de cascadas
- Procesamiento asincrónico
- Rate limiting

### Benchmark Esperado
- Video 1080p: ~5-10 seg de análisis por minuto
- Video 720p: ~3-5 seg de análisis por minuto
- Imagen: <1 segundo

## Seguridad

### Capas
1. **Input Validation**: Verificación de archivos
2. **Rate Limiting**: Límite de requests
3. **File Size Limits**: 500MB máximo
4. **CORS**: Cross-Origin Resource Sharing
5. **Error Handling**: Logging de errores

## Mantenimiento

### Logs
```
backend/
  └─ logs/
     ├─ app.log
     ├─ analysis.log
     └─ errors.log
```

### Monitoreo
- Health checks automáticos
- Métricas de CPU/RAM
- Errores y excepciones
- Tiempos de respuesta

## Futuras Mejoras

1. **Machine Learning**
   - Entrenamiento de modelos personalizados
   - YOLO v8 para mejor detección
   - Clasificación con redes neuronales

2. **Real-time**
   - WebSockets para live streaming
   - Análisis en tiempo real
   - Alertas instantáneas

3. **Escalabilidad**
   - Kubernetes deployment
   - Load balancing
   - Caché distribuido

4. **Persistencia**
   - Base de datos (PostgreSQL)
   - Historial de análisis
   - Reportes archivados

5. **Integraciones**
   - APIs externas
   - Webhooks
   - Sistemas de seguridad existentes
