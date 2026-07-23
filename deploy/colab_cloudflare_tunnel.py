"""
Stadium Vision — Backend en Colab expuesto con Cloudflare Tunnel.

Pega TODO este archivo en una sola celda de Google Colab y ejecútala.
Antes: Entorno de ejecución -> Cambiar tipo de entorno de ejecución -> T4 GPU.

La celda se queda corriendo a propósito: mientras siga activa, el backend vive.
Para detener: Entorno de ejecución -> Interrumpir ejecución.
"""

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

REPO = "https://github.com/miguelbello2/primerParcialSw2.git"
DEST = "/content/primerParcialSw2"
PORT = 5000
BACKEND_LOG = "/content/backend.log"
TUNNEL_LOG = "/content/cloudflared.log"

# Reemplaza por tu dominio de Vercel para que el enlace final quede armado
FRONTEND = "https://TU-PROYECTO.vercel.app"


def run(cmd, **kw):
    """Ejecuta un comando y aborta con su salida si falla."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if result.returncode != 0:
        raise RuntimeError(f"Falló {' '.join(cmd)}:\n{result.stdout}\n{result.stderr}")
    return result.stdout


# ---------------------------------------------------------------- 1. Repo
# Salir de DEST antes de borrarlo: al re-ejecutar la celda, el proceso sigue
# parado dentro de DEST/backend de la corrida anterior, y borrar el directorio
# actual deja un cwd colgado que hace fallar a git con
# "Unable to read current working directory".
os.chdir("/content")

# Clon limpio: evita arrastrar estado de una ejecución anterior
if os.path.exists(DEST):
    shutil.rmtree(DEST)
run(["git", "clone", "--depth", "1", REPO, DEST])
os.chdir(f"{DEST}/backend")
print("✔ Repositorio clonado")

# ------------------------------------------------------------ 2. Paquetes
# Colab ya trae torch, numpy y opencv; solo falta lo demás
run([sys.executable, "-m", "pip", "install", "-q",
     "flask==2.3.3", "flask-cors==4.0.0", "flask-limiter==3.5.0",
     "werkzeug==2.3.7", "gunicorn==21.2.0", "ultralytics==8.3.50"])

import torch  # noqa: E402  (después de instalar, a propósito)
print(f"✔ Dependencias listas | GPU disponible: {torch.cuda.is_available()}")

# --------------------------------------------------------------- 3. Pesos
os.makedirs("models", exist_ok=True)
src, dst = Path("../models/yolov8n.pt"), Path("models/yolov8n.pt")
if src.exists() and not dst.exists():
    shutil.copy(src, dst)

from ultralytics import YOLO  # noqa: E402

YOLO(str(dst) if dst.exists() else "yolov8n.pt")  # falla acá, no en el 1er request
print("✔ YOLOv8n cargado")

# ------------------------------------------------------------- 4. Backend
# --workers 1: el estado (active_tasks, stream_stats, latest_uploaded_file) vive
#   en memoria del proceso; con más workers cada request cae en uno distinto.
# --timeout 0: el endpoint MJPEG deja la respuesta abierta indefinidamente y el
#   timeout por defecto (30 s) mataría al worker a mitad del stream.
# --threads 16: cada <img> del stream ocupa un hilo mientras el cliente siga
#   conectado; recargar la pestaña varias veces los acumula y bloquea el upload.
subprocess.run(["pkill", "-f", "gunicorn"], capture_output=True)
time.sleep(1)

backend_log = open(BACKEND_LOG, "w")
subprocess.Popen(
    ["gunicorn", "--bind", f"0.0.0.0:{PORT}", "--workers", "1", "--threads", "16",
     "--timeout", "0", "--log-level", "info", "app:app"],
    stdout=backend_log, stderr=subprocess.STDOUT,
)

import requests  # noqa: E402

for _ in range(40):
    time.sleep(1)
    try:
        if requests.get(f"http://127.0.0.1:{PORT}/health", timeout=2).ok:
            break
    except requests.RequestException:
        pass
else:
    print("✘ El backend no arrancó. Log:")
    print(open(BACKEND_LOG).read()[-3000:])
    raise SystemExit(1)
print(f"✔ Backend escuchando en :{PORT}")

# -------------------------------------------------------------- 5. Túnel
# cloudflared sobre ngrok: no pide cuenta ni token, y no interpone la página de
# advertencia que rompe el <img> del stream MJPEG.
CF_BIN = "/usr/local/bin/cloudflared"
if not os.path.exists(CF_BIN):
    run(["wget", "-q",
         "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
         "-O", CF_BIN])
    os.chmod(CF_BIN, 0o755)

subprocess.run(["pkill", "-f", "cloudflared"], capture_output=True)
time.sleep(1)
if os.path.exists(TUNNEL_LOG):
    os.remove(TUNNEL_LOG)

subprocess.Popen(
    [CF_BIN, "tunnel", "--url", f"http://127.0.0.1:{PORT}",
     "--no-autoupdate", "--logfile", TUNNEL_LOG],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

public_url = None
for _ in range(45):
    time.sleep(1)
    if os.path.exists(TUNNEL_LOG):
        found = re.search(r"https://[-a-z0-9]+\.trycloudflare\.com",
                          open(TUNNEL_LOG).read())
        if found:
            public_url = found.group(0)
            break

if not public_url:
    print("✘ No se obtuvo la URL del túnel. Log:")
    print(open(TUNNEL_LOG).read()[-2000:] if os.path.exists(TUNNEL_LOG) else "sin log")
    raise SystemExit(1)

# ---------------------------------------------------------- 6. Resultado
print("\n" + "=" * 72)
print("  BACKEND PÚBLICO:")
print(f"  {public_url}")
print("\n  ABRE EL FRONTEND YA CONECTADO:")
print(f"  {FRONTEND}/?api={public_url}")
print("=" * 72 + "\n")

for path in ("/health", "/api/results/latest"):
    try:
        r = requests.get(public_url + path, timeout=25)
        print(f"  {r.status_code}  {path}  →  {r.text[:100]}")
    except Exception as exc:
        print(f"  ERR  {path}  →  {exc}")

# ------------------------------------------------- 7. Mantener viva la sesión
# Colab desconecta tras ~90 min sin interacción. Mientras este bucle corra,
# el backend sigue en pie.
print("\nMantén esta celda ejecutándose. Ctrl+M I para detener.\n")
try:
    while True:
        try:
            d = requests.get(f"http://127.0.0.1:{PORT}/api/results/latest", timeout=5).json()
            print(f"[{datetime.now():%H:%M:%S}] archivo={d.get('active_file_id')} "
                  f"densidad={d.get('density')} ánimo={d.get('mood')}")
        except Exception as exc:
            print(f"[{datetime.now():%H:%M:%S}] sin respuesta: {exc}")
        time.sleep(60)
except KeyboardInterrupt:
    print("\nDetenido. El backend sigue vivo hasta que reinicies el entorno.")
