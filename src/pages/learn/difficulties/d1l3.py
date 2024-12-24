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
from services.firebase import add_score, get_current_user, update_progress

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

model1 = load_model(os.path.join(os.path.dirname(__file__), "../../../models/Hello_Fast_model.h5"))
model2 = load_model(os.path.join(os.path.dirname(__file__), "../../../models/Eerst_model.h5"))
model3 = load_model(os.path.join(os.path.dirname(__file__), "../../../models/Goed_Fast_model.h5"))

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

cameraClosed = True

# IP Webcam URL
ip_webcam_url = "http://10.2.88.62:8080/video"

# Debouncing buffer for consistent gesture detection
debounce_buffer = []
debounce_threshold = 3  # Minimum consecutive consistent frames to update message
gesture_start_time = None
gesture_hold_duration = 3
current_gesture_index = 0
gestures = ['Hello', 'Goed', 'Eerst']
gesture_completed = False
score = 0


# Lock to protect shared resources between threads
camera_lock = threading.Lock()

# Define global variables for UI elements
img_widget = None
status_text = None
message_text = None
ai_message = None
camera_section = None
gesture_text = None
camera_button = None




    



def show_d1l3_page(page: ft.Page, router): 
    state = {
        "exercise_index": 0,
        "score": 0,
        "cap": None,
        "thread_running": False,
        "recognized_since": None,
        "seq": deque(maxlen=30),
        "router": router  # Store router in state
    }
    
    global cap, update_thread_running, update_thread, img_widget, status_text, message_text, ai_message, camera_section, using_ip_webcam, current_gesture_index, gesture_start_time, gesture_completed, gesture_text, camera_button, score
    
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
    
    # Text control to display which gesture should be performed
    gesture_text = ft.Text(f"Perform gesture: {gestures[current_gesture_index]}", size=20, color=ft.colors.BLACK)


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
    
    # Bottom button to start the camera
    camera_button = ft.Container(
        content=ft.ElevatedButton(
            "Start Camera",
            on_click=lambda e: toggle_camera(page),  # Toggle camera on button click
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
            ),
            width=400,
            height=50
        ),
        padding=ft.padding.symmetric(horizontal=20),
        margin=ft.margin.only(bottom=20),
    )
    
    # Create navigation bar
    nav_bar = NavBar(router=router, active_route="/level_3")

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
            gesture_text,
            ai_message,
            status_text,
            ft.Container(expand=True),
            camera_button,
            nav_bar,
        ],
        expand=True,
        spacing=0,
    )
    
    # Function to initialize the camera
    def open_camera():
        global cap, ip_webcam_url, using_ip_webcam

        # Attempt to open IP webcam first
        if not ip_webcam_url:
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
        if not results.multi_hand_landmarks:
            return None
        landmarks = []
        # Verwerk alleen de eerste hand
        hand_landmarks = results.multi_hand_landmarks[0]
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        return landmarks

    def update_frame():
         global cap, update_thread_running, using_ip_webcam, img_widget  # Ensure global variables are used
         global current_gesture_index, gestures, gesture_start_time, gesture_completed
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
                 perform_inference(frame, page, state["router"])  # Pass frame and router as arguments
             else:
                 pass

             # Encode and update the frame for the UI
             _, buffer = cv2.imencode(".jpg", frame)
             img_base64 = base64.b64encode(buffer).decode("utf-8")
             img_widget.src_base64 = img_base64

             # Avoid any additional frame processing if frame time exceeds the limit
             page.update()


    # Toggle camera: Open/Close camera when button is pressed
    def toggle_camera(page):
        global cap, update_thread_running, cameraClosed
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
            
            
    def next_gesture(page):
        global current_gesture_index, gesture_start_time, gesture_completed, debounce_buffer, score
        global gesture_text, message_text, ai_message, camera_button

        # Reset state
        gesture_start_time = None
        gesture_completed = False
        debounce_buffer.clear()

        # Move to next gesture
        current_gesture_index += 1
        
        # Check if there are more gestures
        if current_gesture_index < len(gestures):
            # Update UI for next gesture
            gesture_text.value = f"Perform gesture: {gestures[current_gesture_index]}"
            message_text.value = ""
            ai_message.visible = False
        else:
            # All gestures completed
            show_results(router)
            gesture_text.value = "All exercises completed!"
            message_text.value = "Well done!"
            camera_button.content.text = "Finish"
            stop_update_thread()
            close_camera()
        
        page.update()
    
    def show_results(router):
        user_id = get_current_user()
        update_progress(user_id, "difficulty1", "d1l3", 1)
        add_score(user_id, score , "gesture_game", 3)
        router.navigate(f"/results/3/3")
        
    def perform_inference(frame, page, router):
        global gesture_start_time, gesture_completed, current_gesture_index, message_text, ai_message, gestures, score
        
        # Initialize defaults
        best_label = None
        best_confidence = 0.0
        
        try:
            if len(sequence) == 30:
                sequence_array = np.array(sequence)
                
                if sequence_array.shape != (30, 63):
                    print(f"Warning: Invalid sequence shape {sequence_array.shape}")
                    return
                
                # Check if the current gesture is valid
                if current_gesture_index >= len(gestures):
                    return # All gestures are done, so no need to perform inference anymore
                    
                predictions = {}
                for model_name, info in models_info.items():
                    model = info['model']
                    expected_features = info['features']
                    
                    # Get prediction
                    if expected_features == 63:
                        input_data = sequence_array.reshape(1, 30, 63) 
                        with tf.device('/GPU:0'):
                            pred = model.predict(input_data, verbose=0)[0]
                            pred_idx = np.argmax(pred)
                            confidence = pred[pred_idx]
                            label = actions[model_name][pred_idx]
                            predictions[model_name] = (label, confidence)
                            
                # Filter and get best prediction
                filtered_predictions = {k: v for k, v in predictions.items() 
                                    if v[0] != 'no_gesture'}
                                    
                if filtered_predictions:
                    best_prediction = max(filtered_predictions.items(), 
                                        key=lambda x: x[1][1])
                    best_label, best_confidence = best_prediction[1]
                    
                    current_gesture = gestures[current_gesture_index]
                    
                    # Handle gesture detection
                    if best_label == current_gesture:
                        debounce_buffer.append(best_label)
                        if (len(debounce_buffer) >= debounce_threshold and 
                            debounce_buffer.count(best_label) == debounce_threshold):
                            
                            if not gesture_start_time:
                                gesture_start_time = time.time()
                                
                            elapsed_time = time.time() - gesture_start_time
                            if elapsed_time >= gesture_hold_duration and not gesture_completed:
                                score += 1
                                if current_gesture_index >= len(gestures) - 1:
                                    # All gestures completed
                                    show_results(page, score, router)  # Pass router directly
                                    close_camera()
                                else:
                                    next_gesture(page)
                            elif not gesture_completed:
                                message_text.value = (f"Gesture {best_label} held for "
                                                f"{gesture_hold_duration} seconds. "
                                                "Proceeding to next exercise.")
                                ai_message.visible = True
                                debounce_buffer.clear()
                                gesture_completed = True
                                score += 1  # Increment the score
                                next_gesture(page)
                            elif not gesture_completed:
                                message_text.value = (f"Detected: {best_label} "
                                                f"({best_confidence:.2f}). "
                                                f"Hold for {gesture_hold_duration - int(elapsed_time)}s")
                                ai_message.visible = True
                                if confidence > 0.5:
                                    debounce_buffer.clear()
                                    gesture_completed = True
                                    score +=1 # Increment the score
                                    next_gesture(page)
                                    page.update()
                        else:
                            message_text.value = (f"Detected: {best_label} "
                                            f"({best_confidence:.2f}). "
                                            f"Hold for {gesture_hold_duration}s")
                            ai_message.visible = True
                            page.update()
                    else:
                        message_text.value = f"Please perform: {current_gesture}"
                        ai_message.visible = True
                        debounce_buffer.clear()
                        gesture_start_time = None
                        page.update()
                else:
                    message_text.value = "No valid gesture detected"
                    ai_message.visible = True
                    page.update()
                    
        except Exception as e:
            print(f"Error in perform_inference: {str(e)}")
            message_text.value = "Error processing gesture"
            ai_message.visible = True
            page.update()
    
    # Return the View object
    return ft.View(
        route="/level_3",  # Changed the route to /level_3
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

