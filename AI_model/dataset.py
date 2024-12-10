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
        
        hand_landmarks = results.multi_hand_landmarks[0]
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
    else:
        
        landmarks.extend([0] * 63)
    return landmarks

print("Processing data directories...")
for class_name in ['gesture', 'no_gesture']:
    class_path = os.path.join(dir, class_name)
    if not os.path.isdir(class_path):
        print(f"Skipping {class_path} - not a directory")
        continue
        
    print(f"\nProcessing class: {class_name}")
    
    
    for sequence in os.listdir(class_path):
        sequence_path = os.path.join(class_path, sequence)
        if not os.path.isdir(sequence_path):
            continue
            
        print(f"Processing sequence: {sequence}")
        sequence_data = []
        
        
        for frame_num in range(10):  
            frame_path = os.path.join(sequence_path, str(frame_num) + '.npy')
            try:
                frame_data = np.load(frame_path)
                if len(frame_data) == 63:  
                    sequence_data.append(frame_data)
                else:
                    print(f"Skipping frame {frame_num} - incorrect shape: {len(frame_data)}")
            except Exception as e:
                print(f"Error loading {frame_path}: {e}")
                continue
        
        while len(sequence_data) < 10:
            sequence_data.append(np.zeros(63))
        
        if len(sequence_data) == 10 and all(len(frame) == 63 for frame in sequence_data):  
            sequence_array = np.array(sequence_data)
            if sequence_array.shape == (10, 63):
                data.append(sequence_array)
                if class_name == 'gesture':
                    labels.append(1)
                else:
                    labels.append(0)
            else:
                print(f"Skipping sequence {sequence} - wrong shape: {sequence_array.shape}")


data = np.array(data, dtype=np.float32)
labels = np.array(labels, dtype=np.int32)

print(f"\nFinal dataset shape: {data.shape}")
print(f"Labels shape: {labels.shape}")
print(f"Number of gesture samples: {np.sum(labels == 1)}")
print(f"Number of no_gesture samples: {np.sum(labels == 0)}")

np.save(os.path.join(dir, 'data.npy'), data)
np.save(os.path.join(dir, 'labels.npy'), labels)
print("Data saved successfully")
