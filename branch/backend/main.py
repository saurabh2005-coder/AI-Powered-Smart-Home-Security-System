from camera import Camera
from notifications import send_notification
from storage import list_videos_in_date_range
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory
from flask import Response
import cv2
from face_utils import register_face, list_registered
import tempfile
import os
from datetime import datetime



app = Flask(__name__)
CORS(app)

camera = Camera()
# Get absolute path to backend/videos
VIDEO_DIR = os.path.join(os.path.dirname(__file__), "videos")
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")


@app.route('/arm', methods=['POST'])
def arm():
    camera.arm()
    return jsonify(message="System armed."), 200

@app.route('/disarm', methods=['POST'])
def disarm():
    camera.disarm()
    return jsonify(message="System disarmed."), 200


@app.route('/live')
def live():
    def generate_frames():
        cap = camera.cap
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/videos/<path:filename>')
# def serve_video(filename):
#     return send_from_directory(VIDEO_DIR, filename)

@app.route("/videos", methods=["GET"])
def list_videos():
    if not os.path.exists(VIDEO_FOLDER):
        return jsonify({"error": f"Video folder not found at {VIDEO_FOLDER}"}), 404

    files = [f for f in os.listdir(VIDEO_FOLDER) if f.endswith(".mp4")]
    return jsonify(files)

@app.route("/videos/<filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)


@app.route('/get-armed', methods=['GET'])
def get_armed():
    return jsonify(armed=camera.armed), 200

@app.route('/motion_detected', methods=['POST'])
def motion_detected():
    data = request.get_json()

    if 'url' in data:
        print("URL: ", data['url'])
        send_notification(data["url"])
    else:
        print("'url' not in incoming data")

    return jsonify({}), 201


@app.route('/register-face', methods=['POST'])
def register_face_route():
    # Accept multipart form: name and image file
    if 'name' not in request.form or 'image' not in request.files:
        return jsonify({"error": "name and image required"}), 400

    name = request.form.get('name')
    img_file = request.files['image']
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img_file.save(tmp.name)
    try:
        success, msg = register_face(name, tmp.name)
        if not success:
            return jsonify({"error": msg}), 400
        return jsonify({"message": msg}), 200
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


@app.route('/list-registered', methods=['GET'])
def list_registered_route():
    names = list_registered()
    return jsonify({"registered": names}), 200

@app.route('/get-logs')
def get_logs():
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")

    # Fetch all .mp4 files in videos folder
    all_files = [
        f for f in os.listdir(VIDEO_DIR)
        if f.endswith(".mp4")
    ]

    logs = []
    for f in sorted(all_files, reverse=True):  # latest first
        file_path = os.path.join(VIDEO_DIR, f)
        modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        formatted_date = modified_time.strftime("%Y-%m-%d %H:%M:%S")

        # Only include videos between start and end (if given)
        if start_date and end_date:
            if not (start_date <= formatted_date[:10] <= end_date):
                continue

        logs.append({
            "url": f"http://127.0.0.1:5000/videos/{f}",
            "date": formatted_date
        })

    return jsonify({"logs": logs})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

