import os
import numpy as np
import tensorflow as tf
import yaml
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioDataLoader:
    def __init__(self, config_path='../config/config.yaml'):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.batch_size = self.config['batch_size']
        self.input_shape = tuple(self.config['input_shape'])
        
        
        os.makedirs(self.config['processed_dir'], exist_ok=True)
        
        
        self.label_encoder = LabelEncoder()
    
    def load_dataset(self, data_dir, test_size=0.2, val_size=0.1, random_state=42):
        
        
        
        
        
        audio_paths = []
        labels = []
        
        
        
        
        
        
        
        
        
        
        
        
        
        num_samples = 100  
        dummy_spectrogram = np.zeros(self.input_shape)
        
        X = np.array([dummy_spectrogram] * num_samples)
        y = np.random.randint(0, self.config['num_classes'], num_samples)
        
        
        y_encoded = self.label_encoder.fit_transform(y)
        
        
        y_one_hot = tf.keras.utils.to_categorical(
            y_encoded, 
            num_classes=len(self.label_encoder.classes_)
        )
        
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_one_hot, test_size=test_size, random_state=random_state, stratify=y
        )
        
        
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, 
            test_size=val_size_adjusted, 
            random_state=random_state,
            stratify=np.argmax(y_train, axis=1)
        )
        
        logger.info(f"Dataset loaded with {len(X_train)} training, {len(X_val)} validation, and {len(X_test)} test samples.")
        
        return (X_train, y_train), (X_val, y_val), (X_test, y_test)
    
    def create_tf_dataset(self, X, y, is_training=False):
        
        dataset = tf.data.Dataset.from_tensor_slices((X, y))
        
        if is_training:
            
            dataset = dataset.shuffle(buffer_size=1024)
            dataset = dataset.repeat()
        
        
        dataset = dataset.batch(self.batch_size)
        
        
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset
    
    def get_class_weights(self, y):
        
        from sklearn.utils.class_weight import compute_class_weight
        
        
        y_indices = np.argmax(y, axis=1)
        
        
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_indices),
            y=y_indices
        )
        
        
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
        
        return class_weight_dict
