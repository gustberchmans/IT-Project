import os
import mediapipe as mp
import numpy as np
import cv2

# Directory containing the data
dir = './data'

# Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.75, min_tracking_confidence=0.75)

# Initialize arrays to hold data and labels
data = []
labels = []

# Function to extract landmarks
def extract_landmarks(results):
    landmarks = []
    if results.face_landmarks:
        landmarks.extend([[res.x, res.y, res.z] for res in results.face_landmarks.landmark])
    else:
        landmarks.extend([[0, 0, 0]] * 468)  # 468 face landmarks

    if results.left_hand_landmarks:
        landmarks.extend([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark])
    else:
        landmarks.extend([[0, 0, 0]] * 21)  # 21 hand landmarks

    if results.right_hand_landmarks:
        landmarks.extend([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark])
    else:
        landmarks.extend([[0, 0, 0]] * 21)  # 21 hand landmarks

    return landmarks

# Process each class directory
for class_dir in os.listdir(dir):
    class_path = os.path.join(dir, class_dir)
    if not os.path.isdir(class_path):
        continue

    print(f'Processing class directory: {class_dir}')

    # Process each sequence file
    for sequence_file in os.listdir(class_path):
        sequence_path = os.path.join(class_path, sequence_file)
        if not sequence_path.endswith('.npy'):
            continue

        print(f'Processing sequence file: {sequence_file}')

        # Load the sequence
        sequence = np.load(sequence_path)

        # Process each frame in the sequence
        for frame_idx, frame in enumerate(sequence):
            print(f'Processing frame {frame_idx} in sequence {sequence_file}')

            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame and detect holistic landmarks
            results = holistic.process(rgb_frame)

            # Extract landmarks
            landmarks = extract_landmarks(results)

            # Append the landmarks and label to the data and labels arrays
            data.append(landmarks)
            labels.append(class_dir)

# Convert data and labels to numpy arrays
data = np.array(data)
labels = np.array(labels)

# Save data and labels arrays to disk
np.save(os.path.join(dir, 'data.npy'), data)
np.save(os.path.join(dir, 'labels.npy'), labels)

print('Data and labels have been saved.')
