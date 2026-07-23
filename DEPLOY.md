# Despliegue gratuito en la nube

El sistema son dos piezas con necesidades muy distintas:

| Pieza | Qué es | Dónde vive |
|---|---|---|
| Frontend | React (CRA), estático | **Vercel** (gratis, ya desplegado) |
| Backend | Flask + PyTorch + YOLOv8n | **Google Colab** (sin tarjeta) o **Cloud Run** (con tarjeta) |

El backend no cabe en Vercel: son funciones serverless sin PyTorch, sin proceso
persistente y con límite de 10 s por request, mientras que el endpoint MJPEG
(`/api/stream/video`) mantiene la conexión abierta indefinidamente.

---

## Lo primero: el frontend ya no necesita rebuild

Antes, la URL del backend se congelaba en el build de Vercel
(`REACT_APP_API_URL`), así que cada sesión nueva de Colab —con su URL nueva—
obligaba a redeployar. Ahora [frontend/src/api.js](frontend/src/api.js) la
resuelve **en el navegador**, en este orden:

1. `?api=https://algo.trycloudflare.com` en la URL (se guarda y se limpia sola)
2. `localStorage` (lo guardado antes, o el botón «Cambiar» del dashboard)
3. `REACT_APP_API_URL` del build (para un backend con URL estable)
4. `http://localhost:5000` (desarrollo local)

En la práctica: **abres `https://tu-app.vercel.app/?api=<URL-del-backend>` una
vez y queda memorizado.** O usas el botón «Cambiar» al pie del dashboard.

---

## Opción A — Backend en Google Colab (tu flujo actual, mejorado)

Gratis, con GPU T4, sin tarjeta. El precio es que la sesión muere y hay que
relanzarla.

1. Sube [deploy/colab_backend.ipynb](deploy/colab_backend.ipynb) a
   [colab.research.google.com](https://colab.research.google.com) (`Archivo →
   Subir cuaderno`), o ábrelo desde GitHub.
2. `Entorno de ejecución → Cambiar tipo de entorno de ejecución → T4 GPU`.
3. Ejecuta las celdas en orden. La celda 5 imprime la URL pública.
4. Abre `https://tu-app.vercel.app/?api=<esa-URL>`.
5. **Deja corriendo la celda 7**: mientras esté activa, el backend sigue vivo.

Dos cambios respecto a lo que tenías:

- **Cloudflare Tunnel en vez de ngrok.** No pide cuenta ni token, y sobre todo
  no interpone la página de advertencia del plan gratuito de ngrok —esa
  advertencia es exactamente lo que rompe el `<img>` del stream MJPEG, y es la
  razón del parche `ngrok-skip-browser-warning` que había repartido por el
  frontend (una cabecera que un `<img>` no puede enviar).
- **gunicorn con `--timeout 0` y 1 worker.** Con el timeout por defecto (30 s)
  gunicorn mata al worker a mitad del stream; con más de 1 worker, el estado en
  memoria (`active_tasks`, `stream_stats`, `latest_uploaded_file`) queda repartido
  entre procesos y el dashboard lee datos vacíos.

**Límites reales:** ~90 min de inactividad y 12 h máximo por sesión. Al caerse,
vuelve a ejecutar el cuaderno y pega la URL nueva.

---

## Opción B — Backend en Google Cloud Run (URL estable)

Free tier real (2M requests/mes, ~50 h de cómputo activo con 2 GB de RAM) y URL
estable, pero **exige tarjeta de crédito** para activar billing —no te cobran
mientras no superes el límite, aunque tenerla registrada es un requisito
inevitable.

```bash
gcloud run deploy stadium-vision \
  --source . --dockerfile Dockerfile.backend \
  --region us-central1 \
  --memory 2Gi --cpu 2 \
  --max-instances 1 --timeout 3600 \
  --allow-unauthenticated
```

Tres banderas no son opcionales:

- `--max-instances 1`: el estado vive en memoria del proceso; si Cloud Run
  escala a dos instancias, el upload cae en una y el dashboard lee de la otra.
- `--timeout 3600`: el máximo. El stream MJPEG cuenta como un request abierto,
  así que se corta al llegar a esa hora.
- `--memory 2Gi`: con menos, PyTorch muere al cargar el modelo.

Con URL estable conviene fijarla en Vercel:
`Settings → Environment Variables → REACT_APP_API_URL` y redeploy.

### Por qué NO Hugging Face Spaces

Lo era, y de hecho el [Dockerfile.backend](Dockerfile.backend) quedó preparado
para Spaces (uid 1000, puerto 7860, `YOLO_CONFIG_DIR` escribible). Pero HF cambió
la política: **crear un Space de Docker o Gradio ahora requiere plan de pago**
(PRO en cuentas personales). Solo los Static Spaces siguen gratis, y esos no
ejecutan Python.

Esas mismas opciones del Dockerfile son inocuas en cualquier otro host —el
puerto se toma de `$PORT` y correr sin root es buena práctica— así que sirve
igual para Cloud Run, Fly o Docker local.

### Por qué NO Render / Koyeb

Su tier gratuito da **512 MB de RAM**; solo PyTorch ya no entra y el contenedor
muere en el arranque. Además Render duerme el servicio a los 15 min de
inactividad con cold starts de 30-60 s.

---

## Configuración de Vercel (revisada)

- **Root Directory: `frontend`** — obligatorio, el `package.json` no está en la
  raíz del repo. Se configura en `Settings → General`, no en `vercel.json`
  (`rootDirectory` no es una propiedad válida de ese archivo).
- El `vercel.json` de la raíz se movió a
  [frontend/vercel.json](frontend/vercel.json), porque Vercel lo busca dentro
  del Root Directory: en la raíz simplemente no se leía.
- `REACT_APP_API_URL` es ahora **opcional**. Útil solo con backend de URL
  estable (opción B); con Colab, deja que mande el `?api=`.
- **`package-lock.json` regenerado.** El commiteado estaba desincronizado con
  `package.json` y `npm ci` fallaba en seco (`lock file's ajv@6.15.0 does not
  satisfy ajv@8.20.0`). Vercel sobrevivía porque cae a `npm install`, pero era
  una bomba de relojería: cualquier build que use `npm ci` —CI propio, Docker,
  o un cambio de política de Vercel— habría reventado.

---

## Qué cambió en el modelo

Bajamos de **YOLOv8l a YOLOv8n** ([backend/vision_analyzer.py](backend/vision_analyzer.py)),
y con eso los tiles pasan de 480 px inferidos a 960 px (un upscale 2× que en un
modelo nano solo agregaba ruido) a 640/640 sin reescalado. El umbral de confianza
sube de `0.05` a `0.15`: a 0.05 la variante nano marca como personas casi
cualquier mancha de la tribuna.

Traducción: **menos precisión en multitudes densas y lejanas**, a cambio de un
stream que se ve fluido en vez de avanzar a ~0.2 FPS. Si algún día pasas a una
GPU permanente, revertir es cambiar `MODEL_NAME` y los tres valores de
`detect_persons`.

---

## Verificación

```bash
curl https://<tu-backend>/health
curl https://<tu-backend>/api/results/latest
```

Ambos deben responder `200` con JSON. Luego, en el frontend, el punto junto a
«Backend:» al pie del dashboard queda verde si hay conexión y rojo si no.

## Problemas frecuentes

| Síntoma | Causa |
|---|---|
| «No se pudo conectar con el servidor» | La URL del backend cambió (sesión de Colab nueva). Actualízala con «Cambiar». |
| El video no carga pero las métricas sí | Interstitial de ngrok bloqueando el `<img>`. Usa Cloudflare Tunnel. |
| Métricas siempre en cero | Más de un worker de gunicorn: el estado está en memoria. Debe ser `--workers 1`. |
| El stream se corta a los 30 s | Falta `--timeout 0` en gunicorn. |
| Los archivos subidos desaparecen | Disco efímero en Colab/Spaces. Es esperado: vuelve a subir el video. |
