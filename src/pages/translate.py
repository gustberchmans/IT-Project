import flet as ft
import cv2
import os
import threading
import numpy as np
import base64
import mediapipe as mp
import time
import tensorflow as tf
from tensorflow.python.keras.models import load_model
from components.nav_bar import NavBar
from components.header import HeaderBar

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

video_playing = False
cameraClosed = True

# IP Webcam URL
ip_webcam_url = "http://10.2.88.111:8080/video"

# Path to your video files folder
video_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video")
video_folder_path = os.path.normpath(video_folder_path)
video_files = [f for f in os.listdir(video_folder_path) if f.endswith(".mp4")]

print("Video files in the folder:")
for video_file in video_files:
    print(video_file)
    
# Define global variable for user input
user_input_global = ""

def show_translate_page(page: ft.Page, router):
    global cap, update_thread_running, update_thread, img_widget, status_text, message_text, ai_message, user_message_text, camera_section, using_ip_webcam

    # Placeholder image if the camera is not accessible
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
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

    # User message text widget
    user_message_text = ft.Text("", size=14, color=ft.colors.BLACK)

    # User message container aligned to the right
    user_message = ft.Row(
        controls=[ 
            ft.Container(
                content=user_message_text,
                bgcolor=ft.colors.GREEN_50,
                border_radius=10,
                padding=ft.padding.all(15),
                margin=ft.margin.only(top=10),
                visible=False,  # Hide initially until there's input
            )
        ],
        alignment=ft.MainAxisAlignment.END,  # Align container to the right
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
                        on_submit=lambda e: send_user_message(e.control.value),
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
            user_message,
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
        global update_thread_running, video_playing
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
        global update_thread_running, video_playing  # Ensure global variables are used
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

            try:
              ret, frame = cap.read()
            except:
              pass
            
            if not ret:
                print("Failed to capture image")
                continue

            # Throttle frame processing to 20 FPS for display (50ms delay between frames)
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
            else:
                # Handle case when no landmarks (hand) are detected
                frame_skipped += 1
                if frame_skipped > 5:  # Only add "No hand detected" if no hand is seen for 5 consecutive frames
                    debounce_buffer.append("No hand detected")
                    if len(debounce_buffer) > debounce_threshold:
                        debounce_buffer.pop(0)

                    if len(set(debounce_buffer)) == 1:  # Consistent "No hand detected"
                        message_text.value = "No hand detected."
                        ai_message.visible = True

            # Encode and update frame for UI (in case you need to display it)
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            img_widget.src_base64 = img_base64
            page.update()

    def play_video(video_path):
        print(f"Playing video: {video_path}")
        
        # Set the video window size to 400x500
        cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video", 400, 500)

        # Check if the video exists or not
        cap_video = cv2.VideoCapture(video_path)

        if not cap_video.isOpened():
            # If no video is found, display a black screen
            print("No video available, displaying a black screen.")
            black_screen = np.zeros((500, 400, 3), dtype=np.uint8)
            while True:
                cv2.imshow('Video', black_screen)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
            return

        while cap_video.isOpened():
            ret, frame = cap_video.read()
            if not ret:
                break

            # Resize video frame to fit within 400x500 if necessary
            frame = cv2.resize(frame, (400, 500))

            # Display the frame
            cv2.imshow('Video', frame)

            # Press 'q' to exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap_video.release()
        cv2.destroyAllWindows()

    # Toggle camera: Open/Close camera when button is pressed
    def toggle_camera(page):
        global cap, update_thread_running, video_playing, cameraClosed
        if not cap or not cap.isOpened():
            if open_camera():
                print("Camera initialized successfully.")
            else:
                print("Error: Camera not accessible.")
            start_update_thread()
            # Make the camera preview bigger when recording
            camera_section.width = 400  # Keep the width same
            camera_section.height = 500  # Set height to 500 when recording
            img_widget.width = 400  # Keep the width same
            img_widget.height = 500  # Set height to 500 when recording
            page.update()
            
            cameraClosed = False
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
            
            cameraClosed = True

    # Handle user input and display user message
    def send_user_message(user_input):
        global user_input_global, video_playing  # Declare that we are using the global variable
        print(user_input)
        user_message_text.value = user_input  # Update the text content
        user_message.controls[0].visible = True  # Make the user message visible
        page.update()
        user_input_global = user_input  # Store the input in the global variable
        
        if not video_playing:
            video_playing = True  # Set flag to prevent replay
            print(f"Attempting to play video for gesture: {user_input_global}")
            
            # Iterate over the video files
            for video_file in video_files:
                # Remove the '.mp4' extension for the comparison
                video_file_name_without_extension = os.path.splitext(video_file)[0]
                
                # Compare the user input (gesture) with the video file name without extension
                if user_input_global.lower() == video_file_name_without_extension.lower():
                    # Construct the full video path by adding back the '.mp4' extension
                    video_path = os.path.join(video_folder_path, video_file)
                    print(f"Video path: {video_path}")
                    play_video(video_path)
                    video_playing = False
                    break
                else:
                    video_playing = False
        return user_input


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
