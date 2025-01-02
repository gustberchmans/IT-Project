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
from collections import deque

if tf.config.list_physical_devices('GPU'):
    print("GPU is available.")
else:
    print("GPU is not available.")

# Set the GPU device for the model
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    tf.config.set_visible_devices(physical_devices[0], 'GPU')
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

frame_processing_time_limit = 1 / 20

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.75, 
    min_tracking_confidence=0.75,
    max_num_hands=2,
)
mp_drawing = mp.solutions.drawing_utils

model1 = load_model(os.path.join(os.path.dirname(__file__), "../models/Hello_Fast_model.h5"))
model2 = load_model(os.path.join(os.path.dirname(__file__), "../models/Eerst_model.h5"))
model3 = load_model(os.path.join(os.path.dirname(__file__), "../models/Goed_Fast_model.h5"))

actions = {
    'Hello': ['Hello', 'no_gesture'],
    'Eerst': ['Eerst', 'no_gesture'],
    'Goed': ['Goed', 'no_gesture']
}

models_info = {
    'Hello': {'model': model1, 'features': 63},
    'Eerst': {'model': model2, 'features': 63},
    'Goed': {'model': model3, 'features': 63}
}

sequence = deque(maxlen=30)

# Global variables for camera and thread control
cap = None
update_thread_running = False
update_thread = None

video_playing = False
cameraClosed = True

# IP Webcam URL
ip_webcam_url = "http://192.168.0.130:8080/video"

# Path to your video files folder
video_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video")
video_folder_path = os.path.normpath(video_folder_path)
video_files = [f for f in os.listdir(video_folder_path) if f.endswith(".mp4")]
    
# Define global variable for user input
user_input_global = ""

# Lock to protect shared resources between threads
camera_lock = threading.Lock()

# Debouncing buffer for consistent gesture detection
debounce_buffer = []
debounce_threshold = 3  # Minimum consecutive consistent frames to update message

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
        height=500,  # Set initial height to 400
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
            cap = cv2.VideoCapture(ip_webcam_url)

            # Wait for the camera to open with a timeout
            while not cap.isOpened():
                print("Timeout reached. Failed to access IP Webcam.")
                cap.release()
                cap = None
                break

            if cap and cap.isOpened():
                using_ip_webcam = True
                return True
            else:
                print("Failed to access IP Webcam. Trying hardware webcam...")

        # Fallback to hardware webcam if IP webcam fails
        print("Attempting to access hardware webcam...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
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

    def preprocess_landmarks(landmarks):
        if landmarks is None:
            return None
        
        landmarks = np.array(landmarks)
        
        # Check if the landmarks have the correct size (63 per hand)
        if len(landmarks) != 63:  # For one hand, we expect 63 values (21 landmarks * 3 values per landmark)
            return None
        
        # Normalize landmarks (optional, if required by the model)
        landmarks = landmarks / np.linalg.norm(landmarks)  # Normalize vector length
        
        # Expand dimensions to match model input (1, 10, 63)
        sequence = np.tile(landmarks, (10, 1))  # Replicate landmarks 10 times to create a sequence
        sequence = np.expand_dims(sequence, axis=0)  # Shape should be (1, 10, 63)
        
        return sequence

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
        if not results.multi_hand_landmarks:
            return None
        landmarks = []
        # Verwerk alleen de eerste hand
        hand_landmarks = results.multi_hand_landmarks[0]
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return landmarks

    def update_frame():
        global cap, update_thread_running, video_playing, using_ip_webcam, img_widget  # Ensure global variables are used

        last_frame_time = 0
        frame_count = 0  # Initialize a counter for the frames

        while update_thread_running:
            if not cap or not cap.isOpened():
                print("Camera feed not available")
                continue

            try:
                ret, frame = cap.read()
            except Exception as e:
                print(f"Error reading frame: {e}")
                continue

            if not ret:
                print("Error capturing image")
                continue

            # Skip every third frame
            frame_count += 1
            if frame_count % 3 == 0:
                continue

            # Throttle frame processing to 20 FPS for display (50ms delay between frames)
            current_time = time.time()
            frame_processing_time = current_time - last_frame_time

            # Calculate the sleep time
            sleep_time = frame_processing_time_limit - frame_processing_time
            
            # Only sleep if the sleep time is positive
            if sleep_time > 0:
                time.sleep(sleep_time)  # Sleep to balance FPS

            last_frame_time = current_time

            if not using_ip_webcam:
                frame = cv2.flip(frame, 1)
            else:
                frame = cv2.flip(frame, 1)
                frame = cv2.flip(frame, -1)

            frame = make_square(frame)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            landmarks = extract_landmarks(results)

            # Perform inference when landmarks are detected
            if landmarks is not None and len(landmarks) == 63:
                sequence.append(landmarks)
                perform_inference(frame, page)  # Pass frame as an argument
            else:
                pass

            # Encode and update the frame for the UI
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            img_widget.src_base64 = img_base64
            
            # Avoid any additional frame processing if frame time exceeds the limit
            page.update()

    def play_video(video_path, page):
        global video_playing
        # Check if the video exists or not
        cap_video = cv2.VideoCapture(video_path)

        if not cap_video.isOpened():
            # If no video is found, display a black screen
            print("No video available, displaying a black screen.")
            black_screen = np.zeros((500, 400, 3), dtype=np.uint8)
            _, black_buffer = cv2.imencode('.jpg', black_screen)
            black_base64 = base64.b64encode(black_buffer).decode('utf-8')
            img_widget.src_base64 = black_base64

            # Set container size to 400x500 for consistency
            camera_section.width = 400
            camera_section.height = 500
            page.update()
            return

        # Set the container size to 400x500 at the start of video playback
        camera_section.width = 400
        camera_section.height = 500
        img_widget.width = 400
        img_widget.height = 500
        page.update()

        while cap_video.isOpened():
            ret, frame = cap_video.read()
            if not ret:
                break

            # Resize video frame to fit within 400x500
            frame = cv2.resize(frame, (400, 500))

            # Encode the frame into base64
            _, buffer = cv2.imencode(".jpg", frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # Update the img_widget with the new frame
            img_widget.src_base64 = frame_base64
            page.update()

        cap_video.release()
        video_playing = False  # Reset the flag once the video ends

        # Reset the container size to indicate no video feed
        camera_section.width = 0
        camera_section.height = 0
        img_widget.width = 0
        img_widget.height = 0
        page.update()

    # Toggle camera: Open/Close camera when button is pressed
    def toggle_camera(page):
        global cap, update_thread_running, video_playing, cameraClosed
        if not cap or not cap.isOpened():
            if open_camera():
                pass
            else:
                print("Error: Camera not accessible.")
            start_update_thread()
            # Make the camera preview bigger when recording
            camera_section.width = 400  # Keep the width same
            camera_section.height = 500  # Set height to 550 when recording
            img_widget.width = 400  # Keep the width same
            img_widget.height = 500  # Set height to 550 when recording
            page.update()
            
            cameraClosed = False
        else:
            close_camera()
            stop_update_thread()
            # Set the black screen with "No video available" message
            placeholder_image = np.ones((400, 500, 3), dtype=np.uint8) * 255  # 400x400 placeholder
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
        user_message_text.value = user_input  # Update the text content
        user_message.controls[0].visible = True  # Make the user message visible
        page.update()
        user_input_global = user_input  # Store the input in the global variable

        if not video_playing:
            video_playing = True  # Set flag to prevent replay
            video_found = False  # Track whether a matching video is found
            user_input_words = user_input_global.lower().split()  # Split input into words

            for word in user_input_words:
                for video_file in video_files:
                    video_file_name_without_extension = os.path.splitext(video_file)[0]

                    # Compare each word from the user input with the video file name (case insensitive)
                    if word == video_file_name_without_extension.lower():
                        video_path = os.path.join(video_folder_path, video_file)
                        play_video(video_path, page)
                        video_found = True
                        message_text.value = "Playing video..."
                        ai_message.visible = True
                        break  # Exit the inner loop if a match is found

            if not video_found:
                message_text.value = "No matching video found."
                ai_message.visible = True
                page.update()
            
            video_playing = False  # Reset the flag after attempting to play

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

def make_square(frame):
    height, width, _ = frame.shape
    if height > width:
        delta = height - width
        top = delta // 2
        bottom = delta - top
        frame = frame[top:height-bottom, 0:width]
    elif width > height:
        delta = width - height
        left = delta // 2
        right = delta - left
        frame = frame[0:height, left:width-right]
    return frame

def perform_inference(frame, page):
    global sequence, models_info, actions, debounce_buffer, debounce_threshold, message_text, ai_message

    if len(sequence) == 30:
        sequence_array = np.array(sequence)

        # Check the shape of the sequence array
        if sequence_array.shape != (30, 63):
            print(f"Warning: sequence shape is {sequence_array.shape}. Expected (30, 63).")
            return

        predictions = {}
        for model_name, info in models_info.items():
            model = info['model']
            expected_features = info['features']

            if expected_features == 63:
                single_hand_landmarks = sequence_array.reshape(1, 30, 63)
                with tf.device('/GPU:0'):  # Ensure GPU is used for inference
                    pred = model.predict(single_hand_landmarks, verbose=0)[0]
            elif expected_features == 126:
                input_data_full = sequence_array.reshape(1, 30, 126)
                with tf.device('/GPU:0'):  # Ensure GPU is used for inference
                    pred = model.predict(input_data_full, verbose=0)[0]
            else:
                print(f"Model {model_name} has an unexpected feature size.")
                continue

            pred_idx = np.argmax(pred)
            confidence = pred[pred_idx]
            label = actions[model_name][pred_idx]
            predictions[model_name] = (label, confidence)

        # Filter predictions to exclude 'no_gesture'
        filtered_predictions = {k: v for k, v in predictions.items() if v[0] != 'no_gesture'}
        if filtered_predictions:
            # Find the prediction with the highest confidence
            best_prediction = max(filtered_predictions.items(), key=lambda x: x[1][1])
            best_label, best_confidence = best_prediction[1]

            # Debounce for consistent gesture detection
            debounce_buffer.append(best_label)
            if len(debounce_buffer) >= debounce_threshold and debounce_buffer.count(best_label) == debounce_threshold:
                # Update message and AI container if gesture is consistent
                message_text.value = f"Detected gesture: {best_label} ({best_confidence:.2f})"
                ai_message.visible = True
                debounce_buffer.clear()  # Reset debounce buffer after updating
        else:
            message_text.value = "No valid gesture detected."
            ai_message.visible = True

        # Update UI
        if page:
            page.update()
