import os
import numpy as np

dir = './data'

if not os.path.exists(dir):
    os.makedirs(dir)
    print(f"Created main directory: {dir}")

data = []
labels = []

def get_gesture_classes():
    gesture_classes = []
    for item in os.listdir(dir):
        item_path = os.path.join(dir, item)
        if os.path.isdir(item_path):
            gesture_classes.append(item)
    return gesture_classes

def validate_sequence_directory(sequence_path):
    if not os.path.exists(sequence_path):
        return False
    required_files = [f"{i}.npy" for i in range(30)]  
    existing_files = os.listdir(sequence_path)
    return all(f in existing_files for f in required_files)

print("Processing data directories...")
gesture_classes = get_gesture_classes()

if not gesture_classes:
    print("No gesture classes found. Please run data collection first.")
    exit()

print(f"Found gesture classes: {gesture_classes}")

for class_name in gesture_classes:
    class_path = os.path.join(dir, class_name)
    if not os.path.isdir(class_path):
        print(f"Skipping {class_path} - not a directory")
        continue
        
    print(f"\nProcessing class: {class_name}")
    
    sequences = []
    for item in os.listdir(class_path):
        item_path = os.path.join(class_path, item)
        if os.path.isdir(item_path):
            sequences.append(item)
    
    if not sequences:
        print(f"No sequences found for class {class_name}")
        continue
    
    for sequence in sequences:
        sequence_path = os.path.join(class_path, sequence)
        
        if not validate_sequence_directory(sequence_path):
            print(f"Skipping incomplete sequence: {sequence_path}")
            continue
            
        sequence_data = []
        
        for frame_num in range(30):
            frame_path = os.path.join(sequence_path, f"{frame_num}.npy")
            try:
                frame_data = np.load(frame_path)
                if len(frame_data) in [63, 126]:  
                    
                    if len(frame_data) == 126:
                        frame_data = frame_data[:63]
                    sequence_data.append(frame_data)
                else:
                    print(f"Skipping frame {frame_num} - unexpected shape: {len(frame_data)}")
            except Exception as e:
                print(f"Error loading {frame_path}: {e}")
                continue
        
        if len(sequence_data) == 30:
            sequence_array = np.array(sequence_data)
            if sequence_array.shape == (30, 63):
                data.append(sequence_array)
                labels.append(class_name)
            else:
                print(f"Skipping sequence {sequence} - wrong shape: {sequence_array.shape}")


if data and labels:
    data = np.array(data)
    labels = np.array(labels)

    print(f"\nFinal dataset shape: {data.shape}")
    print(f"Labels shape: {labels.shape}")
    print("Class distribution:")
    for class_name in np.unique(labels):
        count = np.sum(labels == class_name)
        print(f"{class_name}: {count} samples")

    
    np.save(os.path.join(dir, 'data.npy'), data)
    np.save(os.path.join(dir, 'labels.npy'), labels)
    print("Data saved successfully")
else:
    print("No valid data collected. Please check the data collection process.")
