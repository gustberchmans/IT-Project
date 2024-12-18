import flet as ft
import cv2
import os
import threading
import numpy as np
import base64
import mediapipe as mp
from components.header import HeaderBar
from components.nav_bar import NavBar
import time
import tensorflow as tf
from tensorflow.python.keras.models import load_model

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

model_path = os.path.join(os.path.dirname(__file__), "../models/Hello_model.h5")

# Load the model
model = load_model(model_path)

# Global variables for camera and thread control
cap = None
update_thread_running = False
update_thread = None
using_ip_webcam = False  # Flag to indicate camera type

# IP Webcam URL
ip_webcam_url = "http://10.2.88.110:8080/video"

def show_translate_page(page: ft.Page, router):
    global cap, update_thread_running, update_thread, img_widget, status_text, message_text, ai_message, camera_section, using_ip_webcam

    # Placeholder image if the camera is not accessible
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
    #cv2.putText(placeholder_image, "Camera not available", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
    placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')

    # Create the Image widget globally to make it accessible across functions
    img_widget = ft.Image(
        src_base64=placeholder_base64, 
        width=400,
        height=400,  # Set initial height to 400
        fit=ft.ImageFit.COVER,
        border_radius=8,
    )

    # At the start of show_translate_page, create a Text control for the message
    message_text = ft.Text("", size=14, color=ft.colors.BLACK)
    
    # Create the AI message container with the dynamic text
    ai_message = ft.Container(
        content=message_text,
        bgcolor=ft.colors.BLUE_50,
        border_radius=10,
        padding=ft.padding.all(15),
        margin=ft.margin.only(left=20, right=80),
        visible=False,  # Hide initially until there's a message
    )

    # Grey camera preview area (initially set to 400x400)
    camera_section = ft.Container(
        content=img_widget,
        width=0,
        height=0,  # Set initial height to 400
        border_radius=8,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.center,
        margin=ft.margin.symmetric(vertical=20),
    )

    # Status text for gesture detection
    status_text = ft.Text("", size=20)

    # Bottom input bar with camera button
    input_section = ft.Container(
        content=ft.Row(
            controls=[ 
                ft.Container(
                    content=ft.TextField(
                        hint_text="Type",
                        border=ft.InputBorder.NONE,
                        cursor_color=ft.colors.BLACK,
                        text_style=ft.TextStyle(
                            color=ft.colors.BLACK,
                        ),
                    ),
                    bgcolor=ft.colors.GREY_200,
                    border_radius=25,
                    padding=ft.padding.only(left=20, right=20),
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.CAMERA_ALT_ROUNDED,
                        icon_color=ft.colors.BLACK54,
                        on_click=lambda e: toggle_camera(page),  # Toggle camera on button click
                    ),
                    bgcolor=ft.colors.GREY_200,
                    border_radius=25,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=20),
        margin=ft.margin.only(bottom=20),
    )

    # Create navigation bar
    nav_bar = NavBar(router=router, active_route="/translate")

    # Page configuration
    page.clean()
    page.bgcolor = ft.colors.WHITE
    page.padding = 0
    page.window_width = 400
    page.window_height = 800

    # Main layout
    content = ft.Column(
        controls=[ 
            HeaderBar(router),
            camera_section,
            ai_message,
            status_text,
            ft.Container(expand=True),
            input_section,
            nav_bar,
        ],
        expand=True,
        spacing=0,
    )

    # Function to initialize the camera
    def open_camera():
        global cap, ip_webcam_url, using_ip_webcam

        # Attempt to open IP webcam first
        if ip_webcam_url:
            print(f"Trying to access IP Webcam at {ip_webcam_url}...")
            cap = cv2.VideoCapture(ip_webcam_url)

            # Wait for the camera to open with a timeout
            while not cap.isOpened():
                    print("Timeout reached. Failed to access IP Webcam.")
                    break

            if cap.isOpened():
                print("IP Webcam accessed successfully.")
                using_ip_webcam = True
                return True
            else:
                print("Failed to access IP Webcam. Trying hardware webcam...")

        # Fallback to hardware webcam if IP webcam fails
        print("Attempting to access hardware webcam...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("Hardware webcam accessed successfully.")
            using_ip_webcam = False
            return True
        else:
            print("Error: Could not access any camera.")
            return False

    # Function to release the camera
    def close_camera():
        global cap
        if cap and cap.isOpened():
            cap.release()
            cap = None

    # Function to stop the update thread
    def stop_update_thread():
        global update_thread_running
        update_thread_running = False
        if update_thread is not None:
            update_thread.join()

    # Function to start the update thread
    def start_update_thread():
        global update_thread_running
        if not update_thread_running:
            update_thread_running = True
            threading.Thread(target=update_frame, daemon=True).start()

    def extract_landmarks(results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Extract and flatten all 21 landmarks (x, y, z)
                landmarks = [
                    [lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark
                ]
                flattened_landmarks = np.array(landmarks).flatten()
                return flattened_landmarks
        return None

    def preprocess_landmarks(landmarks):
        # Normalize landmarks (optional, if required by the model)
        landmarks = np.array(landmarks)
        landmarks = landmarks / np.linalg.norm(landmarks)  # Normalize vector length

        # Expand dimensions to match model input (1, 10, 63)
        # Since the model expects a sequence of 10 frames, replicate landmarks
        sequence = np.tile(landmarks, (10, 1))
        sequence = np.expand_dims(sequence, axis=0)
        return sequence

    def update_frame():
        global update_thread_running
        last_frame_time = 0
        frame_skipped = 0  # Frame skip counter for throttling inference

        # Debouncing buffer for consistent gesture detection
        debounce_buffer = []
        debounce_threshold = 3  # Minimum consecutive consistent frames to update message

        while update_thread_running:
            if not cap or not cap.isOpened():
                print("Camera feed not available")
                # time.sleep(1)
                continue

            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue

            # Throttle frame processing to 20 FPS for display
            current_time = time.time()
            if current_time - last_frame_time < 0.05:  # ~20 FPS
                continue
            last_frame_time = current_time

            # Flip the frame and convert to RGB
            if (not using_ip_webcam):
                frame = cv2.flip(frame, 1)
            else:
                frame = cv2.flip(frame, 1)
                frame = cv2.flip(frame, -1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe Hands
            results = hands.process(rgb_frame)
            landmarks = extract_landmarks(results)

            # Perform inference when landmarks are detected
            if landmarks is not None:
                frame_skipped = 0  # Reset skip counter
                preprocessed_landmarks = preprocess_landmarks(landmarks)

                # Run the model prediction
                predictions = model.predict(preprocessed_landmarks, verbose=0)
                predicted_class = np.argmax(predictions, axis=1)[0]

                # Map predicted class to a gesture name
                gesture_map = {0: "Nothing", 1: "Hallo"}
                gesture_detected = gesture_map.get(predicted_class, "Unknown Gesture")

                # Add the detected gesture to the debounce buffer
                debounce_buffer.append(gesture_detected)
                if len(debounce_buffer) > debounce_threshold:
                    debounce_buffer.pop(0)

                # Check if the gesture has been consistent
                if len(set(debounce_buffer)) == 1:  # All entries in the buffer are the same
                    message_text.value = f"This sign means '{gesture_detected}'."
                    ai_message.visible = True
            else:
                frame_skipped += 1
                if frame_skipped > 5:  # Only add "No hand detected" if no hand is seen for 5 consecutive frames
                    debounce_buffer.append("No hand detected")
                    if len(debounce_buffer) > debounce_threshold:
                        debounce_buffer.pop(0)

                    if len(set(debounce_buffer)) == 1:  # Consistent "No hand detected"
                        message_text.value = "No hand detected."
                        ai_message.visible = True

            # Encode and update frame for UI
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            img_widget.src_base64 = img_base64
            page.update()

    # Toggle camera: Open/Close camera when button is pressed
    def toggle_camera(page):
        global cap, update_thread_running
        if not cap or not cap.isOpened():
            if open_camera():
                print("Camera initialized successfully.")
            else:
                print("Error: Camera not accessible.")
            start_update_thread()
            # Make the camera preview bigger when recording
            camera_section.width = 400  # Keep the width same
            camera_section.height = 550  # Set height to 550 when recording
            img_widget.width = 400  # Keep the width same
            img_widget.height = 550  # Set height to 550 when recording
            page.update()
        else:
            close_camera()
            stop_update_thread()
            # Set the black screen with "No video available" message
            placeholder_image = np.ones((400, 400, 3), dtype=np.uint8) *255  # 400x400 placeholder
            cv2.putText(placeholder_image, "Camera not available", (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
            placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')
            img_widget.src_base64 = placeholder_base64
            # Revert to the original size of 400x400 when camera is closed
            camera_section.width = 0
            camera_section.height = 0
            img_widget.width = 0
            img_widget.height = 0
            page.update()

    # Return the View object
    return ft.View(
        route="/translate",
        controls=[content],
        bgcolor=ft.colors.WHITE,
        vertical_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

# Ensure the camera is closed when navigating away from the page
def on_page_unload():
    stop_update_thread()
    close_camera()

# Call `on_page_unload()` during page navigation or exit
def unload_page(page):
    page.on_unload = on_page_unload
