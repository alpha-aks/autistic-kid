import os
import yaml
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
import librosa
import soundfile as sf
from tqdm import tqdm
import pandas as pd
from pathlib import Path
import random


from src.models.crnn import CRNN
from src.data.data_loader import AudioDataLoader
from src.utils.audio_processor import AudioProcessor

class EmotionTrainer:
    def __init__(self, config_path='config/config.yaml'):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        
        os.makedirs(self.config['model_dir'], exist_ok=True)
        os.makedirs(self.config['processed_dir'], exist_ok=True)
        
        
        self.audio_processor = AudioProcessor(config_path)
        self.data_loader = AudioDataLoader(config_path)
        self.model = CRNN(config_path)
        
        
        self.model.summary()
    
    def load_dataset(self, data_dir):
        
        print("Loading dataset...")
        
        
        features = []
        labels = []
        
        
        emotion_folders = [d for d in os.listdir(data_dir) 
                          if os.path.isdir(os.path.join(data_dir, d))]
        
        
        for emotion in tqdm(emotion_folders, desc="Processing emotions"):
            emotion_dir = os.path.join(data_dir, emotion)
            
            
            audio_files = [f for f in os.listdir(emotion_dir) 
                         if f.endswith(('.wav', '.mp3', '.ogg', '.flac'))]
            
            
            for audio_file in tqdm(audio_files, desc=f"Processing {emotion}", leave=False):
                audio_path = os.path.join(emotion_dir, audio_file)
                
                try:
                    
                    spectrogram = self.audio_processor.process_file(audio_path, save=False)
                    
                    if spectrogram is not None:
                        features.append(spectrogram)
                        labels.append(emotion)
                        
                except Exception as e:
                    print(f"Error processing {audio_file}: {str(e)}")
        
        
        X = np.array(features)
        y = np.array(labels)
        
        
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        y_categorical = to_categorical(y_encoded)
        
        print(f"\nDataset loaded with {len(X)} samples")
        print("Class distribution:")
        for i, cls in enumerate(self.label_encoder.classes_):
            print(f"  {cls}: {np.sum(y_encoded == i)} samples")
        
        return X, y_categorical
    
    def train(self, X, y, test_size=0.2, val_size=0.1, random_state=42):
        
        print("\nStarting model training...")
        
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, 
            test_size=val_size_adjusted, 
            random_state=random_state,
            stratify=np.argmax(y_train, axis=1)
        )
        
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        print(f"Test samples: {len(X_test)}")
        
        
        class_weights = self._calculate_class_weights(y_train)
        
        
        callbacks = [
            
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            
            tf.keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(self.config['model_dir'], 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        
        history = self.model.model.fit(
            X_train, y_train,
            batch_size=self.config['batch_size'],
            epochs=self.config['epochs'],
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1
        )
        
        
        final_model_path = os.path.join(self.config['model_dir'], 'final_model.h5')
        self.model.save(final_model_path)
        print(f"\nTraining completed. Model saved to {final_model_path}")
        
        
        print("\nEvaluating on test set...")
        test_loss, test_accuracy = self.model.model.evaluate(X_test, y_test, verbose=0)
        print(f"Test accuracy: {test_accuracy:.4f}")
        
        return history
    
    def _calculate_class_weights(self, y):
        
        from sklearn.utils.class_weight import compute_class_weight
        
        
        y_indices = np.argmax(y, axis=1)
        
        
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_indices),
            y=y_indices
        )
        
        
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        
        print("\nClass weights:")
        for i, cls in enumerate(self.label_encoder.classes_):
            print(f"  {cls}: {class_weight_dict[i]:.2f}")
        
        return class_weight_dict

def main():
    
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        try:
            for device in physical_devices:
                tf.config.experimental.set_memory_growth(device, True)
            print("GPU memory growth enabled")
        except RuntimeError as e:
            print(f"Error setting GPU memory growth: {e}")
    
    
    trainer = EmotionTrainer()
    
    
    data_dir = os.path.join('data', 'raw')
    X, y = trainer.load_dataset(data_dir)
    
    
    trainer.train(X, y)

if __name__ == "__main__":
    main()
