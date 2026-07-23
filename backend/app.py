"""
Stadium Vision System - Backend API
Sistema de AnÃ¡lisis de Tribunas usando VisiÃ³n Artificial
"""

from flask import Flask, request, jsonify, send_file, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import cv2
import numpy as np
from pathlib import Path
import logging
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import io
from PIL import Image
import threading
import os
import re
import time

# Import custom modules
from vision_analyzer import VisionAnalyzer
from crowd_analyzer import CrowdAnalyzer
from incident_detector import IncidentDetector
from analytics_engine import AnalyticsEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
# Allow all origins and include the ngrok header in allowed headers
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["*", "ngrok-skip-browser-warning"])


# Configuration
UPLOAD_FOLDER = Path('uploads')
RESULTS_FOLDER = Path('results')
MODELS_FOLDER = Path('models')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# Create folders
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER, MODELS_FOLDER]:
    folder.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialize analyzers
vision_analyzer = VisionAnalyzer()
crowd_analyzer = CrowdAnalyzer()
incident_detector = IncidentDetector()
analytics_engine = AnalyticsEngine()

# Store active tasks
active_tasks = {}

# Store real-time stream stats keyed by filename
stream_stats = {}

# Track the most recently uploaded video for the dashboard
latest_uploaded_file = None


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200


# ==================== UPLOAD ENDPOINTS ====================

@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    """Upload video file for analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename

        file.save(filepath)
        logger.info(f"Video uploaded: {filename}")
        
        global latest_uploaded_file
        latest_uploaded_file = filename

        return jsonify({
            'success': True,
            'file_id': filename,
            'filename': filename,
            'size': filepath.stat().st_size,
            'upload_time': datetime.now().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """Upload image file for analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format'}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / filename

        file.save(filepath)
        logger.info(f"Image uploaded: {filename}")

        return jsonify({
            'success': True,
            'file_id': filename,
            'filename': filename,
            'upload_time': datetime.now().isoformat()
        }), 201

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500





# ==================== ANALYSIS ENDPOINTS ====================

@app.route('/api/analyze/video/crowd', methods=['POST'])
def analyze_crowd():
    """Analyze crowd in video"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')

        if not file_id:
            return jsonify({'error': 'No file_id provided'}), 400

        filepath = UPLOAD_FOLDER / file_id
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        # Perform analysis
        task_id = f"crowd_{file_id}_{datetime.now().timestamp()}"
        active_tasks[task_id] = {'status': 'processing', 'progress': 0}

        def process():
            try:
                results = crowd_analyzer.analyze(str(filepath))

                # Save results
                results_file = RESULTS_FOLDER / f"{task_id}_results.json"
                with open(results_file, 'w') as f:
                    json.dump(results, f)

                active_tasks[task_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'results_file': str(results_file)
                }
                logger.info(f"Crowd analysis completed: {task_id}")
            except Exception as e:
                logger.error(f"Analysis error: {str(e)}")
                active_tasks[task_id] = {'status': 'failed', 'error': str(e)}

        # Run in background
        thread = threading.Thread(target=process)
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': 'processing'
        }), 202

    except Exception as e:
        logger.error(f"Crowd analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/video/incidents', methods=['POST'])
def analyze_incidents():
    """Detect incidents in video"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')

        if not file_id:
            return jsonify({'error': 'No file_id provided'}), 400

        filepath = UPLOAD_FOLDER / file_id
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        task_id = f"incident_{file_id}_{datetime.now().timestamp()}"
        active_tasks[task_id] = {'status': 'processing', 'progress': 0}

        def process():
            try:
                results = incident_detector.detect(str(filepath))

                results_file = RESULTS_FOLDER / f"{task_id}_results.json"
                with open(results_file, 'w') as f:
                    json.dump(results, f)

                active_tasks[task_id] = {
                    'status': 'completed',
                    'progress': 100,
                    'results_file': str(results_file)
                }
                logger.info(f"Incident detection completed: {task_id}")
            except Exception as e:
                logger.error(f"Detection error: {str(e)}")
                active_tasks[task_id] = {'status': 'failed', 'error': str(e)}

        thread = threading.Thread(target=process)
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': 'processing'
        }), 202

    except Exception as e:
        logger.error(f"Incident detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze/image/crowd', methods=['POST'])
def analyze_image_crowd():
    """Analyze crowd in single image"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')

        if not file_id:
            return jsonify({'error': 'No file_id provided'}), 400

        filepath = UPLOAD_FOLDER / file_id
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        # Analyze image
        results = crowd_analyzer.analyze_image(str(filepath))

        return jsonify({
            'success': True,
            'results': results,
            'analyzed_at': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== RESULTS ENDPOINTS ====================

@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status and results"""
    try:
        if task_id not in active_tasks:
            return jsonify({'error': 'Task not found'}), 404

        task = active_tasks[task_id]
        return jsonify(task), 200

    except Exception as e:
        logger.error(f"Task fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/<task_id>', methods=['GET'])
def get_results(task_id):
    """Get analysis results"""
    try:
        if task_id not in active_tasks:
            return jsonify({'error': 'Task not found'}), 404

        task = active_tasks[task_id]
        if task['status'] != 'completed':
            return jsonify({'error': 'Task not completed'}), 400

        results_file = task.get('results_file')
        if not results_file or not Path(results_file).exists():
            return jsonify({'error': 'Results file not found'}), 404

        with open(results_file, 'r') as f:
            results = json.load(f)

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Results fetch error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== STATISTICS ENDPOINTS ====================

@app.route('/api/stats/overview', methods=['GET'])
def get_stats_overview():
    """Get system statistics"""
    try:
        stats = {
            'total_files': len(list(UPLOAD_FOLDER.glob('*'))),
            'active_tasks': len([t for t in active_tasks.values() if t['status'] == 'processing']),
            'completed_tasks': len([t for t in active_tasks.values() if t['status'] == 'completed']),
            'failed_tasks': len([t for t in active_tasks.values() if t['status'] == 'failed']),
            'system_time': datetime.now().isoformat()
        }
        return jsonify(stats), 200

    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/results/latest', methods=['GET'])
def get_latest_results():
    """Return latest general results including mood estimation"""
    import random
    try:
        global latest_uploaded_file
        
        # If no file has ever been uploaded, return zeros
        if not latest_uploaded_file:
            return jsonify({
                'people_per_minute': 0,
                'density': 0,
                'mood': 'Sin Datos',
                'active_file_id': None,
                'timestamp': datetime.now().isoformat()
            }), 200
            
        # Try to get stats from the active stream if it's running
        stats = stream_stats.get(latest_uploaded_file, {})
        person_count = stats.get('person_count', 0)
        
        # Derived metrics
        density = round(person_count / 50.0, 2) # Mock density calculation (persons / m^2)
        ppm = person_count + random.randint(-2, 5) if person_count > 0 else 0 # Small variation for active flow
        if ppm < 0: ppm = 0
        
        # Mood estimation logic based on density
        if density == 0:
            mood = 'Sin Datos'
        elif density < 0.3:
            mood = 'Tranquilo'
        elif density < 0.8:
            mood = 'Animado'
        elif density < 1.5:
            mood = 'Eufórico'
        else:
            mood = 'Tenso'

        return jsonify({
            'people_per_minute': ppm,
            'density': density,
            'mood': mood,
            'active_file_id': latest_uploaded_file,
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Latest results error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stream/stop', methods=['POST'])
def stop_stream():
    """Stop the current video analysis and clear the active file"""
    try:
        global latest_uploaded_file
        latest_uploaded_file = None
        return jsonify({'success': True, 'message': 'Análisis detenido'}), 200
    except Exception as e:
        logger.error(f"Stop stream error: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ==================== STREAMING ENDPOINTS ====================

@app.route('/api/stream/video')
def stream_video():
    """Stream video file as MJPEG with YOLO person detections overlaid."""
    filename = request.args.get('filename', '').strip()
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    safe_name = secure_filename(filename)
    filepath = UPLOAD_FOLDER / safe_name

    # Also try without secure_filename in case it altered the name
    if not filepath.exists():
        filepath = UPLOAD_FOLDER / filename
    if not filepath.exists():
        logger.error(f"Stream: file not found: {safe_name} (uploads: {list(UPLOAD_FOLDER.glob('*'))})")
        return jsonify({'error': 'File not found'}), 404

    def generate():
        cap = cv2.VideoCapture(str(filepath))
        if not cap.isOpened():
            logger.error(f"Stream: OpenCV cannot open {filepath}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        target_fps = min(fps, 15) # Limit to 15 FPS to reduce CPU load
        frame_duration = 1.0 / target_fps

        frame_num = 0
        last_bodies = []
        DETECT_EVERY = 12 # Run heavy YOLO inference only every 12 frames

        try:
            while True:
                frame_start = time.time()
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_num = 0

                frame_num += 1

                h, w = frame.shape[:2]
                if w > 640: # Lower resolution to speed up YOLO and transmission
                    scale = 640 / w
                    frame = cv2.resize(frame, (640, int(h * scale)))

                # Run detection every N frames — wrapped so errors never kill the stream
                if frame_num % DETECT_EVERY == 0:
                    try:
                        result = vision_analyzer.detect_persons(frame)
                        last_bodies = result.get('bodies', [])
                        stream_stats[filename] = {
                            'person_count': len(last_bodies),
                            'frame_num': frame_num,
                        }
                    except Exception as det_err:
                        logger.warning(f"Stream detection error (frame {frame_num}): {det_err}")

                annotated = frame.copy()
                for (x, y, bw, bh) in last_bodies:
                    cv2.rectangle(annotated, (x, y), (x + bw, y + bh), (0, 255, 0), 2)

                count = len(last_bodies)
                overlay = annotated.copy()
                cv2.rectangle(overlay, (0, 0), (260, 45), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.55, annotated, 0.45, 0, annotated)
                cv2.putText(annotated, f'Personas: {count}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                ok, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 65])
                if not ok:
                    continue
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

                elapsed = time.time() - frame_start
                sleep_time = max(0.0, frame_duration - elapsed)
                time.sleep(sleep_time)
        except Exception as e:
            logger.error(f"Stream generator error: {e}")
        finally:
            cap.release()

    resp = Response(stream_with_context(generate()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    resp.headers['Cache-Control'] = 'no-cache'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/stream/stats')
def get_stream_stats():
    """Return latest detection stats for a streaming video."""
    filename = request.args.get('filename', '').strip()
    stats = stream_stats.get(filename, {'person_count': 0, 'frame_num': 0})
    return jsonify(stats)


@app.route('/api/video/<path:filename>')
def serve_video(filename):
    """Serve the raw uploaded video file (used as fallback player)."""
    safe_name = secure_filename(filename)
    filepath = UPLOAD_FOLDER / safe_name
    if not filepath.exists():
        filepath = UPLOAD_FOLDER / filename
    if not filepath.exists():
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory(str(UPLOAD_FOLDER.resolve()), safe_name, conditional=True)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Las PaaS (HF Spaces, Cloud Run, Render...) inyectan el puerto por entorno
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Stadium Vision System Backend on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
