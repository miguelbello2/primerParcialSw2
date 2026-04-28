# 📦 Stadium Vision System - Project Manifest

## Información del Proyecto

- **Nombre**: Stadium Vision System
- **Versión**: 1.0.0
- **Fecha de Creación**: 2024
- **Descripción**: Sistema inteligente de análisis de tribunas usando visión artificial e IA
- **Licencia**: Educativa/Comercial

## 📁 Estructura de Archivos

```
stadium-vision-system/
│
├── 📄 Documentación
│   ├── README.md                 # Documentación principal
│   ├── QUICKSTART.md             # Guía de inicio rápido
│   ├── ARCHITECTURE.md           # Arquitectura del sistema
│   ├── PROJECT_MANIFEST.md       # Este archivo
│   └── .env.example              # Configuración de ejemplo
│
├── 🐳 Docker & DevOps
│   ├── docker-compose.yml        # Orquestación de servicios
│   ├── Dockerfile.backend        # Imagen del backend
│   ├── Dockerfile.frontend       # Imagen del frontend
│   ├── install.sh               # Script de instalación (Linux/Mac)
│   ├── install.bat              # Script de instalación (Windows)
│   └── .gitignore               # Ignore para Git
│
├── 🐍 Backend (Python/Flask)
│   └── backend/
│       ├── app.py               # API Flask principal (500+ líneas)
│       ├── vision_analyzer.py   # Analizador de visión base (250+ líneas)
│       ├── crowd_analyzer.py    # Analizador de multitudes (350+ líneas)
│       ├── incident_detector.py # Detector de incidentes (300+ líneas)
│       └── analytics_engine.py  # Motor de análisis (150+ líneas)
│
├── ⚛️ Frontend (React)
│   └── frontend/
│       ├── package.json         # Dependencias Node
│       ├── nginx.conf           # Configuración de servidor
│       ├── public/
│       │   └── index.html       # HTML principal
│       └── src/
│           ├── index.js         # Punto de entrada React
│           ├── index.css        # Estilos globales
│           ├── App.js           # Componente principal
│           ├── App.css          # Estilos de App
│           └── components/
│               ├── Dashboard.js      # Dashboard principal
│               ├── Dashboard.css     # Estilos del dashboard
│               ├── UploadPanel.js    # Panel de subida
│               ├── UploadPanel.css   # Estilos del panel
│               ├── AnalysisResults.js # Resultados
│               └── AnalysisResults.css # Estilos de resultados
│
├── 📋 Configuración
│   ├── requirements.txt          # Dependencias Python
│   └── .env.example              # Variables de entorno
│
└── 📁 Directorios en Tiempo de Ejecución (creados automáticamente)
    ├── uploads/                 # Archivos subidos por usuarios
    ├── results/                 # Resultados de análisis en JSON
    ├── models/                  # Modelos y cascadas de IA
    └── logs/                    # Registros del sistema
```

## 🔧 Dependencias Principales

### Backend (Python)
- Flask 2.3.3 - Framework web
- OpenCV 4.8.0 - Visión artificial
- NumPy 1.24.3 - Computación numérica
- Pillow 10.0.0 - Procesamiento de imágenes
- scikit-learn 1.3.0 - Machine learning
- Flask-CORS 4.0.0 - Cross-origin support
- Flask-Limiter 3.5.0 - Rate limiting
- Gunicorn 21.2.0 - WSGI server

### Frontend (JavaScript)
- React 18.2.0 - Framework UI
- React-DOM 18.2.0 - Renderizador
- Recharts 2.7.2 - Gráficos
- Axios 1.4.0 - Cliente HTTP
- React-Router 6.14.0 - Enrutamiento

### Infraestructura
- Docker - Containerización
- Docker Compose - Orquestación
- Nginx - Servidor web
- Python 3.11 - Runtime backend
- Node.js 18 - Runtime frontend

## 📊 Estadísticas del Código

### Líneas de Código
- Backend Python: ~1500+ líneas
- Frontend React: ~700+ líneas
- Dockerfiles: ~60 líneas
- Documentación: ~2000+ líneas

### Módulos
- **Backend**: 5 módulos principales
- **Frontend**: 3 componentes principales
- **APIs**: 15+ endpoints REST

## 🎯 Funcionalidades Principales

### Análisis de Tribunas
- ✅ Análisis de densidad de multitudes
- ✅ Estimación de capacidad
- ✅ Detección de anomalías
- ✅ Seguimiento de flujos
- ✅ Análisis espacial en grillas

### Detección de Incidentes
- ✅ Detección de pánico/movimientos bruscos
- ✅ Identificación de objetos cayendo
- ✅ Análisis de cambios de iluminación
- ✅ Verificación de barreras
- ✅ Detección de patrones anómalos

### Interfaz de Usuario
- ✅ Dashboard en tiempo real
- ✅ Upload de archivos
- ✅ Visualización de resultados
- ✅ Gráficos interactivos
- ✅ Sistema de alertas
- ✅ Recomendaciones automáticas

## 🚀 Cómo Usar

### Instalación Rápida

#### Linux/Mac
```bash
chmod +x install.sh
./install.sh
```

#### Windows
```bash
install.bat
```

#### Manual
```bash
docker-compose up -d
```

### Acceso

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 📚 Tecnologías de IA Implementadas

### Algoritmos OpenCV
1. Cascade Classifiers - Detección de rostros y cuerpos
2. Canny Edge Detection - Detección de bordes
3. Optical Flow - Análisis de movimiento
4. Contour Detection - Extracción de formas
5. Color Histograms - Análisis de distribución de color

### Técnicas de Procesamiento
- Conversión de espacios de color
- Thresholding adaptativo
- Operaciones morfológicas
- Filtrado Gaussiano
- Análisis estadístico

## 🔒 Características de Seguridad

- Rate limiting (200 req/día, 50 req/hora)
- Validación de archivos
- Sanitización de nombres
- CORS configurado
- Límite de tamaño (500MB)
- Manejo de errores robusto

## 📈 Escalabilidad

### Horizontal
- Load balancing ready
- Múltiples instancias de backend
- Almacenamiento centralizado

### Vertical
- Optimizado para CPU
- GPU-ready (CUDA compatible)
- Procesamiento paralelo

## 🐛 Debugging & Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Específicamente backend
docker-compose logs -f backend

# Específicamente frontend
docker-compose logs -f frontend
```

## 🔄 Ciclo de Vida de un Análisis

1. **Upload**: Usuario sube archivo (video/imagen)
2. **Validación**: Sistema valida formato y tamaño
3. **Almacenamiento**: Archivo se guarda en uploads/
4. **Procesamiento**: OpenCV analiza frame by frame
5. **Análisis**: Se ejecutan detecciones y análisis
6. **Generación**: Se generan resultados JSON
7. **Visualización**: Usuario ve resultados en dashboard
8. **Exportación**: Usuario puede exportar reportes

## 🎓 Basado en Investigación

Fundamentado en el documento académico:
"Sistema de Visión Artificial para Control y Monitoreo en Tribunas del Estadio Municipal"

Implementa:
- Detección de personas (Haar Cascades)
- Análisis de multitudes (densidad, capacidad)
- Detección de anomalías (cambios anormales)
- Sistemas de seguridad inteligentes

## 📞 Soporte Técnico

### Problemas Comunes

**Puerto en uso**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3000
kill -9 <PID>
```

**Memoria insuficiente**
```bash
# Verificar uso
docker stats

# Limpiar containers
docker system prune
```

**Archivos no se procesan**
```bash
# Verificar permisos
docker-compose exec backend ls -la uploads/

# Verificar tamaño
du -h uploads/
```

## 📝 Versioning

- **v1.0.0**: Versión inicial completa
  - Backend completo con análisis
  - Frontend React con dashboard
  - Docker containerization
  - Documentación completa

## 🎁 Incluido en el Paquete

- ✅ Código fuente completo
- ✅ Configuración Docker
- ✅ Frontend React totalmente funcional
- ✅ Backend Python con 5 módulos
- ✅ Documentación completa
- ✅ Guías de instalación (Windows/Mac/Linux)
- ✅ Ejemplos y casos de uso
- ✅ Scripts de instalación automática
- ✅ Configuración de desarrollo
- ✅ README y QUICKSTART

## 🚀 Próximas Mejoras

- [ ] Integración con YOLO v8
- [ ] Base de datos PostgreSQL
- [ ] WebSockets para live streaming
- [ ] Autenticación de usuarios
- [ ] Kubernetes deployment
- [ ] API GraphQL
- [ ] Webhooks
- [ ] Integración con sistemas de emergencia

---

**Stadium Vision System v1.0** | Proyecto Completo en Docker | 2024
