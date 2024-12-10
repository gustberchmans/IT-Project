import os
import cv2
import mediapipe as mp
import numpy as np


CLASSES = ['gesture', 'no_gesture']  
HERHALINGEN = 30  
FRAMES = 30     


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=2)
mp_draw = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")


for class_name in CLASSES:
    class_dir = os.path.join('data', class_name)
    existing_sequences = len(os.listdir(class_dir))
    
    for sequence in range(existing_sequences, existing_sequences + HERHALINGEN):
        os.makedirs(os.path.join(class_dir, str(sequence)), exist_ok=True)
        print(f"\nCollecting {class_name} sequence {sequence}")
        
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            
            
            if class_name == 'gesture':
                instruction = "Show hand gesture"
            else:
                instruction = "Keep hands out of frame"
                
            cv2.putText(frame, f"Class: {class_name} - Sequence {sequence}", 
                      (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            cv2.putText(frame, instruction, 
                      (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.putText(frame, 'Press Q when ready', 
                      (10,110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
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
            
            
            landmarks = []
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
            
            
            if (class_name == 'gesture' and len(landmarks) > 0) or (class_name == 'no_gesture' and len(landmarks) > 0):
                npy_path = os.path.join('data', class_name, str(sequence), str(frames_collected))
                np.save(npy_path, landmarks if landmarks else np.zeros(63))
                frames_collected += 1
                
                cv2.putText(frame, f'Recording frame {frames_collected}/{FRAMES}', 
                          (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            
            cv2.imshow('frame', frame)
            cv2.waitKey(100)

cap.release()
cv2.destroyAllWindows()
print("Data collection complete")
