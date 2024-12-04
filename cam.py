import cv2
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import load_model
import mediapipe as mp


model_path = './data/model.h5'
model = load_model(model_path)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.75, min_tracking_confidence=0.75)


mp_drawing = mp.solutions.drawing_utils


actions = np.array(['action1', 'action2', 'action3']) 


cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break


    frame = cv2.flip(frame, 1)


    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    results = hands.process(rgb_frame)


    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])


        if len(landmarks) == 63: 
            landmarks = np.array(landmarks).reshape(1, -1)
            prediction = model.predict(landmarks)
            action = actions[np.argmax(prediction)]

            
            cv2.putText(frame, action, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)


    cv2.imshow('Hand Gesture Recognition', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()