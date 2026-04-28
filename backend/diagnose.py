"""
Diagnostic script - run from backend/ folder:
  python diagnose.py <video_path>
"""
import sys
import cv2
import numpy as np
from pathlib import Path

VIDEO = sys.argv[1] if len(sys.argv) > 1 else None
if not VIDEO:
    # pick the most recent upload automatically
    uploads = sorted(Path('../uploads').glob('*.mp4'))
    if not uploads:
        uploads = sorted(Path('uploads').glob('*.mp4'))
    if not uploads:
        print("ERROR: no .mp4 found. Pass video path as argument.")
        sys.exit(1)
    VIDEO = str(uploads[-1])

print(f"\n=== VIDEO: {VIDEO} ===")

cap = cv2.VideoCapture(VIDEO)
if not cap.isOpened():
    print("ERROR: OpenCV cannot open the file")
    sys.exit(1)

total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps   = cap.get(cv2.CAP_PROP_FPS) or 30
w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Resolution : {w}x{h}")
print(f"FPS        : {fps:.1f}")
print(f"Frames     : {total}  (~{total/fps:.1f} s)")

# Extract 3 frames: beginning, middle, near end
sample_positions = [max(0, total//10), total//2, max(0, total - total//10)]
frames = {}
for pos in sample_positions:
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
    ret, f = cap.read()
    if ret:
        frames[pos] = f
cap.release()

print(f"\nExtracted {len(frames)} sample frames at positions: {list(frames.keys())}")

# Load YOLO
print("\n=== YOLO LOAD ===")
try:
    from ultralytics import YOLO
    model_path = 'models/yolov8n.pt'
    if Path(model_path).exists():
        print(f"Loading local weights: {model_path}")
        model = YOLO(model_path)
    else:
        print("Downloading yolov8n.pt ...")
        model = YOLO('yolov8n.pt')
    print("YOLO loaded OK")
except Exception as e:
    print(f"YOLO FAILED TO LOAD: {e}")
    sys.exit(1)

# COCO class names for readability
COCO_NAMES = {0:'person',1:'bicycle',2:'car',3:'motorcycle',4:'airplane',
              5:'bus',7:'truck',14:'bird',15:'cat',16:'dog',17:'horse',
              24:'backpack',26:'handbag',28:'tie',32:'sports ball',41:'cup',
              43:'knife',56:'chair',57:'couch',58:'plant',59:'bed',
              60:'table',62:'tv',63:'laptop',67:'cell phone',73:'book',
              74:'clock',75:'vase',79:'toothbrush'}

out_dir = Path('diagnose_output')
out_dir.mkdir(exist_ok=True)

print("\n=== YOLO INFERENCE (ALL classes, conf=0.01) ===")
for pos, frame in frames.items():
    fh, fw = frame.shape[:2]
    print(f"\n--- Frame {pos} ({fw}x{fh}) ---")

    # Run YOLO with NO class filter, very low conf to see everything
    results = model(frame, conf=0.01, iou=0.3, verbose=False)

    all_detections = []
    for result in results:
        for box in result.boxes:
            cls  = int(box.cls[0])
            conf = float(box.conf[0])
            x1,y1,x2,y2 = map(int, box.xyxy[0].tolist())
            all_detections.append((cls, conf, x1, y1, x2, y2))

    if not all_detections:
        print("  *** ZERO detections at conf=0.01 — frame may be solid color, blurry, or YOLO is broken ***")
    else:
        from collections import Counter
        class_counts = Counter(COCO_NAMES.get(d[0], f'cls{d[0]}') for d in all_detections)
        print(f"  Total detections: {len(all_detections)}")
        print(f"  By class: {dict(class_counts)}")
        persons = [(d[1],d[2],d[3],d[4],d[5]) for d in all_detections if d[0]==0]
        print(f"  Persons (class 0): {len(persons)}")
        if persons:
            confs = [p[0] for p in persons]
            print(f"  Person conf range: {min(confs):.3f} – {max(confs):.3f}")
            sizes = [(p[4]-p[2])*(p[5]-p[3]) for p in persons]
            print(f"  Person box sizes (px²): min={min(sizes)} max={max(sizes)} avg={int(np.mean(sizes))}")

    # Save annotated frame
    annotated = frame.copy()
    for cls, conf, x1, y1, x2, y2 in all_detections:
        color = (0, 255, 0) if cls == 0 else (255, 100, 0)
        cv2.rectangle(annotated, (x1,y1), (x2,y2), color, 2)
        label = f"{COCO_NAMES.get(cls, cls)}:{conf:.2f}"
        cv2.putText(annotated, label, (x1, max(y1-5,10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    out_path = out_dir / f"frame_{pos:06d}.jpg"
    cv2.imwrite(str(out_path), annotated)
    print(f"  Saved → {out_path}")

print(f"\n=== DONE — open '{out_dir}/' to inspect annotated frames ===\n")
