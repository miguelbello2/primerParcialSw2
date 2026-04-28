# ⚡ Guía de Inicio Rápido

## 1️⃣ Requisitos Mínimos
- Docker y Docker Compose
- 2GB RAM disponible
- 500MB espacio en disco

## 2️⃣ Pasos de Instalación (5 minutos)

```bash
# 1. Descargar proyecto
unzip stadium-vision-system.zip
cd stadium-vision-system

# 2. Iniciar servicios
docker-compose up -d

# 3. Esperar 30-60 segundos
# Las imágenes se construirán automáticamente

# 4. Acceder a la aplicación
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/health
```

## 3️⃣ Primer Análisis

1. Abre http://localhost:3000 en tu navegador
2. Ve a "Subir Archivo"
3. Selecciona tipo de análisis (Multitudes o Incidentes)
4. Sube un video o imagen
5. Espera a que se complete
6. Visualiza resultados

## 4️⃣ Archivos de Prueba

Ejemplos de formatos soportados:
- Video: `video.mp4`, `footage.avi`
- Imagen: `tribuna.jpg`, `estadio.png`
- Máximo: 500MB

## 5️⃣ Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Detener servicios
docker-compose down

# Reiniciar
docker-compose restart

# Reconstruir imágenes
docker-compose build --no-cache
```

## 🐛 Solución de Problemas

### Puerto 3000/5000 en uso
```bash
# Cambiar puertos en docker-compose.yml
# frontend ports: "8080:80"
# backend ports: "8000:5000"
docker-compose up -d
```

### Memoria insuficiente
```bash
# Verificar uso de memoria
docker stats

# Aumentar límite en docker-compose.yml
# mem_limit: 2g
```

### Archivos no se suben
```bash
# Verificar permisos
docker-compose exec backend ls -la uploads/

# Verificar tamaño
ls -lh archivo.mp4
```

## 📊 Ejemplos de Uso

### API Curl - Subir Video
```bash
curl -X POST -F "file=@video.mp4" \
  http://localhost:5000/api/upload/video
```

### API Curl - Iniciar Análisis
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"file_id":"20240101_120000_video.mp4"}' \
  http://localhost:5000/api/analyze/video/crowd
```

### API Curl - Obtener Resultados
```bash
curl http://localhost:5000/api/task/crowd_20240101_120000_video.mp4_1234567890
```

## 📈 Dashboard Features

✅ Estadísticas en tiempo real
✅ Gráficos de densidad
✅ Sistema de alertas
✅ Análisis de múltiples zonas
✅ Recomendaciones inteligentes
✅ Exportación de reportes

## 🎯 Casos de Uso

- Monitoreo de capacidad en estadios
- Análisis de seguridad en eventos
- Estimación de afluencia
- Detección de anomalías
- Reportes post-evento
- Planificación de evacuación

## 🔗 Enlaces Útiles

- Frontend: http://localhost:3000
- API Docs: http://localhost:5000/api/
- Health: http://localhost:5000/health
- Swagger: http://localhost:5000/docs (si está habilitado)

## 💡 Próximos Pasos

1. Entrenar modelos personalizados
2. Integrar YOLO para mejor detección
3. Agregar notificaciones en tiempo real
4. Crear base de datos de historial
5. Implementar API webhooks

---

**¿Necesitas ayuda?** Consulta el README.md para documentación completa.
