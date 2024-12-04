import os
import mediapipe as mp
import numpy as np
import cv2

dir = './data'
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)

data = []
labels = []

def extract_landmarks(results):
    landmarks = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
    else:
        landmarks.extend([0] * 63) 
    return landmarks

print("Processing data directories...")
for gesture in os.listdir(dir):
    gesture_path = os.path.join(dir, gesture)
    if not os.path.isdir(gesture_path):
        continue
        
    print(f"\nProcessing gesture: {gesture}")
    
    for sequence in os.listdir(gesture_path):
        sequence_path = os.path.join(gesture_path, sequence)
        if not os.path.isdir(sequence_path):
            continue
            
        print(f"Processing sequence: {sequence}")
        sequence_data = []
        
        for frame_num in range(15): 
            frame_path = os.path.join(sequence_path, str(frame_num) + '.npy')
            try:
                frame_data = np.load(frame_path)
                sequence_data.append(frame_data)
            except Exception as e:
                print(f"Error loading {frame_path}: {e}")
                continue
        
        if sequence_data:
            data.append(sequence_data)
            labels.append(gesture)

data = np.array(data)
labels = np.array(labels)

print(f"\nFinal data shape: {data.shape}")
print(f"Final labels shape: {labels.shape}")
print(f"Unique labels: {np.unique(labels)}")

np.save(os.path.join(dir, 'data.npy'), data)
np.save(os.path.join(dir, 'labels.npy'), labels)
print("Data saved successfully")
