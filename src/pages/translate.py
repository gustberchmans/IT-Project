import flet as ft
import cv2
import threading
import numpy as np
import base64
import mediapipe as mp
from components.nav_bar import NavBar
import time
import requests
from io import BytesIO
from PIL import Image

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Global variables for camera and thread control
cap = None
update_thread_running = False
update_thread = None

# IP Webcam URL
ip_webcam_url = "http://10.2.88.156:8080/video"  # Default IP Webcam URL, replace as needed

def show_translate_page(page: ft.Page, router):
    global cap, update_thread_running, update_thread

    # Placeholder image if the camera is not accessible
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(placeholder_image, "Camera not available", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
    placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')

    # Create the Image widget globally to make it accessible across functions
    img_widget = ft.Image(src_base64=placeholder_base64, width=640, height=480)
    status_text = ft.Text("", size=20)

    # Function to initialize the camera
    def open_camera():
        global cap
        global ip_webcam_url

        # Attempt to open IP webcam first
        if ip_webcam_url:
            cap = cv2.VideoCapture(ip_webcam_url)
            print("Attempting to open IP Webcam...")

        # Fallback to hardware webcam if IP webcam fails
        if not cap or not cap.isOpened():
            print("Failed to access IP Webcam. Trying hardware webcam...")
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not access any camera.")
            return False
        print("Camera successfully opened.")
        return True

    # Function to release the camera
    def close_camera():
        global cap
        if cap and cap.isOpened():
            cap.release()
            cap = None
            print("Camera released.")

    # Function to stop the update thread
    def stop_update_thread():
        global update_thread_running
        update_thread_running = False
        if update_thread is not None:
            update_thread.join()
        print("Update thread stopped.")

    # Function to start the update thread
    def start_update_thread():
        global update_thread_running, update_thread
        update_thread_running = False
        if not update_thread_running:
            update_thread_running = True
            update_thread = threading.Thread(target=update_frame, daemon=True)
            update_thread.start()
            print("Update thread started.")

    def fetch_ip_webcam_frame(url):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                bytes_io = BytesIO(response.content)
                img = Image.open(bytes_io)
                frame = np.array(img)
                return frame
            else:
                print(f"Failed to fetch frame: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching frame: {e}")
            return None

    def update_frame():
        global update_thread_running
        last_frame_time = 0
        while update_thread_running:
            if not cap or not cap.isOpened():
                print("Camera feed not available")
                time.sleep(1)
                continue

            # Try to read the frame using OpenCV
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image using OpenCV. Trying alternative method...")
                frame = fetch_ip_webcam_frame(ip_webcam_url)
                if frame is None:
                    print("Failed to capture image using alternative method")
                    time.sleep(1)
                    continue

            # Throttle frame processing to 10 FPS
            current_time = time.time()
            if current_time - last_frame_time < 0.05:  # 10 FPS limit
                continue
            last_frame_time = current_time

            # Flip the frame horizontally and vertically
            frame = cv2.flip(frame, 1)
            frame = cv2.flip(frame, -1)

            # Convert to RGB for gesture processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Initialize gesture detection variable
            gesture_detected = ""
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    if thumb_tip.y < index_tip.y:
                        gesture_detected = "Thumbs Up"

            # Encode the frame to base64
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")

            # Update the Image widget with the new frame
            img_widget.src_base64 = img_base64
            status_text.value = f"Gesture detected: {gesture_detected}"
            page.update()

    # Clean the page and open the camera
    page.clean()
    page.window_width = 400
    page.window_height = 800
    page.bgcolor = "#f0f4f8"

    if not open_camera():
        return

    # Create navigation buttons
    nav_bar = NavBar(router=router, active_route="/translate")

    # Main layout with SPACE_BETWEEN to place nav buttons at the bottom
    content = ft.Column(
        controls=[
            ft.Column(
                controls=[img_widget, status_text],
                alignment=ft.alignment.center,
            ),
            nav_bar,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        expand=True
    )

    # Start the frame update thread
    start_update_thread()

    # Return the View object
    return ft.View(
        route="/translate",
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

# Ensure the camera is closed when navigating away from the page
def on_page_unload():
    print("Page unload triggered")
    stop_update_thread()
    close_camera()