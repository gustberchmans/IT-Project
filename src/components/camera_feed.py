import flet as ft
import cv2
import base64
import threading

class CameraFeed(ft.UserControl):
    def __init__(self, width=640, height=480):
        super().__init__()
        self.width = width
        self.height = height
        self.cap = None
        self.running = False
        self.image = ft.Image(width=width, height=height, fit=ft.ImageFit.CONTAIN)

    def did_mount(self):
        self.start_camera()

    def will_unmount(self):
        self.stop_camera()

    def build(self):
        return self.image

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            return False
        self.running = True
        threading.Thread(target=self._update_frame, daemon=True).start()
        return True

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def _update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode()
            self.image.src_base64 = img_base64
            self.update()