import cv2
import threading
import time

class CameraService:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = False
        self.frame = None

    def start_camera(self):
        if not self.cap.isOpened():
            self.cap.open(self.camera_index)
        self.running = True
        threading.Thread(target=self._capture_frames, daemon=True).start()

    def stop_camera(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()

    def _capture_frames(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            time.sleep(0.03)

    def get_frame(self):
        return self.frame

    def __del__(self):
        self.stop_camera()