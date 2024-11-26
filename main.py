import pygame
import sys
import cv2
import numpy as np
import mediapipe as mp
import math

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 500
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Webcam + Full-Body Recognition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.Font(None, 74)

# Webcam settings
cap = cv2.VideoCapture(0)  # Use the first camera (default webcam)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    sys.exit()

# MediaPipe hands setup for detecting up to 2 hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# MediaPipe Pose setup for full body recognition
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def recognize_asl_letter(landmarks):
    """
    A basic example of recognizing letters "A", "B", and "C"
    using relative distances of certain hand landmarks.
    This is a very simplified approximation.
    """

    # Example letter "A": all fingers curled except the thumb
    if (landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y >
            landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y >
            landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y >
            landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y >
            landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x >
            landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x):
        return "A"

    # Example letter "B": All fingers extended and close together, thumb across palm
    if (
        # All four fingers should be straight (tip above PIP joint)
        landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < 
            landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < 
            landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < 
            landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < 
            landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y and
        # All four fingers should be roughly aligned vertically
        abs(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x - 
            landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x) < 0.05 and
        abs(landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x - 
            landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x) < 0.05 and
        abs(landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x - 
            landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].x) < 0.05 and
        # Thumb should be lower than index finger PIP, resting across palm
        landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y > 
            landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y):
        return "B"

    # Example letter "C": Hand forming a "C" shape, fingers curved
    distance_thumb_index = calculate_distance(
        landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP])
    distance_thumb_pinky = calculate_distance(
        landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
        landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP])
    
    if distance_thumb_index > 0.05 and distance_thumb_pinky > 0.1:
        return "C"

    # If no recognized gesture, return empty
    return ""


# Main loop
running = True
recognized_letter = ""
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    # Process the frame with MediaPipe for hand detection
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_hands = hands.process(frame_rgb)
    results_pose = pose.process(frame_rgb)

    # Draw hand landmarks and recognize ASL letter if a hand is detected
    if results_hands.multi_hand_landmarks:
        for hand_landmarks in results_hands.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Recognize ASL letter based on landmarks (dummy function)
            recognized_letter = recognize_asl_letter(hand_landmarks)
    
    # Draw body landmarks
    if results_pose.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Resize frame to fit the top half of the screen
    frame_resized = cv2.resize(frame, (screen_width, screen_height // 2))

    # Convert the frame from BGR to RGB (since Pygame uses RGB)
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Convert the frame to a Pygame surface
    frame_surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the webcam feed (top half of the screen)
    screen.blit(frame_surface, (0, 0))  # top left corner of the screen

    # Draw the recognized letter as text on the bottom half of the screen
    text_surface = font.render(f"Letter: {recognized_letter}", True, BLACK)
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 200))
    screen.blit(text_surface, text_rect)

    # Update the display
    pygame.display.flip()

# Release the webcam and quit Pygame
cap.release()
pose.close()
hands.close()
pygame.quit()
sys.exit()
