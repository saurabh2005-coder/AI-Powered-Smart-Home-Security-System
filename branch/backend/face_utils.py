import os
import numpy as np
import json
import face_recognition

BASE_DIR = os.path.dirname(__file__)
KNOWN_DIR = os.path.join(BASE_DIR, "known_faces")
os.makedirs(KNOWN_DIR, exist_ok=True)

METADATA_PATH = os.path.join(KNOWN_DIR, "metadata.json")

def _load_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            return json.load(f)
    return {}

def _save_metadata(md):
    with open(METADATA_PATH, "w") as f:
        json.dump(md, f)

def register_face(name, image_path):
    """Register a face by name from an image file. Returns True if registered."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return False, "No face found in image"

    encoding = encodings[0]
    filename = f"{name}.npy"
    filepath = os.path.join(KNOWN_DIR, filename)
    np.save(filepath, encoding)

    md = _load_metadata()
    md[name] = filename
    _save_metadata(md)
    return True, "Registered"

def list_registered():
    md = _load_metadata()
    return list(md.keys())

def load_known_encodings():
    md = _load_metadata()
    names = []
    encs = []
    for name, fname in md.items():
        path = os.path.join(KNOWN_DIR, fname)
        if os.path.exists(path):
            enc = np.load(path)
            names.append(name)
            encs.append(enc)
    return names, encs

def is_known_face_from_image(image_path, tolerance=0.6):
    """Return (matched_name or None, distance)"""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return None, None
    enc = encodings[0]
    names, encs = load_known_encodings()
    if not encs:
        return None, None
    results = face_recognition.compare_faces(encs, enc, tolerance=tolerance)
    # compute distances
    dists = face_recognition.face_distance(encs, enc)
    for matched, dist, name in zip(results, dists, names):
        if matched:
            return name, float(dist)
    return None, None
