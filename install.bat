@echo off
REM Stadium Vision System - Installation Script for Windows
REM Instalador automático para Windows

setlocal enabledelayedexpansion

echo.
echo 🏟️  Stadium Vision System - Instalador
echo ========================================
echo.

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no está instalado
    echo Por favor instala Docker Desktop que incluye Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker detectado:
docker --version
echo ✅ Docker Compose detectado:
docker-compose --version
echo.

REM Crear directorios
echo 📁 Creando directorios...
if not exist uploads mkdir uploads
if not exist results mkdir results
if not exist models mkdir models
if not exist logs mkdir logs

REM Crear archivo .env si no existe
if not exist .env (
    echo ⚙️  Creando archivo .env...
    if exist .env.example (
        copy .env.example .env
    ) else (
        echo # Configuración automática > .env
    )
)

echo.
echo 🔨 Compilando imágenes Docker...
echo   Esto puede tomar 5-10 minutos en la primera ejecución...
docker-compose build

echo.
echo 🚀 Iniciando servicios...
docker-compose up -d

echo.
echo ⏳ Esperando a que los servicios se inicien...
timeout /t 10 /nobreak

echo.
echo ✨ ¡Instalación completada exitosamente!
echo.
echo 📍 Accede a la aplicación:
echo    Frontend: http://localhost:3000
echo    Backend API: http://localhost:5000
echo.
echo 📚 Para más información, consulta:
echo    README.md - Documentación completa
echo    QUICKSTART.md - Guía rápida
echo.
echo 🛠️  Comandos útiles:
echo    docker-compose ps      - Ver estado de servicios
echo    docker-compose logs -f - Ver logs en tiempo real
echo    docker-compose down    - Detener servicios
echo.
pause
