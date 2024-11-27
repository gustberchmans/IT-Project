import cv2
import flet as ft
import base64
import threading
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def main(page: ft.Page):
    # Create a Text widget for the loading screen
    loading_text = ft.Text("Loading camera... Please wait.", size=20)

    # Create a temporary placeholder image (can be a blank or a colored image)
    placeholder_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(placeholder_image, "Camera not available", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    _, placeholder_buffer = cv2.imencode('.jpg', placeholder_image)
    placeholder_base64 = base64.b64encode(placeholder_buffer).decode('utf-8')
    
    # Create an Image widget to display the camera feed (initialized with placeholder image)
    img_widget = ft.Image(src_base64=placeholder_base64, width=640, height=480)
    
    # Create a Text widget to show the thumbs-up detection status
    status_text = ft.Text("", size=20)

    # Use Column layout to arrange the image and status text
    layout = ft.Column(
        controls=[
            loading_text,  # Loading text placed first, on top
            img_widget,    # Camera feed placed second, below the loading text
            status_text    # Status text for thumbs-up detection placed below the image
        ],
        alignment=ft.alignment.center,  # Center both widgets in the column
        spacing=10  # Add some space between the image and the text
    )

    # Add the layout to the page
    page.add(layout)

    # Open the camera
    cap = cv2.VideoCapture(0)  # Camera index (0 for default)
    
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        loading_text.value = "Error: Could not access the camera."
        page.update()
        return

    # Function to check for thumbs-up gesture
    def is_thumbs_up(hand_landmarks):
        # Get the landmarks for the thumb
        thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
        thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
        thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
        
        # Check if the thumb is extended (thumb tip is higher than the base of the thumb)
        if thumb_tip.y < thumb_ip.y < thumb_mcp.y:
            return True
        return False

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
            
            # Initialize thumbs-up detection status
            thumbs_up_detected = False

            # Draw the hand landmarks if any hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Check if thumbs up gesture is detected
                    if is_thumbs_up(hand_landmarks):
                        thumbs_up_detected = True

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

            # Update the status text based on thumbs-up detection
            if thumbs_up_detected:
                status_text.value = "Thumbs up detected!"
            else:
                status_text.value = ""

            # Update the page layout
            page.update()

    # Run the update_frame function in a separate thread to avoid blocking the main thread
    threading.Thread(target=update_frame, daemon=True).start()

    # Run the app
    page.update()

# Run the Flet app
ft.app(target=main)
