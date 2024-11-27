import cv2
import flet as ft
import base64
import threading
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def main(page: ft.Page):
    # Create a Text widget for the loading screen
    loading_text = ft.Text("Loading camera... Please wait.", size=20)

    # Add the loading screen widget to the page
    page.add(loading_text)

    # Create an Image widget to display the camera feed (initialized with no source)
    img_widget = ft.Image(width=640, height=480)
    
    # Add the image widget to the page (but keep it hidden initially)
    page.add(img_widget)

    # Open the camera
    cap = cv2.VideoCapture(0)  # Camera index (0 for default)
    
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        loading_text.value = "Error: Could not access the camera."
        page.update()
        return

    # Function to capture frames from the camera, process hand recognition, and update the Image widget
    def update_frame():
        while True:
            # Capture a frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture image")
                continue
            
            # Convert the frame to RGB (MediaPipe requires RGB images)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame with MediaPipe Hands
            results = hands.process(rgb_frame)
            
            # Draw the hand landmarks if any hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Flip the frame horizontally to mirror the image
            frame = cv2.flip(frame, 1)  # 1 means horizontal flip (mirror effect)

            # Convert the frame to base64 to display in Flet
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # Update the Image widget with the new base64-encoded frame
            img_widget.src_base64 = img_base64

            # Replace the loading screen with the camera feed after it's ready
            if loading_text.value != "":
                loading_text.value = ""
                page.update()

            page.update()

    # Run the update_frame function in a separate thread to avoid blocking the main thread
    threading.Thread(target=update_frame, daemon=True).start()

    # Run the app
    page.update()

# Run the Flet app
ft.app(target=main)
