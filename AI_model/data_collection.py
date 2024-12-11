import os
import cv2
import mediapipe as mp
import numpy as np
from collections import deque

GESTURES = {
    'eerst',
    'no_gesture'
}

HERHALINGEN = 30
FRAMES = 30
BUFFER_SIZE = FRAMES  

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  

if not cap.isOpened():
    raise IOError("Cannot open webcam")

for gesture_name in GESTURES:
    class_dir = os.path.join('data', gesture_name)
    os.makedirs(class_dir, exist_ok=True)
    existing_sequences = len(os.listdir(class_dir))
    
    for sequence in range(existing_sequences, existing_sequences + HERHALINGEN):
        sequence_dir = os.path.join(class_dir, str(sequence))
        os.makedirs(sequence_dir, exist_ok=True)
        
        
        frame_buffer = deque(maxlen=BUFFER_SIZE)
        landmark_buffer = deque(maxlen=BUFFER_SIZE)
        
        print(f"\nReady to collect {gesture_name} sequence {sequence}")
        print("Press 'q' to start recording")
        
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' when ready", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        print("Recording...")
        frames_collected = 0
        
        
        while frames_collected < FRAMES:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            frame_buffer.append(frame.copy())
            frames_collected += 1
            
            
            cv2.putText(frame, f"Recording: {frames_collected}/{FRAMES}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)

        print("Processing frames...")
        
        for idx, frame in enumerate(frame_buffer):
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            landmarks = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
            
            
            np.save(os.path.join(sequence_dir, f"{idx}.npy"),
                   landmarks if landmarks else np.zeros(63))

        print(f"Sequence {sequence} completed")

cap.release()
cv2.destroyAllWindows()
print("Data collection complete")
