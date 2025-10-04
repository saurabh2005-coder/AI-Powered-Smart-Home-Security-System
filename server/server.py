# server/server.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import numpy as np
import os
import io
from PIL import Image
import face_recognition

from server.models import DB, PersonIn  # Absolute import
import config
from utils.storage import save_image   # ✅ Fixed relative import

app = FastAPI(title="Smart Home Security Backend")
db = DB()

@app.post("/alerts")
async def receive_alert(
    camera: str = Form(...),
    reason: str = Form(...),
    similarity: float = Form(None),
    file: UploadFile = File(...)
):
    """
    Receives POSTed alerts from detectors.
    Expects multipart/form-data with:
    - camera: camera id/name
    - reason: string reason, e.g., 'unknown_person'
    - similarity: optional float
    - file: image snapshot
    """
    contents = await file.read()

    # Convert image to BGR (OpenCV style)
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    arr = np.array(img)[:, :, ::-1]

    # Save image
    folder = os.path.join(config.STORAGE_PATH, "events")
    filepath = save_image(arr, folder, prefix=f"{camera}_{reason}")

    event = {
        "camera": camera,
        "timestamp": datetime.utcnow(),
        "image_path": filepath,
        "matched_name": None,
        "similarity": similarity,
        "reason": reason
    }

    await db.add_event(event)
    print("Stored event:", filepath)

    return JSONResponse({"status": "ok", "stored": filepath})


@app.post("/enroll")
async def enroll_person(
    name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """
    Enroll a person: accepts multiple image files and stores embeddings in DB.
    """
    imgs = []

    for f in files:
        contents = await f.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        imgs.append(np.array(img)[:, :, ::-1])  # to BGR

    embeddings = []
    for bgr in imgs:
        rgb = bgr[:, :, ::-1]  # back to RGB
        locs = face_recognition.face_locations(rgb, model="hog")
        if not locs:
            continue
        encs = face_recognition.face_encodings(rgb, known_face_locations=locs)
        if encs:
            embeddings.append(encs[0].tolist())

    if not embeddings:
        return JSONResponse(
            {"status": "error", "reason": "no faces found"},
            status_code=400
        )

    pid = await db.add_person(name, embeddings, metadata={})

    return {
        "status": "ok",
        "person_id": str(pid),
        "count_embeddings": len(embeddings)
    }

@app.get("/embeddings")
async def embeddings():
    embs = await db.get_all_embeddings()
    # return as JSON serializable lists
    return {k: list(v) for k,v in embs.items()}
