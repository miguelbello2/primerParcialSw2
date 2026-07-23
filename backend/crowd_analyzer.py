"""
Crowd Analyzer - Analyze crowd density and movement
Analizador de Multitudes - Analizar densidad y movimiento de multitudes
"""

import cv2
import numpy as np
import logging
from vision_analyzer import VisionAnalyzer

logger = logging.getLogger(__name__)


class CrowdAnalyzer(VisionAnalyzer):
    """Analyze crowd density, distribution and movement patterns"""

    def __init__(self):
        super().__init__()
        self.grid_divisions = 4  # 4x4 grid for spatial analysis

    def calculate_crowd_density(self, frame):
        """Calculate crowd density per grid region.

        Runs YOLO once on the full frame, then maps each bounding-box
        centre into the appropriate grid cell.  Running YOLO on tiny
        160×120 crops would miss people who are only a few pixels tall
        in stadium/aerial footage.
        """
        try:
            h, w = frame.shape[:2]
            grid_h = h // self.grid_divisions
            grid_w = w // self.grid_divisions
            region_area = grid_h * grid_w

            # Grid counter: [row][col]
            counts = [[0] * self.grid_divisions for _ in range(self.grid_divisions)]

            # Single YOLO inference on the full frame
            detections = self.detect_persons(frame)
            for (x, y, bw, bh) in detections['bodies']:
                cx, cy = x + bw // 2, y + bh // 2
                gi = min(cy // grid_h, self.grid_divisions - 1)
                gj = min(cx // grid_w, self.grid_divisions - 1)
                counts[gi][gj] += 1

            density_map = []
            for i in range(self.grid_divisions):
                for j in range(self.grid_divisions):
                    count = counts[i][j]
                    density = count / (region_area / 10000) if region_area > 0 else 0
                    density_map.append({
                        'region': f"{i},{j}",
                        'x': j * grid_w,
                        'y': i * grid_h,
                        'person_count': count,
                        'density': float(density)
                    })

            return density_map
        except Exception as e:
            logger.error(f"Density calculation error: {str(e)}")
            return []

    def detect_crowd_anomalies(self, frame):
        """Detect anomalies in crowd distribution"""
        try:
            density_map = self.calculate_crowd_density(frame)

            if not density_map:
                return {'anomalies': [], 'alert_level': 'normal'}

            densities = [d['density'] for d in density_map]
            mean_density = np.mean(densities)
            std_density = np.std(densities)

            anomalies = []
            for region in density_map:
                deviation = (region['density'] - mean_density) / (std_density + 1)
                if abs(deviation) > 2:  # More than 2 std deviations
                    anomalies.append({
                        'region': region['region'],
                        'density': region['density'],
                        'deviation': float(deviation),
                        'status': 'overcrowded' if deviation > 0 else 'sparse'
                    })

            # Determine alert level
            max_deviation = max([abs((d['density'] - mean_density) / (std_density + 1)) for d in density_map], default=0)
            if max_deviation > 3:
                alert_level = 'critical'
            elif max_deviation > 2:
                alert_level = 'warning'
            else:
                alert_level = 'normal'

            return {
                'anomalies': anomalies,
                'alert_level': alert_level,
                'mean_density': float(mean_density),
                'std_density': float(std_density)
            }
        except Exception as e:
            logger.error(f"Anomaly detection error: {str(e)}")
            return {'anomalies': [], 'alert_level': 'error'}

    def track_crowd_flow(self, frame1, frame2):
        """Track crowd flow and movement between frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )

            # Calculate flow magnitude and direction
            magnitude, direction = cv2.cartToPolar(flow[..., 0], flow[..., 1])

            # Aggregate flow statistics
            avg_magnitude = float(np.mean(magnitude))
            avg_direction = float(np.mean(direction))
            max_magnitude = float(np.max(magnitude))

            # Identify flow vectors
            h, w = frame1.shape[:2]
            grid_h = h // 4
            grid_w = w // 4

            flow_vectors = []
            for i in range(4):
                for j in range(4):
                    region_mag = magnitude[i*grid_h:(i+1)*grid_h, j*grid_w:(j+1)*grid_w]
                    region_dir = direction[i*grid_h:(i+1)*grid_h, j*grid_w:(j+1)*grid_w]

                    flow_vectors.append({
                        'region': f"{i},{j}",
                        'avg_magnitude': float(np.mean(region_mag)),
                        'avg_direction': float(np.mean(region_dir)),
                        'dominant_movement': classify_movement(np.mean(region_dir))
                    })

            return {
                'average_magnitude': avg_magnitude,
                'maximum_magnitude': max_magnitude,
                'average_direction': avg_direction,
                'flow_vectors': flow_vectors,
                'motion_detected': avg_magnitude > 1.0
            }
        except Exception as e:
            logger.error(f"Flow tracking error: {str(e)}")
            return {'average_magnitude': 0, 'motion_detected': False}

    def estimate_capacity(self, frame, max_capacity=100000):
        """Estimate stadium capacity usage"""
        try:
            density_map = self.calculate_crowd_density(frame)
            total_persons = sum(d['person_count'] for d in density_map)

            usage_percentage = (total_persons / max_capacity) * 100

            return {
                'total_persons': total_persons,
                'max_capacity': max_capacity,
                'usage_percentage': float(usage_percentage),
                'status': classify_capacity(usage_percentage),
                'regions': density_map
            }
        except Exception as e:
            logger.error(f"Capacity estimation error: {str(e)}")
            return {'total_persons': 0, 'usage_percentage': 0}

    def analyze(self, filepath):
        """Complete crowd analysis on video.

        Muestrea como máximo MAX_SAMPLES fotogramas repartidos por todo el
        video: con un intervalo fijo, un video largo dispara el número de
        inferencias y el análisis nunca termina.
        Returns field names that match what the frontend expects.
        """
        MAX_SAMPLES = 40     # techo de inferencias, sin importar la duración
        MIN_SAMPLE_EVERY = 30  # ~1 muestra/segundo a 30 fps para videos cortos
        DETECT_WIDTH = 1280  # ancho máximo para detectar (ver nota abajo)

        try:
            cap = cv2.VideoCapture(filepath)
            if not cap.isOpened():
                logger.error(f"Cannot open video: {filepath}")
                return {'error': 'Cannot open video'}

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            vid_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            vid_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_s = total_frames / fps if fps > 0 else 0

            # Intervalo adaptativo: se estira en videos largos para no pasar de
            # MAX_SAMPLES inferencias, que es lo que define cuánto tarda todo.
            sample_every = max(MIN_SAMPLE_EVERY, total_frames // MAX_SAMPLES) if total_frames > 0 else MIN_SAMPLE_EVERY
            logger.info(
                "Video info: %s | %dx%d | %.1f fps | %d total frames (~%.1f s) | will sample every %d frames (~%d samples)",
                filepath, vid_w, vid_h, fps, total_frames, duration_s,
                sample_every, max(1, total_frames // sample_every)
            )

            frame_count = 0
            samples_taken = 0
            densities = []
            last_density_map = []
            critical_alerts = []
            warnings_list = []
            prev_frame = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1

                if frame_count % sample_every != 0:
                    continue

                # Detectar sobre una copia reducida, NO sobre el original:
                # detect_persons trocea en tiles de 640px, así que un fotograma
                # 1080p daba 12 tiles y uno 4K daba 40 — el mismo trabajo que a
                # 1280px se hace en 6, sin cambiar lo que el modelo alcanza a ver
                # (yolov8n infiere a 640px de todos modos).
                fh, fw = frame.shape[:2]
                if fw > DETECT_WIDTH:
                    scale = DETECT_WIDTH / fw
                    frame_small = cv2.resize(frame, (DETECT_WIDTH, int(fh * scale)))
                else:
                    frame_small = frame

                density_map = self.calculate_crowd_density(frame_small)
                last_density_map = density_map

                densities_in_frame = [d['density'] for d in density_map]
                total_in_frame = sum(d['person_count'] for d in density_map)
                avg = float(np.mean(densities_in_frame)) if densities_in_frame else 0
                peak = float(np.max(densities_in_frame)) if densities_in_frame else 0
                densities.append(avg)

                logger.info(
                    "Sample #%d (frame %d / %d): %d persons detected, avg_density=%.3f peak=%.3f",
                    samples_taken + 1, frame_count, total_frames, total_in_frame, avg, peak
                )

                if peak > 8:
                    critical_alerts.append({
                        'type': 'HIGH_DENSITY',
                        'frame': frame_count,
                        'severity': 'critical',
                        'density': peak
                    })
                elif peak > 5:
                    warnings_list.append({
                        'type': 'ELEVATED_DENSITY',
                        'frame': frame_count,
                        'density': peak
                    })

                # Optical-flow motion (needs two consecutive sampled frames).
                # Uses the small copy to keep it fast.
                if prev_frame is not None:
                    motion = self.detect_motion(prev_frame, frame_small)
                    if motion.get('motion_percentage', 0) > 20:
                        warnings_list.append({
                            'type': 'HIGH_MOTION',
                            'frame': frame_count,
                        })

                prev_frame = frame_small
                samples_taken += 1

            cap.release()

            logger.info(
                "Crowd analysis DONE: %d total frames read, %d samples taken, "
                "avg_density=%.3f, peak_density=%.3f, critical_alerts=%d",
                frame_count, samples_taken,
                float(np.mean(densities)) if densities else 0,
                float(np.max(densities)) if densities else 0,
                len(critical_alerts)
            )
            return {
                'frames_analyzed': samples_taken,
                'average_density': float(np.mean(densities)) if densities else 0,
                'peak_density': float(np.max(densities)) if densities else 0,
                'density_map': last_density_map,
                'incidents_detected': len(critical_alerts),
                'critical_alerts': critical_alerts,
                'warnings': warnings_list,
            }

        except Exception as e:
            logger.error(f"Crowd analysis error: {str(e)}")
            return {'error': str(e)}

    def analyze_image(self, filepath):
        """Analyze single image"""
        try:
            frame = cv2.imread(filepath)
            if frame is None:
                return {'error': 'Cannot read image'}

            frame = cv2.resize(frame, (1280, 720))

            return {
                'density_map': self.calculate_crowd_density(frame),
                'anomalies': self.detect_crowd_anomalies(frame),
                'capacity': self.estimate_capacity(frame)
            }
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {'error': str(e)}


def classify_movement(angle):
    """Classify movement direction from angle"""
    angle = angle % (2 * np.pi)
    if angle < np.pi / 8 or angle > 15 * np.pi / 8:
        return 'right'
    elif np.pi / 8 <= angle < 3 * np.pi / 8:
        return 'down-right'
    elif 3 * np.pi / 8 <= angle < 5 * np.pi / 8:
        return 'down'
    elif 5 * np.pi / 8 <= angle < 7 * np.pi / 8:
        return 'down-left'
    elif 7 * np.pi / 8 <= angle < 9 * np.pi / 8:
        return 'left'
    elif 9 * np.pi / 8 <= angle < 11 * np.pi / 8:
        return 'up-left'
    elif 11 * np.pi / 8 <= angle < 13 * np.pi / 8:
        return 'up'
    else:
        return 'up-right'


def classify_capacity(percentage):
    """Classify capacity status"""
    if percentage >= 95:
        return 'overcrowded'
    elif percentage >= 80:
        return 'critical'
    elif percentage >= 60:
        return 'high'
    elif percentage >= 40:
        return 'moderate'
    else:
        return 'normal'
