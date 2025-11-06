# face_utils.py - use face_recognition to load known faces and match incoming images
import os
import face_recognition

# Directory layout: known_faces/<PersonName>/*.jpg
KNOWN_DIR = os.path.join(os.path.dirname(__file__), 'known_faces')

def load_known_encodings():
    """Load known face encodings into a dict {name: [encodings,...]}"""
    known = {}
    os.makedirs(KNOWN_DIR, exist_ok=True)
    for person in os.listdir(KNOWN_DIR):
        pdir = os.path.join(KNOWN_DIR, person)
        if not os.path.isdir(pdir):
            continue
        encs = []
        for fname in os.listdir(pdir):
            if not fname.lower().endswith(('.jpg','.jpeg','.png')): continue
            img = face_recognition.load_image_file(os.path.join(pdir, fname))
            enc = face_recognition.face_encodings(img)
            if enc:
                encs.append(enc[0])
        if encs:
            known[person] = encs
    return known

def recognize_faces(image_path, tolerance=0.5):
    """
    Returns list of dicts per face: {name, distance, location}
    - distance is the face_distance returned by face_recognition
    - location is (top,right,bottom,left)
    """
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    known = load_known_encodings()
    results = []
    for enc, loc in zip(encodings, face_locations):
        best_name = "unknown"
        best_dist = 1.0
        for name, enc_list in known.items():
            dists = face_recognition.face_distance(enc_list, enc)
            if len(dists) == 0: continue
            min_d = float(dists.min())
            if min_d < best_dist:
                best_dist = min_d
                best_name = name
        if best_dist <= tolerance:
            results.append({"name": best_name, "distance": best_dist, "location": loc})
        else:
            results.append({"name": "unknown", "distance": best_dist, "location": loc})
    return results
