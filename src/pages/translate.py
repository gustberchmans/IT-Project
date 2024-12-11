import flet as ft
import cv2
import threading
import numpy as np
import base64
import mediapipe as mp
from components.header import HeaderBar
from components.nav_bar import NavBar
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Global variables for camera and thread control
cap = None
update_thread_running = False
update_thread = None

# IP Webcam URL
ip_webcam_url = "http://10.2.88.156:8080/video"

def show_translate_page(page: ft.Page, router):
    global cap, update_thread_running, update_thread, img_widget, status_text, message_text, ai_message, camera_section

    # Placeholder image if the camera is not accessible
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(placeholder_image, "Camera not available", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
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
        width=400,
        height=400,  # Set initial height to 400
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
        global cap, ip_webcam_url

        # Attempt to open IP webcam first
        if ip_webcam_url:
            cap = cv2.VideoCapture(ip_webcam_url)
        
        # Fallback to hardware webcam if IP webcam fails
        if not cap or not cap.isOpened():
            print("Failed to access IP Webcam. Trying hardware webcam...")
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not access any camera.")
            return False
        return True

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

    def update_frame():
        global update_thread_running
        last_frame_time = 0
        while update_thread_running:
            if not cap or not cap.isOpened():
                print("Camera feed not available")
                time.sleep(1)
                continue

            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue

            # Throttle frame processing to 20 FPS
            current_time = time.time()
            if current_time - last_frame_time < 0.05:  # 20 FPS limit
                continue
            last_frame_time = current_time

            # Flip the frame horizontally and vertically
            frame = cv2.flip(frame, 1)  # Flip horizontally
            frame = cv2.flip(frame, -1)  # Flip vertically

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
                        # Update the message when gesture is detected
                        message_text.value = f"This sign means '{gesture_detected}' in sign language."
                        ai_message.visible = True
                    else:
                        ai_message.visible = False
                        status_text.value = ""

            # Encode the frame to base64
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")

            # Update the Image widget with the new frame
            img_widget.src_base64 = img_base64
            page.update()

    # Toggle camera: Open/Close camera when button is pressed
    def toggle_camera(page):
        global cap, update_thread_running
        if not cap or not cap.isOpened():
            if not open_camera():
                print("Failed to open camera")
                return
            start_update_thread()
            print("Camera opened")
            # Make the camera preview bigger when recording
            camera_section.width = 400  # Keep the width same
            camera_section.height = 600  # Set height to 600 when recording
            img_widget.width = 400  # Keep the width same
            img_widget.height = 600  # Set height to 600 when recording
            page.update()
        else:
            close_camera()
            stop_update_thread()
            # Set the black screen with "No video available" message
            placeholder_image = np.zeros((400, 400, 3), dtype=np.uint8)  # 400x400 placeholder
            #cv2.putText(placeholder_image, "Camera not available", (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
            placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')
            img_widget.src_base64 = placeholder_base64
            # Revert to the original size of 400x400 when camera is closed
            camera_section.width = 400
            camera_section.height = 400  # Reset to 400x400
            img_widget.width = 400
            img_widget.height = 400  # Reset to 400x400
            print("Camera closed")
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
