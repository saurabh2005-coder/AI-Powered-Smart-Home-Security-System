# utils/face_utils.py
"""
Wrapper functions for:
- face detection (face_recognition)
- embedding extraction
- matching logic with cosine similarity

Uses face_recognition (dlib) for ease of prototype.
Replace with InsightFace/ArcFace for production.
"""

import numpy as np
import face_recognition
from typing import List, Tuple, Optional

def rgb_from_bgr(img_bgr):
    """Convert cv2 BGR image to RGB for face_recognition."""
    return img_bgr[:, :, ::-1]

def find_face_locations(rgb_img, model="hog"):
    """
    Return face locations in (top, right, bottom, left) format.
    model="hog" is CPU friendly; "cnn" is more accurate but needs GPU/dlib compiled with CUDA.
    """
    return face_recognition.face_locations(rgb_img, model=model)

def get_face_embeddings(rgb_img, face_locations: List[Tuple[int,int,int,int]] = None):
    """
    Given an RGB image (whole image) and optional face_locations, return list of 128-d embeddings.
    Returns list of embeddings aligned with face_locations order.
    """
    return face_recognition.face_encodings(rgb_img, known_face_locations=face_locations)

def normalize_embedding(vec: np.ndarray) -> np.ndarray:
    """L2 normalize embedding vector to unit length."""
    v = np.array(vec, dtype=np.float64)
    norm = np.linalg.norm(v)
    return v / (norm + 1e-10)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between normalized vectors (works even if not normalized)."""
    a_n = a / (np.linalg.norm(a) + 1e-10)
    b_n = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_n, b_n))

def find_best_match(embedding: np.ndarray, known_embeddings: dict):
    """
    known_embeddings: dict[name] -> embedding (np.array)
    Returns (best_name, best_score) or (None, None) if no known embeddings.
    Score is cosine similarity (1.0 best).
    """
    if not known_embeddings:
        return None, None
    best_name = None
    best_score = -1.0
    for name, emb in known_embeddings.items():
        score = cosine_similarity(embedding, emb)
        if score > best_score:
            best_score = score
            best_name = name
    return best_name, best_score
