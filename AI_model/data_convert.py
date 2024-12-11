import numpy as np
import pandas as pd
import os


dir = './data'
data = np.load(os.path.join(dir, 'data.npy'))
labels = np.load(os.path.join(dir, 'labels.npy'))

try:
    
    samples, frames, features = data.shape
    data_reshaped = data.reshape(samples, frames * features)
    
    
    feature_cols = [f'frame{i}_feature{j}' for i in range(frames) for j in range(features)]
    
    
    df = pd.DataFrame(data_reshaped, columns=feature_cols)
    df['label'] = labels
    
    
    csv_path = os.path.join(dir, 'gesture_data.csv')
    df.to_csv(csv_path, index=False)
    
    
    print(f"Data saved to: {csv_path}")
    print(f"Shape of data: {df.shape}")
    print("\nUnique labels and their counts:")
    print(df['label'].value_counts())
    
    
    print("\nUnique labels found:", np.unique(labels))

except Exception as e:
    print(f"Error converting data: {e}")