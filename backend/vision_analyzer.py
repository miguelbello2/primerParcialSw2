"""
Vision Analyzer - Core computer vision operations
Analizador de Visión - Operaciones fundamentales de visión por computadora
"""

import cv2
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

PERSON_CLASS_ID = 0  # COCO class 0 = person
_LOCAL_MODEL = Path('models/yolov8n.pt')


def _nms(boxes, scores, iou_threshold=0.4):
    """Pure-numpy non-maximum suppression. Returns indices of kept boxes."""
    if len(boxes) == 0:
        return []
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        ix1 = np.maximum(x1[i], x1[order[1:]])
        iy1 = np.maximum(y1[i], y1[order[1:]])
        ix2 = np.minimum(x2[i], x2[order[1:]])
        iy2 = np.minimum(y2[i], y2[order[1:]])
        inter = np.maximum(0, ix2 - ix1 + 1) * np.maximum(0, iy2 - iy1 + 1)
        iou = inter / (areas[i] + areas[order[1:]] - inter)
        order = order[1:][iou <= iou_threshold]
    return keep


class VisionAnalyzer:
    """Base class for vision analysis using YOLOv8 + OpenCV"""

    def __init__(self):
        Path('models').mkdir(parents=True, exist_ok=True)
        self._yolo = None

    def _get_yolo(self):
        """Lazy-load YOLOv8n. Uses local weights if available, else downloads."""
        if self._yolo is None:
            try:
                from ultralytics import YOLO
                model_arg = str(_LOCAL_MODEL) if _LOCAL_MODEL.exists() else 'yolov8n.pt'
                logger.info("Loading YOLO from: %s", model_arg)
                self._yolo = YOLO(model_arg)
                if not _LOCAL_MODEL.exists():
                    import shutil
                    src = Path(self._yolo.ckpt_path)
                    if src.exists():
                        shutil.copy(src, _LOCAL_MODEL)
                logger.info("YOLOv8n loaded OK — ckpt: %s", getattr(self._yolo, 'ckpt_path', 'unknown'))
            except Exception as e:
                logger.error("Failed to load YOLOv8n: %s", e)
                raise
        return self._yolo

    def detect_persons(self, frame):
        """Detect persons using tiled YOLOv8n inference.

        Splits the frame into overlapping 640×640 tiles and runs YOLO on each
        tile independently, then merges results with NMS.  This is essential
        for aerial/stadium footage where people occupy only a few pixels in the
        full-frame view — a single full-frame pass at any imgsz misses them.
        """
        try:
            model = self._get_yolo()
            h, w = frame.shape[:2]

            TILE = 640      # tile size fed to YOLO
            OVERLAP = 0.2   # 20 % overlap between adjacent tiles

            stride = int(TILE * (1 - OVERLAP))
            raw_boxes = []  # (x1, y1, x2, y2, conf)

            for y0 in range(0, h, stride):
                for x0 in range(0, w, stride):
                    x1t = min(x0, w - TILE) if w >= TILE else 0
                    y1t = min(y0, h - TILE) if h >= TILE else 0
                    x2t = x1t + min(TILE, w)
                    y2t = y1t + min(TILE, h)

                    tile = frame[y1t:y2t, x1t:x2t]
                    if tile.size == 0:
                        continue

                    results = model(tile, classes=[PERSON_CLASS_ID], verbose=False, conf=0.05, iou=0.4)
                    for result in results:
                        for box in result.boxes:
                            bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                            conf_score = float(box.conf[0])
                            # Translate tile-relative coords back to full-frame coords
                            raw_boxes.append((bx1 + x1t, by1 + y1t, bx2 + x1t, by2 + y1t, conf_score))

            # NMS across tiles to remove duplicates on tile borders
            bodies = []
            if raw_boxes:
                boxes_arr = np.array([[b[0], b[1], b[2], b[3]] for b in raw_boxes], dtype=float)
                scores_arr = np.array([b[4] for b in raw_boxes], dtype=float)
                keep = _nms(boxes_arr, scores_arr, iou_threshold=0.4)
                for i in keep:
                    x1b, y1b, x2b, y2b = map(int, boxes_arr[i])
                    bodies.append((x1b, y1b, x2b - x1b, y2b - y1b))
                    logger.debug("  person (%d,%d,%d,%d) conf=%.2f", x1b, y1b, x2b, y2b, scores_arr[i])

            logger.info("detect_persons: frame=%dx%d tiles=%d → %d persons",
                        w, h, len(raw_boxes), len(bodies))
            return {
                'faces': [],
                'bodies': bodies,
                'total_detected': len(bodies)
            }
        except Exception as e:
            logger.error("Person detection error: %s", e)
            return {'faces': [], 'bodies': [], 'total_detected': 0}

    def detect_motion(self, frame1, frame2):
        """Detect motion between two consecutive frames"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

            # Compute difference
            diff = cv2.absdiff(gray1, gray2)

            # Apply threshold
            _, thresh = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

            # Find contours
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Calculate motion magnitude
            motion_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 100)
            motion_percentage = (motion_area / (frame1.shape[0] * frame1.shape[1])) * 100

            return {
                'motion_detected': motion_percentage > 5,
                'motion_percentage': float(motion_percentage),
                'motion_regions': len(contours)
            }
        except Exception as e:
            logger.error(f"Motion detection error: {str(e)}")
            return {'motion_detected': False, 'motion_percentage': 0, 'motion_regions': 0}

    def detect_edges(self, frame):
        """Detect edges using Canny edge detection"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 50, 150)

            edge_percentage = (np.count_nonzero(edges) / edges.size) * 100

            return {
                'edges_detected': edge_percentage > 5,
                'edge_percentage': float(edge_percentage),
                'edges': edges
            }
        except Exception as e:
            logger.error(f"Edge detection error: {str(e)}")
            return {'edges_detected': False, 'edge_percentage': 0, 'edges': None}

    def detect_contours(self, frame):
        """Detect and analyze contours in frame"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            contour_info = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 100:  # Filter small contours
                    perimeter = cv2.arcLength(cnt, True)
                    x, y, w, h = cv2.boundingRect(cnt)
                    contour_info.append({
                        'area': float(area),
                        'perimeter': float(perimeter),
                        'bbox': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)}
                    })

            return {
                'contours_found': len(contour_info),
                'contours': sorted(contour_info, key=lambda x: x['area'], reverse=True)[:10]
            }
        except Exception as e:
            logger.error(f"Contour detection error: {str(e)}")
            return {'contours_found': 0, 'contours': []}

    def color_histogram(self, frame):
        """Analyze color distribution in frame"""
        try:
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])

            return {
                'dominant_colors': {
                    'blue_mean': float(np.mean(frame[:,:,0])),
                    'green_mean': float(np.mean(frame[:,:,1])),
                    'red_mean': float(np.mean(frame[:,:,2]))
                },
                'brightness': float(np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)))
            }
        except Exception as e:
            logger.error(f"Histogram error: {str(e)}")
            return {'dominant_colors': {}, 'brightness': 0}

    def draw_detections(self, frame, detections):
        """Draw detection boxes on frame"""
        try:
            result = frame.copy()

            # Draw faces
            for (x, y, w, h) in detections.get('faces', []):
                cv2.rectangle(result, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Draw bodies
            for (x, y, w, h) in detections.get('bodies', []):
                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)

            return result
        except Exception as e:
            logger.error(f"Drawing error: {str(e)}")
            return frame

    def analyze(self, filepath):
        """Basic analysis of video file"""
        try:
            cap = cv2.VideoCapture(filepath)

            if not cap.isOpened():
                logger.error(f"Cannot open video: {filepath}")
                return {'error': 'Cannot open video'}

            frame_count = 0
            total_persons = 0

            SAMPLE_EVERY = 30
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_count += 1
                if frame_count % SAMPLE_EVERY != 0:
                    continue

                detections = self.detect_persons(frame)
                total_persons += detections['total_detected']

            cap.release()

            return {
                'frames_analyzed': frame_count,
                'average_persons_per_frame': float(total_persons / max(1, frame_count)),
                'total_persons_detected': total_persons
            }
        except Exception as e:
            logger.error(f"Video analysis error: {str(e)}")
            return {'error': str(e)}
