import os
import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import time

GESTURES = {
    'hallo',
    'no_gesture'
}

HERHALINGEN = 30
FRAMES = 30
WAIT_TIME = 1  


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 60)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

for gesture_name in GESTURES:
    class_dir = os.path.join('data', gesture_name)
    os.makedirs(class_dir, exist_ok=True)
    existing_sequences = len(os.listdir(class_dir))
    
    print(f"\nStarting collection for {gesture_name}")
    print("Press 'q' to begin automated collection")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, f"Ready to collect {gesture_name}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press 'q' to start", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    for sequence in range(existing_sequences, existing_sequences + HERHALINGEN):
        sequence_dir = os.path.join(class_dir, str(sequence))
        os.makedirs(sequence_dir, exist_ok=True)
        
        frame_buffer = deque(maxlen=FRAMES)
        
        frames_collected = 0
        while frames_collected < FRAMES:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # frame = cv2.flip(frame, 1)
            frame_buffer.append(frame.copy())
            frames_collected += 1
            
            cv2.putText(frame, f"Recording: {frames_collected}/{FRAMES}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
        
        print(f"Processing sequence {sequence}...")
        for idx, frame in enumerate(frame_buffer):
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            landmarks = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
            
            if len(landmarks) in [63, 126]:  
                np.save(os.path.join(sequence_dir, f"{idx}.npy"), landmarks)
            else:
                print(f"Skipping frame {idx} - unexpected shape: {len(landmarks)}")
        
        print(f"Sequence {sequence} completed")
        
        start_time = time.time()
        while time.time() - start_time < WAIT_TIME:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                remaining = int(WAIT_TIME - (time.time() - start_time))
                cv2.putText(frame, f"Next sequence in {remaining}s", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('frame', frame)
                cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
print("Data collection complete")
