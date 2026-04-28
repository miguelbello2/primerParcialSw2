"""
Incident Detector - Detect anomalies and potential incidents
Detector de Incidentes - Detectar anomalías e incidentes potenciales
"""

import cv2
import numpy as np
import logging
from vision_analyzer import VisionAnalyzer

logger = logging.getLogger(__name__)


class IncidentDetector(VisionAnalyzer):
    """Detect potential incidents and anomalies in stadium"""

    def __init__(self):
        super().__init__()
        self.motion_history = []
        self.max_history = 30

    def detect_sudden_movement(self, frame1, frame2):
        """Detect sudden movement/panic"""
        try:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            diff = cv2.absdiff(gray1, gray2)
            _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

            # Dilate to connect components
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dilated = cv2.dilate(thresh, kernel, iterations=2)

            # Find contours
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            large_movements = 0
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 1000:  # Significant movement
                    large_movements += 1

            movement_intensity = len(contours)
            panic_detected = movement_intensity > 50

            return {
                'panic_detected': panic_detected,
                'movement_intensity': movement_intensity,
                'large_movements': large_movements
            }
        except Exception as e:
            logger.error(f"Sudden movement detection error: {str(e)}")
            return {'panic_detected': False, 'movement_intensity': 0}

    def detect_falling_objects(self, frame):
        """Detect falling or thrown objects"""
        try:
            edges = self.detect_edges(frame)['edges']
            if edges is None:
                return {'objects_detected': 0, 'alert': False}

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            falling_objects = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 100 < area < 1000:  # Medium-sized objects
                    x, y, w, h = cv2.boundingRect(cnt)
                    # Look for vertical movement patterns
                    aspect_ratio = float(w) / h if h > 0 else 0

                    falling_objects.append({
                        'area': float(area),
                        'position': {'x': int(x), 'y': int(y)},
                        'size': {'w': int(w), 'h': int(h)},
                        'aspect_ratio': float(aspect_ratio)
                    })

            return {
                'objects_detected': len(falling_objects),
                'alert': len(falling_objects) > 5,
                'objects': falling_objects[:10]
            }
        except Exception as e:
            logger.error(f"Object detection error: {str(e)}")
            return {'objects_detected': 0, 'alert': False}

    def detect_light_changes(self, frame):
        """Detect sudden light changes (flares, strobes, etc.)"""
        try:
            brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

            self.motion_history.append(brightness)
            if len(self.motion_history) > self.max_history:
                self.motion_history.pop(0)

            if len(self.motion_history) < 5:
                return {'light_change_detected': False, 'change_intensity': 0}

            # Calculate brightness variance
            variance = np.var(self.motion_history[-5:])
            sudden_change = variance > 1000

            # Check for flashing pattern
            recent = self.motion_history[-10:]
            brightness_diffs = [abs(recent[i] - recent[i-1]) for i in range(1, len(recent))]
            flashing = sum(1 for d in brightness_diffs if d > 30) > 3

            return {
                'light_change_detected': sudden_change,
                'change_intensity': float(variance),
                'flashing_detected': flashing,
                'brightness': float(brightness)
            }
        except Exception as e:
            logger.error(f"Light change detection error: {str(e)}")
            return {'light_change_detected': False, 'change_intensity': 0}

    def detect_barriers_down(self, frame):
        """Detect if safety barriers are compromised"""
        try:
            # Look for horizontal lines (barriers)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)

            # Hough line detection
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

            if lines is None:
                return {'barrier_status': 'unknown', 'lines_detected': 0}

            horizontal_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Check if roughly horizontal
                if abs(y2 - y1) < 20:
                    horizontal_lines += 1

            barrier_compromised = horizontal_lines < 3

            return {
                'barrier_status': 'compromised' if barrier_compromised else 'intact',
                'lines_detected': int(horizontal_lines),
                'alert': barrier_compromised
            }
        except Exception as e:
            logger.error(f"Barrier detection error: {str(e)}")
            return {'barrier_status': 'unknown', 'alert': False}

    def detect_unusual_patterns(self, frame):
        """Detect unusual crowd patterns"""
        try:
            # Convert to HSV for color-based analysis
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Detect red colors (often clothing, flags)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            red_mask = cv2.bitwise_or(mask1, mask2)

            red_percentage = (cv2.countNonZero(red_mask) / (frame.shape[0] * frame.shape[1])) * 100

            # Detect blue colors
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([130, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            blue_percentage = (cv2.countNonZero(blue_mask) / (frame.shape[0] * frame.shape[1])) * 100

            return {
                'red_percentage': float(red_percentage),
                'blue_percentage': float(blue_percentage),
                'color_dominance': 'red' if red_percentage > blue_percentage else 'blue',
                'anomaly_detected': red_percentage > 30 or blue_percentage > 30
            }
        except Exception as e:
            logger.error(f"Pattern detection error: {str(e)}")
            return {'anomaly_detected': False}

    def analyze(self, filepath):
        """Complete incident detection on video"""
        try:
            cap = cv2.VideoCapture(filepath)

            if not cap.isOpened():
                logger.error(f"Cannot open video: {filepath}")
                return {'error': 'Cannot open video'}

            results = {
                'total_frames': 0,
                'incidents_detected': [],
                'anomaly_count': 0,
                'critical_alerts': [],
                'warnings': []
            }

            frame_count = 0
            prev_frame = None

            while frame_count < 300:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize for faster processing
                frame = cv2.resize(frame, (640, 480))

                # Check light changes
                if frame_count % 5 == 0:
                    light_analysis = self.detect_light_changes(frame)
                    if light_analysis['light_change_detected']:
                        results['warnings'].append({
                            'type': 'light_change',
                            'frame': frame_count,
                            'severity': 'warning'
                        })

                # Check for unusual patterns
                if frame_count % 10 == 0:
                    pattern_analysis = self.detect_unusual_patterns(frame)
                    if pattern_analysis['anomaly_detected']:
                        results['anomaly_count'] += 1
                        results['warnings'].append({
                            'type': 'unusual_pattern',
                            'frame': frame_count,
                            'analysis': pattern_analysis
                        })

                # Check barriers
                if frame_count % 30 == 0:
                    barrier_analysis = self.detect_barriers_down(frame)
                    if barrier_analysis['alert']:
                        results['critical_alerts'].append({
                            'type': 'barrier_compromise',
                            'frame': frame_count,
                            'severity': 'critical'
                        })

                # Check for sudden movement
                if prev_frame is not None and frame_count % 15 == 0:
                    movement_analysis = self.detect_sudden_movement(prev_frame, frame)
                    if movement_analysis['panic_detected']:
                        results['critical_alerts'].append({
                            'type': 'panic_movement',
                            'frame': frame_count,
                            'severity': 'critical',
                            'intensity': movement_analysis['movement_intensity']
                        })

                # Check for falling objects
                if frame_count % 20 == 0:
                    object_analysis = self.detect_falling_objects(frame)
                    if object_analysis['alert']:
                        results['warnings'].append({
                            'type': 'falling_objects',
                            'frame': frame_count,
                            'count': object_analysis['objects_detected']
                        })

                prev_frame = frame
                frame_count += 1

            cap.release()

            results['total_frames'] = frame_count
            results['incidents_detected'] = len(results['critical_alerts'])

            logger.info(f"Incident detection completed: {filepath}")
            return results

        except Exception as e:
            logger.error(f"Incident detection error: {str(e)}")
            return {'error': str(e)}
