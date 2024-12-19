import os
import numpy as np

def generate_no_gesture_sequence(sequence_dir, start_seq_num=1, num_sequences=50, frames_per_sequence=30, num_hands=2):
    for seq in range(start_seq_num, start_seq_num + num_sequences):
        # Creëer een subdirectory voor elke sequentie
        seq_dir = os.path.join(sequence_dir, f'sequence_{seq:03d}')
        os.makedirs(seq_dir, exist_ok=True)
        print(f"Generating no_gesture sequence {seq}/{start_seq_num + num_sequences - 1} in {seq_dir}")
        
        for frame_idx in range(frames_per_sequence):
            landmarks = []
            for hand in range(num_hands):
                for lm in range(21):  # 21 landmarks per hand
                    x = np.random.uniform(0, 1)
                    y = np.random.uniform(0, 1)
                    z = np.random.uniform(-0.1, 0.1)
                    landmarks.extend([x, y, z])
            # Sla elke frame op als een npy-bestand
            frame_path = os.path.join(seq_dir, f"{frame_idx}.npy")
            np.save(frame_path, landmarks)
        
        print(f"No_gesture sequence {seq} completed")

def get_last_sequence_number(sequence_dir):
    seq_numbers = [int(d.split('_')[1]) for d in os.listdir(sequence_dir) if d.startswith('sequence_')]
    return max(seq_numbers) if seq_numbers else 0


if __name__ == "__main__":
    # Definieer de directory waar no_gesture sequenties moeten worden opgeslagen
    data_dir = 'data'
    no_gesture_dir = os.path.join(data_dir, 'no_gesture')
    os.makedirs(no_gesture_dir, exist_ok=True)
    
    # Genereer no_gesture data voor twee handen
    print("Generating no_gesture sequences for two hands...")
    generate_no_gesture_sequence(no_gesture_dir, num_sequences=50, num_hands=2)
    
    # Bepaal het laatste sequentienummer voor twee handen
    last_seq_num = get_last_sequence_number(no_gesture_dir)
    
    # Genereer no_gesture data voor één hand, beginnend vanaf het volgende sequentienummer
    print("\nGenerating no_gesture sequences for one hand...")
    generate_no_gesture_sequence(no_gesture_dir, start_seq_num=last_seq_num + 1, num_sequences=50, num_hands=1)
    
    print("\nAll no_gesture data generated successfully.")