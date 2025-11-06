# app.py - FastAPI ML microservice for inference
# - runs a loaded anomaly model (MobileNetV2 head) to predict normal vs intruder
# - runs face recognition using face_utils or fallback
# - returns JSON: { event_id, anomaly: bool, anomaly_score: float, faces: [ {name, distance, location}, ... ] }

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, sys
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import logging

# Try to import preferred face recognition helper (face_recognition wrapper).
# If unavailable, fallback to alternative helper.
try:
    from face_utils import recognize_faces
    logging.info("Using face_utils (face_recognition)")
except Exception:
    try:
        from face_utils_alt import recognize_faces
        logging.info("Using face_utils_alt (OpenCV fallback)")
    except Exception:
        # final fallback - return no faces but keep service up
        def recognize_faces(_):
            return []

# Path to trained anomaly model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'anomaly_mobilenetv2.h5')

app = FastAPI(title="ML Microservice - Smart Home Security")

# Load model at startup if exists
model = None
if os.path.exists(MODEL_PATH):
    model = load_model(MODEL_PATH)
    logging.info(f"Loaded anomaly model from {MODEL_PATH}")
else:
    logging.warning("Anomaly model not found. Run train.py to produce models/anomaly_mobilenetv2.h5")

# Pydantic schema for predict request
class PredictRequest(BaseModel):
    image_path: str
    event_id: int | None = None

# helper: preprocess image for MobileNetV2
def preprocess_for_mobilenet(image_path):
    img = Image.open(image_path).convert('RGB').resize((224,224))    # resize to 224x224
    arr = np.array(img).astype(np.float32) / 255.0                   # scale 0..1
    arr = np.expand_dims(arr, axis=0)                                # add batch dim
    return arr

# helper: predict anomaly score & flag
def predict_image_class(image_path):
    # returns (score, flag) where score is float 0..1 (probability of intruder)
    arr = preprocess_for_mobilenet(image_path)
    pred = model.predict(arr, verbose=0)[0][0]   # sigmoid output
    flag = bool(pred > 0.5)                     # threshold 0.5 (tuneable)
    return float(pred), flag

@app.post('/predict')
def predict(req: PredictRequest):
    image_path = req.image_path
    if not os.path.exists(image_path):
        raise HTTPException(status_code=400, detail="image_path not found")

    # 1) face recognition
    try:
        faces = recognize_faces(image_path)   # list of dicts or []
    except Exception as e:
        logging.exception("face recognition failed")
        faces = []

    # 2) anomaly detection (if model available)
    anomaly_score = None
    anomaly_flag = False
    if model is not None:
        try:
            score, flag = predict_image_class(image_path)
            anomaly_score = score
            anomaly_flag = flag
        except Exception:
            logging.exception("anomaly prediction failed")

    result = {
        "event_id": req.event_id,
        "anomaly": anomaly_flag,
        "anomaly_score": anomaly_score,
        "faces": faces
    }
    return result

# optional health endpoint
@app.get('/health')
def health():
    return {"ok": True, "model_loaded": model is not None}
