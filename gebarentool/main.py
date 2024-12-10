import cv2
import flet as ft
import base64
import threading
import mediapipe as mp
import numpy as np
import time

from leerTool import show_page1
from account import show_page3
from login import show_login_page
from register import show_register_page

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils


def main(page: ft.Page):
    # Set the default theme mode to Light
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "white"

    # Placeholder image if the camera is not accessible
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(placeholder_image, "Camera not available", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
    placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')

    # Open the IP Webcam stream
    #ip_webcam_url = "http://10.2.88.169:8080/video"  # Replace with your IP Webcam URL
    #cap = cv2.VideoCapture(ip_webcam_url)
    #if not cap.isOpened():
        #print("Error: Could not access the IP Webcam stream.")
        #page.update()
        #return

    # Create the Image widget globally to make it accessible across functions
    img_widget = ft.Image(src_base64=placeholder_base64, width=640, height=480)
    status_text = ft.Text("", size=20)

    def show_main_page():
        page.clean()

        # Create navigation buttons
        button1 = ft.ElevatedButton("Learn", on_click=lambda e: show_page1(page, show_main_page, show_page3))
        button2 = ft.ElevatedButton("Translate", on_click=lambda e: show_main_page())
        button3 = ft.ElevatedButton("Account", on_click=lambda e: show_page3(page, show_main_page, show_page1))

        # Bottom row for navigation buttons
        nav_buttons = ft.Row(
            controls=[button1, button2, button3],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20  # Add spacing between the buttons
        )

        # Main layout with SPACE_BETWEEN to place nav buttons at the bottom
        layout = ft.Column(
            controls=[
                ft.Column(
                    controls=[img_widget, status_text],
                    alignment=ft.alignment.center,
                ),  # Centered content (camera feed and status)
                nav_buttons,  # Navigation buttons at the bottom
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Space between main content and nav
            expand=True  # Allow column to expand and push content apart
        )

        # Add the layout to the page
        page.add(layout)

        # Start frame updates in a separate thread
        threading.Thread(target=update_frame, daemon=True).start()

    def update_frame():
        last_frame_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue

            # Throttle frame processing to 10 FPS to reduce overhead
            current_time = time.time()
            if current_time - last_frame_time < 0.1:  # 10 FPS limit
                continue
            last_frame_time = current_time

            # Rotate the frame 180 degrees (flip upside down)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            
            # Flip the frame horizontally for a mirror-like effect
            frame = cv2.flip(frame, 1)

            # Convert to RGB only for gesture processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            # Initialize gesture detection variable
            gesture_detected = ""
            
            # Detect and draw landmarks only if hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Gesture recognition logic (Example: "Thumbs Up")
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    # Example for "Thumbs Up" gesture detection
                    if thumb_tip.y < index_tip.y:
                        gesture_detected = "Thumbs Up"
                    
                    # Add other gestures detection as needed
                    # For example, "Peace" sign, "Open hand", etc.
            
            # Encode the frame to base64
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")

            # Update the Image widget with the new frame
            img_widget.src_base64 = img_base64
            # Update the status text with the detected gesture
            status_text.value = f"Gesture detected: {gesture_detected}"
            page.update()

    # Start with login page instead of main page
    show_login_page(page, lambda: show_main_page(), lambda p, m, l: show_register_page(p, m, l))

ft.app(target=main)
