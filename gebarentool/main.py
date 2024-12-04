import cv2
import flet as ft
import base64
import threading
import mediapipe as mp
import numpy as np

from leerTool import show_page1
from account import show_page3

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

    # Open the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        page.update()
        return

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
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            gesture_detected = ""
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            frame = cv2.flip(frame, 1)
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # Update the Image widget
            img_widget.src_base64 = img_base64
            status_text.value = f"Gesture detected: {gesture_detected}"
            page.update()

    show_main_page()

ft.app(target=main)