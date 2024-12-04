import os
import cv2
import mediapipe as mp
import numpy as np

GESTURES = ['warm', 'koud', 'hallo', 'huis']
SEQUENCES = 10
FRAMES = 15

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

for gesture in GESTURES:
    for sequence in range(SEQUENCES):
        os.makedirs(os.path.join('data', gesture, str(sequence)), exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

for gesture in GESTURES:
    for sequence in range(SEQUENCES):
        frame_data = []  
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            num_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
            cv2.putText(frame, f'Hands detected: {num_hands}', 
                       (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
            
            cv2.putText(frame, f'Ready to record {gesture} sequence {sequence}?', 
                       (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, 'Press Q when ready', (10,100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, 
                                         mp_hands.HAND_CONNECTIONS)
            
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frames_collected = 0
        while frames_collected < FRAMES:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            if results.multi_hand_landmarks:
                landmarks = []
                
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
                
                if len(results.multi_hand_landmarks) == 1:
                    landmarks.extend([0] * 63)  
                    
                if len(landmarks) == 126:
                    npy_path = os.path.join('data', gesture, str(sequence), str(frames_collected))
                    np.save(npy_path, landmarks)
                    frames_collected += 1
                    
                    cv2.putText(frame, f'Recording {gesture} {sequence} frame {frames_collected}/{FRAMES}', 
                               (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            else:
                landmarks = [0] * 126 
                npy_path = os.path.join('data', gesture, str(sequence), str(frames_collected))
                np.save(npy_path, landmarks)
                frames_collected += 1
                
                cv2.putText(frame, 'No hands detected', (10,50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            
            cv2.imshow('frame', frame)
            key = cv2.waitKey(100)
            if key & 0xFF == ord('q'):
                break
        
        if frames_collected < FRAMES:
            print(f"Warning: Sequence {sequence} for {gesture} incomplete ({frames_collected}/{FRAMES} frames)")
            
        print(f"Completed {gesture} sequence {sequence}")

cap.release()
cv2.destroyAllWindows()
print("Data collection complete")
