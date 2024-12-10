import os
import numpy as np
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, LSTMV1
from tensorflow.python.keras.optimizer_v2.adam import Adam
from tensorflow.python.keras.regularizers import l2
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from tensorflow.python.keras.utils.np_utils import to_categorical
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint

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
labels = tf.keras.utils.to_categorical(labels)
print(f"Labels shape: {labels.shape}")


X_train_val, X_test, y_train_val, y_test = train_test_split(
    data, labels, test_size=0.2, random_state=42, stratify=labels
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=0.2, random_state=42, stratify=y_train_val
)

print(f"Train set: {X_train.shape[0]} samples")
print(f"Validation set: {X_val.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")


model = Sequential([
    LSTMV1(128, return_sequences=True, 
         input_shape=(timesteps, features),
         kernel_regularizer=l2(0.01)),
    Dropout(0.3),
    
    LSTMV1(64, return_sequences=True,
         kernel_regularizer=l2(0.01)),
    Dropout(0.3),
    
    LSTMV1(32, kernel_regularizer=l2(0.01)),
    Dropout(0.3),
    
    Dense(32, activation='relu',
          kernel_regularizer=l2(0.01)),
    Dropout(0.3),
    
    Dense(labels.shape[1], activation='softmax')
])


optimizer = Adam(learning_rate=0.0005)
model.compile(
    optimizer=optimizer,
    loss='categorical_crossentropy',
    metrics=['accuracy', 'Precision', 'Recall']
)


early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    'best_model.h5',
    monitor='val_loss',
    save_best_only=True
)


model_dir = './models'
os.makedirs(model_dir, exist_ok=True)


history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=16,
    callbacks=[early_stopping, checkpoint]
)


best_model_path = os.path.join(model_dir, 'best_model.h5')
final_model_path = os.path.join(model_dir, 'final_model.h5')

try:
    
    model.save(final_model_path)
    print(f"Final model saved to: {final_model_path}")
    
    
    if os.path.exists(best_model_path):
        best_model = tf.keras.models.load_model(best_model_path)
        print(f"Best model loaded from: {best_model_path}")
    else:
        print("No best model checkpoint found, using final model")
        best_model = model
    
    
    val_metrics = best_model.evaluate(X_val, y_val)
    test_metrics = best_model.evaluate(X_test, y_test)
    
    print("\nValidation Results:")
    print(f"Loss: {val_metrics[0]:.4f}")
    print(f"Accuracy: {val_metrics[1]:.4f}")
    
    print("\nTest Results:")
    print(f"Loss: {test_metrics[0]:.4f}")
    print(f"Accuracy: {test_metrics[1]:.4f}")
    
except Exception as e:
    print(f"Error saving/loading model: {str(e)}")


import matplotlib.pyplot as plt

plt.figure(figsize=(15, 5))


plt.subplot(1, 3, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()


plt.subplot(1, 3, 2)
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()


from sklearn.metrics import confusion_matrix
import seaborn as sns

plt.subplot(1, 3, 3)
y_pred = np.argmax(best_model.predict(X_val), axis=1)
y_true = np.argmax(y_val, axis=1)
cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix\n(Validation Set)')
plt.xlabel('Predicted')
plt.ylabel('True')

plt.tight_layout()
plt.show()
