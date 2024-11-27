import os
import cv2
import mediapipe as mp
import numpy as np

# Create directory if it doesn't exist
dir = './data'
if not os.path.exists(dir):
    try:
        os.makedirs(dir)
        print(f'Directory created: {dir}')
    except OSError as e:
        print('Problem creating directory:', e)
else:
    print(f'Directory already exists: {dir}')

# Initialize video capture
videoCapture = cv2.VideoCapture(0)
if not videoCapture.isOpened():
    print('Error: Could not access the webcam.')
    exit()
else:
    print('Webcam accessed successfully.')


# Parameters
sets = 3
frames_per_sequence = 30

# Collect data
for j in range(sets):
    class_dir = os.path.join(dir, str(j))
    if not os.path.exists(class_dir):
        try:
            os.makedirs(class_dir)
            print(f'Directory created: {class_dir}')
        except OSError as e:
            print('Problem creating directory:', e)
        
    print('Collecting data for class {}'.format(j))

    for sequence in range(frames_per_sequence):
        frames = []
        print(f'Collecting sequence {sequence} for class {j}')
        
        while len(frames) < frames_per_sequence:
            ret, frame = videoCapture.read()
            if not ret or frame is None:
                print('Error: Failed to capture image')
                break


            cv2.putText(frame, 'Press "Q" to start recording', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow('frame', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

            # Append the frame to the sequence
            frames.append(frame)

        # Save the sequence as a numpy array
        np.save(os.path.join(class_dir, f'sequence_{sequence}.npy'), np.array(frames))

videoCapture.release()
cv2.destroyAllWindows()
