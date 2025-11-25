import os
import threading
import requests
import ffmpeg
from datetime import datetime
import cv2

try:
    from face_utils import is_known_face_from_image
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    is_known_face_from_image = None

# Local storage folder path
LOCAL_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(LOCAL_STORAGE_PATH, exist_ok=True)

API_ENDPOINT = "http://127.0.0.1:5000/motion_detected"

def handle_detection(path_to_file):
    """Handles processing and notification after a detection event."""
    def action_thread(path_to_file):
        # Convert input path to full path
        full_input_path = os.path.join(LOCAL_STORAGE_PATH, path_to_file)
        output_path = os.path.join(LOCAL_STORAGE_PATH, path_to_file.split(".mp4")[0] + "-out.mp4")

        # Convert to 720p and save locally
        ffmpeg.input(full_input_path).output(output_path, vf='scale=-1:720').run()
        os.remove(full_input_path)

        # Send notification with local file path (URL)
        # Before notifying, check whether the video contains a registered face (if available)
        should_notify = True
        if FACE_RECOGNITION_AVAILABLE:
            try:
                print(f"[DEBUG] Checking face recognition for {output_path}")
                cap = cv2.VideoCapture(output_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
                mid_frame_idx = max(0, frame_count // 2)
                print(f"[DEBUG] Video frame count: {frame_count}, checking frame at index: {mid_frame_idx}")
                cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_idx)
                ret, frame = cap.read()
                temp_frame_path = None
                try:
                    if ret:
                        temp_frame_path = os.path.join(LOCAL_STORAGE_PATH, "_temp_frame.jpg")
                        cv2.imwrite(temp_frame_path, frame)
                        matched_name, dist = is_known_face_from_image(temp_frame_path)
                        print(f"[DEBUG] Face recognition result: matched_name={matched_name}, dist={dist}")
                        if matched_name is None:
                            # No registered face found; NOTIFY (unknown person)
                            print("[DEBUG] No registered face found - WILL NOTIFY")
                            should_notify = True
                        else:
                            # Registered face matched; DO NOT NOTIFY
                            print(f"[DEBUG] Registered face matched: {matched_name} - NOT NOTIFYING")
                            should_notify = False
                    else:
                        # if frame extraction failed, fall back to notifying
                        print("[DEBUG] Frame extraction failed - will notify")
                        should_notify = True
                finally:
                    cap.release()
                    if temp_frame_path and os.path.exists(temp_frame_path):
                        os.remove(temp_frame_path)
            except Exception as e:
                # If face recognition fails for any reason, fall back to notifying
                print(f"[DEBUG] Face recognition exception: {e}. Notifying anyway.")
                import traceback
                traceback.print_exc()
                should_notify = True
        else:
            print("[DEBUG] Face recognition not available - will notify")

        print(f"[DEBUG] Final decision: should_notify={should_notify}")
        if should_notify:
            url = f"http://127.0.0.1:5000/videos/{os.path.basename(output_path)}"
            data = {"url": url}
            print(f"[DEBUG] Sending notification: {url}")
            requests.post(API_ENDPOINT, json=data)
        else:
            print("[DEBUG] Skipping notification")

    thread = threading.Thread(target=action_thread, args=(path_to_file,))
    thread.start()


def list_videos_in_date_range(start_date, end_date, extension=".mp4"):
    """List all locally stored videos in the given date range."""
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    matching_files = []

    for filename in os.listdir(LOCAL_STORAGE_PATH):
        if filename.endswith(extension):
            file_path = os.path.join(LOCAL_STORAGE_PATH, filename)
            created_time = datetime.fromtimestamp(os.path.getmtime(file_path))

            if start_datetime <= created_time <= end_datetime:
                matching_files.append({
                    "url": f"http://127.0.0.1:5000/videos/{filename}",
                    "date": created_time
                })

    return matching_files
