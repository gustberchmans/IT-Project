import pygame
import sys
import cv2
import numpy as np

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 500
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Webcam and Game Example")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Webcam settings
cap = cv2.VideoCapture(0)  # Use the first camera (default webcam)

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not access the webcam.")
    sys.exit()

# Get the webcam frame dimensions
ret, frame = cap.read()
frame_height, frame_width = frame.shape[:2]

# Resize the frame to fit the top half of the screen
top_half_height = screen_height // 2
aspect_ratio = frame_width / frame_height
frame_width_resized = int(top_half_height * aspect_ratio)
frame_resized = cv2.resize(frame, (frame_width_resized, top_half_height))

# Main loop
running = True
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

    # Resize frame to fit the top half of the screen
    frame_resized = cv2.resize(frame, (frame_width_resized, top_half_height))

    # Convert the frame from BGR to RGB (since Pygame uses RGB)
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    # Convert the frame to a Pygame surface
    frame_surface = pygame.surfarray.make_surface(np.transpose(frame_rgb, (1, 0, 2)))

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the webcam feed (top half of the screen)
    screen.blit(frame_surface, (0, 0))  # top left corner of the screen

    # Draw a red vertical rectangle on the bottom half of the screen
    rect_width = 100
    rect_height = 300
    rect_x = (screen_width - rect_width) // 2  # Center the rectangle horizontally
    rect_y = screen_height // 2 + 50  # Position it in the bottom half of the screen

    # Update the display
    pygame.display.flip()

# Release the webcam and quit Pygame
cap.release()
pygame.quit()
sys.exit()
