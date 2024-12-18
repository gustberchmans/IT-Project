import cv2
import numpy as np
from tensorflow.python.keras.models import load_model
import mediapipe as mp
from collections import deque


model1 = load_model('./models/my_model.h5')
model2 = load_model('./models/Eerst_model.h5')
model3 = load_model('./models/Goed_Fast_model.h5')

actions = {
    'Hello': ['Hello', 'no_gesture'],
    'Eerst': ['Eerst', 'no_gesture'],
    'Goed': ['Goed', 'no_gesture']
}

models_info = {
    'Hello': {'model': model1, 'features': 63},
    'Eerst': {'model': model2, 'features': 63}, 
    'Goed': {'model': model3, 'features': 63}   
}

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.75, 
    min_tracking_confidence=0.75, 
    max_num_hands=2
)
mp_drawing = mp.solutions.drawing_utils

sequence = deque(maxlen=30)  

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    num_hands = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
    cv2.putText(frame, f'Hands detected: {num_hands}', (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        try:
            landmarks = []
            for hand_landmarks in results.multi_hand_landmarks:
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])

            if len(landmarks) == 63:
                zeros = [0.0] * 63
                landmarks.extend(zeros)
            elif len(landmarks) == 126:
                pass
            else:
                print(f"Unexpected number of landmarks: {len(landmarks)}")
                continue

            sequence.append(landmarks)

            if len(sequence) == 30:
                sequence_array = np.array(sequence)

                predictions = {}
                for model_name, info in models_info.items():
                    model = info['model']
                    expected_features = info['features']

                    if expected_features == 63:
                        single_hand_landmarks = sequence_array[:, :63].reshape(1, 30, 63)
                        pred = model.predict(single_hand_landmarks, verbose=0)[0]
                    elif expected_features == 126:
                        input_data_full = sequence_array.reshape(1, 30, 126)
                        pred = model.predict(input_data_full, verbose=0)[0]
                    else:
                        print(f"Model {model_name} heeft een onverwachte feature grootte.")
                        continue

                    pred_idx = np.argmax(pred)
                    confidence = pred[pred_idx]
                    label = actions[model_name][pred_idx]
                    predictions[model_name] = (label, confidence)


                    y_offset = 30
                    for model_name, (label, confidence) in predictions.items():
                        if confidence > 0.7:
                            color = (0, 255, 0) 
                        elif confidence > 0.4:
                            color = (0, 255, 255)  
                        else:
                            color = (0, 0, 255) 

                        cv2.putText(frame, f'{model_name}: {label} ({confidence:.2f})', 
                                    (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
                        y_offset += 30

        except Exception as e:
            print(f"Error: {str(e)}")

    else:
        cv2.putText(frame, 'No Gesture', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('Gesture Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()