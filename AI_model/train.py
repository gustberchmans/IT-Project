import os
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout
from tensorflow.python.keras.layers import LSTMV1 as LSTM
#from keras.layers.normalization.batch_normalization import BatchNormalization
from tensorflow.python.keras.optimizer_v2.adam import Adam
from tensorflow.python.keras.regularizers import L2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.python.keras.utils.np_utils import to_categorical
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns

dir = './data'
if not os.path.exists(os.path.join(dir, 'data.npy')) or not os.path.exists(os.path.join(dir, 'labels.npy')):
    raise FileNotFoundError(f"Data files not found in {dir}")

data = np.load(os.path.join(dir, 'data.npy'))
labels = np.load(os.path.join(dir, 'labels.npy'))

print(f"Initial data shape: {data.shape}")

scaler = StandardScaler()
samples, timesteps, features = data.shape
data_reshaped = data.reshape(samples, -1)
data_normalized = scaler.fit_transform(data_reshaped)
data = data_normalized.reshape(samples, timesteps, features)

label_encoder = LabelEncoder()
labels = label_encoder.fit_transform(labels)
labels = to_categorical(labels)
num_classes = labels.shape[1]
print(f"Labels shape: {labels.shape}")

X_train_val, X_test, y_train_val, y_test = train_test_split(
    data, labels, test_size=0.1, random_state=50, stratify=labels.argmax(axis=1)
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=0.2, random_state=50, stratify=y_train_val.argmax(axis=1)
)

print(f"Train set: {X_train.shape[0]} samples")
print(f"Validation set: {X_val.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

model = Sequential([
     LSTM(
        128, 
        return_sequences=True, 
        activation='tanh', 
        recurrent_activation='sigmoid', 
        input_shape=(timesteps, features),
        kernel_regularizer=tf.keras.regularizers.l2(0.001)  
    ),
    Dropout(0.3), 
    
    LSTM(
        256, 
        return_sequences=True, 
        activation='tanh', 
        recurrent_activation='sigmoid', 
        kernel_regularizer=tf.keras.regularizers.l2(0.001)  
    ),
    Dropout(0.3), 
    
    LSTM(
        128, 
        return_sequences=False, 
        activation='tanh', 
        recurrent_activation='sigmoid', 
        kernel_regularizer=tf.keras.regularizers.l2(0.001)  
    ),
    Dropout(0.3),
    
    Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    Dropout(0.3),
    
    Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    Dropout(0.3),
    
    Dense(labels.shape[1], activation='softmax')
])

optimizer = Adam(learning_rate=0.001)
model.compile(
    optimizer=optimizer,
    loss='categorical_crossentropy',
    metrics=['categorical_accuracy']
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=0.00001
)

checkpoint = ModelCheckpoint(
    'best_model.h5',
    monitor='val_loss',
    save_best_only=True
)

history = model.fit(
    X_train, 
    y_train,
    epochs=100,
    batch_size=64,
    validation_data=(X_val, y_val),
    callbacks=[early_stopping, reduce_lr, checkpoint]
)

# Save trained model
model_dir = './models'
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'my_model.h5')

try:
    model.save(model_path)
    print(f"Model saved successfully to {model_path}")
except Exception as e:
    print(f"Error saving model: {str(e)}")

predictions = np.argmax(model.predict(X_test), axis=1)
test_labels = np.argmax(y_test, axis=1)

accuracy = accuracy_score(test_labels, predictions)
print(f"Test Accuracy: {accuracy:.2f}")

plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 3, 2)
plt.plot(history.history['categorical_accuracy'], label='Training Accuracy')
plt.plot(history.history['val_categorical_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.subplot(1, 3, 3)
cm = confusion_matrix(test_labels, predictions)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix (Test Set)')
plt.xlabel('Predicted')
plt.ylabel('True')

plt.tight_layout()

diagram_dir = os.path.join(dir, 'diagram')
os.makedirs(diagram_dir, exist_ok=True)
diagram_path = os.path.join(diagram_dir, 'training_history.png')

try:
    plt.savefig(diagram_path)
    print(f"Diagram saved successfully to {diagram_path}")
except Exception as e:
    print(f"Error saving diagram: {str(e)}")

plt.show()
