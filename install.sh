#!/bin/bash

# Stadium Vision System - Installation Script
# Instalador automático para Linux y macOS

set -e

echo "🏟️  Stadium Vision System - Instalador"
echo "========================================"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "Por favor instala Docker desde: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    echo "Por favor instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker detectado: $(docker --version)"
echo "✅ Docker Compose detectado: $(docker-compose --version)"
echo ""

# Crear directorio de proyecto si no existe
if [ ! -d "stadium-vision-system" ]; then
    echo "📁 Creando directorio del proyecto..."
    mkdir -p stadium-vision-system
    cd stadium-vision-system
else
    cd stadium-vision-system
fi

# Copiar archivos de configuración si no existen
if [ ! -f ".env" ]; then
    echo "⚙️  Creando archivo .env..."
    cp .env.example .env 2>/dev/null || echo "# Nota: Copia .env.example a .env"
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p uploads results models logs

# Verificar espacio en disco
DISK_SPACE=$(df . | awk 'NR==2 {print $4}')
if [ "$DISK_SPACE" -lt 500000 ]; then
    echo "⚠️  Advertencia: Espacio en disco limitado (mínimo 500MB recomendado)"
fi

echo ""
echo "🔨 Compilando imágenes Docker..."
echo "  Esto puede tomar 5-10 minutos en la primera ejecución..."
docker-compose build

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo ""
echo "⏳ Esperando a que los servicios se inicien..."
sleep 10

# Verificar health
echo "🏥 Verificando salud de los servicios..."

# Revisar backend
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Backend está listo"
else
    echo "⚠️  Backend aún se está iniciando..."
fi

# Revisar frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend está listo"
else
    echo "⚠️  Frontend aún se está iniciando..."
fi

echo ""
echo "✨ ¡Instalación completada exitosamente!"
echo ""
echo "📍 Accede a la aplicación:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo ""
echo "📚 Para más información, consulta:"
echo "   README.md - Documentación completa"
echo "   QUICKSTART.md - Guía rápida"
echo ""
echo "🛠️  Comandos útiles:"
echo "   docker-compose ps      - Ver estado de servicios"
echo "   docker-compose logs -f - Ver logs en tiempo real"
echo "   docker-compose down    - Detener servicios"
echo ""
