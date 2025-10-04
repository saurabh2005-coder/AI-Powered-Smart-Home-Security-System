# utils/storage.py
import os
from datetime import datetime
from pathlib import Path

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_image(cv2_img, folder, prefix="snapshot"):
    ensure_dir(folder)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")[:-3]
    filename = f"{prefix}_{ts}.jpg"
    filepath = os.path.join(folder, filename)
    import cv2
    cv2.imwrite(filepath, cv2_img)
    return filepath
