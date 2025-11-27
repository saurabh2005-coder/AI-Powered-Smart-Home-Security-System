import cv2 as cv
import numpy as np
import threading
import datetime
import os
import time
import requests
from storage import handle_detection

class Camera:
    net = cv.dnn.readNetFromCaffe('models/deploy.protxt', 'models/mobilenet_iter_73000.caffemodel')
    cap = cv.VideoCapture(0)
    out = None

    def __init__(self):
        self.armed = False
        self.camera_thread = None
    
    def arm(self):
        if not self.armed and not self.camera_thread:
            self.camera_thread = threading.Thread(target=self.run)
        
        self.camera_thread.start()
        self.armed = True
        print("Camera armed.")

    def disarm(self):
        self.armed = False
        self.camera_thread = None
        print("Camera disarmed.")

    def run(self):
        person_detected = False
        non_detected_counter = 0
        current_recording_name = None

        # For camera-movement forced recordings
        move_out = None
        move_recording_name = None
        move_end_time = 0
        last_move_time = 0

        Camera.cap = cv.VideoCapture(0)

        print("Camera started...")
        prev_gray = None
        MOVE_THRESHOLD = 20.0  # tune this if needed
        while self.armed:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            # --- Camera movement detection (global motion) ---
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            if prev_gray is None:
                prev_gray = gray
            else:
                diff = cv.absdiff(prev_gray, gray)
                mean_diff = np.mean(diff)
                # if large global change detected, treat as camera movement
                if mean_diff > MOVE_THRESHOLD and (time.time() - last_move_time) > 30:
                    last_move_time = time.time()
                    now = datetime.datetime.now()
                    formatted_now = now.strftime("%d-%m-%y-%H-%M-%S")
                    print("Camera movement detected at", formatted_now, "mean_diff=", mean_diff)
                    videos_dir = os.path.join(os.path.dirname(__file__), "videos")
                    os.makedirs(videos_dir, exist_ok=True)
                    move_recording_name = f"{formatted_now}-move.mp4"
                    move_recording_path = os.path.join(videos_dir, move_recording_name)
                    fourcc = cv.VideoWriter_fourcc(*'mp4v')
                    move_out = cv.VideoWriter(move_recording_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
                    move_end_time = time.time() + 10.0  # record for 10 seconds

                    # send an immediate, event-only notification (no URL yet)
                    try:
                        requests.post("http://127.0.0.1:5000/motion_detected", json={"event": "camera_moved"}, timeout=2)
                    except Exception:
                        pass

                prev_gray = gray

            # --- Person detection (existing code) ---
            blob = cv.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
            self.net.setInput(blob)
            detections = self.net.forward()
            person_detected = False

            for i in range(detections.shape[2]):
                # Extract the confidence
                confidence = detections[0, 0, i, 2]

                # Get the label for the class number and set its color
                idx = int(detections[0, 0, i, 1])

                # Check if the detection is of a person and its confidence is greater than the minimum confidence
                if idx == 15 and confidence > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                    (startX, startY, endX, endY) = box.astype("int")
                    # Validate coordinates
                    if startX >= 0 and startY >= 0 and endX > startX and endY > startY:
                        cv.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
                    person_detected = True

            # If a person is detected, start/continue recording
            if person_detected:
                non_detected_counter = 0  # reset the counter
                if self.out is None:  # if VideoWriter isn't initialized, initialize it
                    now = datetime.datetime.now()
                    formatted_now = now.strftime("%d-%m-%y-%H-%M-%S")
                    print("Person motion detected at", formatted_now)
                    videos_dir = os.path.join(os.path.dirname(__file__), "videos")
                    os.makedirs(videos_dir, exist_ok=True)
                    current_recording_name = f"{formatted_now}.mp4"
                    current_recording_path = os.path.join(videos_dir, current_recording_name)
                    fourcc = cv.VideoWriter_fourcc(*'mp4v')  # or use 'XVID'
                    self.out = cv.VideoWriter(current_recording_path, fourcc, 20.0, (frame.shape[1], frame.shape[0]))

                # Write the frame into the person detection file
                self.out.write(frame)

            # If no person is detected, stop recording after 50 frames
            else:
                non_detected_counter += 1  # increment the counter
                if non_detected_counter >= 50:  # if 50 frames have passed without a detection
                    if self.out is not None:  # if VideoWriter is initialized, release it
                        self.out.release()
                        self.out = None  # set it back to None
                        handle_detection(current_recording_name)
                        current_recording_name = None

            # If a move recording is active, write frames until end time
            if move_out is not None:
                move_out.write(frame)
                if time.time() >= move_end_time:
                    try:
                        move_out.release()
                    except Exception:
                        pass
                    move_out = None
                    # process and force notify for move recording
                    try:
                        handle_detection(move_recording_name, force_notify=True)
                    except Exception:
                        pass
                    move_recording_name = None

        # cleanup on exit
        if self.out is not None:  # if VideoWriter is initialized, release it
            self.out.release()
            self.out = None  # set it back to None
            handle_detection(current_recording_name)
            current_recording_name = None

        if move_out is not None:
            try:
                move_out.release()
            except Exception:
                pass
            try:
                handle_detection(move_recording_name, force_notify=True)
            except Exception:
                pass
            move_recording_name = None

        self.cap.release()
        print("Camera released...")

    def __del__(self):
        self.cap.release()
        if self.out is not None:
            self.out.release()

