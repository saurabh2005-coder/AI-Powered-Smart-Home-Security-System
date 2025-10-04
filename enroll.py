# enroll.py
"""
Enroll a person by taking images from webcam or folder and POSTing to server /enroll.
Simpler CLI: capture N frames and upload.
"""

import cv2, requests, time, os
from config import ALERT_WEBHOOK
SERVER_ENROLL_URL = os.getenv("SERVER_ENROLL_URL", "http://localhost:8000/enroll")

def capture_images_from_cam(num=8, cam=0):
    cap = cv2.VideoCapture(int(cam))
    images = []
    for i in range(num):
        ret, frame = cap.read()
        if not ret:
            break
        images.append(frame.copy())
        cv2.imshow("enroll capture", frame)
        if cv2.waitKey(300) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    return images

def upload_images(name, images):
    files = []
    import tempfile
    for i, img in enumerate(images):
        path = f"temp_enroll_{i}.jpg"
        import cv2
        cv2.imwrite(path, img)
        files.append(('files', (path, open(path, 'rb'), 'image/jpeg')))
    data = {'name': name}
    r = requests.post(SERVER_ENROLL_URL, data=data, files=files)
    # cleanup
    for _, (path, fh, _) in files:
        fh.close()
        try:
            os.remove(path)
        except:
            pass
    print("Server response:", r.status_code, r.text)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python enroll.py <PersonName> [num_images] [cam_index]")
        sys.exit(1)
    name = sys.argv[1]
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    cam = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    imgs = capture_images_from_cam(num, cam)
    upload_images(name, imgs)
