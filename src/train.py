import os
import yaml
import tensorflow as tf
from datetime import datetime
from pathlib import Path
import logging


from models.crnn import CRNN
from data.data_loader import AudioDataLoader
from utils.audio_processor import AudioProcessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionRecognitionTrainer:
    def __init__(self, config_path='config/config.yaml'):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        
        self.model_dir = self.config['model_dir']
        self.log_dir = os.path.join(self.config['log_dir'], datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        
        self.audio_processor = AudioProcessor(config_path)
        self.data_loader = AudioDataLoader(config_path)
        self.model = CRNN(config_path)
        
        
        self.model.summary()
    
    def train(self):
        
        
        (X_train, y_train), (X_val, y_val), _ = self.data_loader.load_dataset(
            self.config['data_dir']
        )
        
        
        train_dataset = self.data_loader.create_tf_dataset(X_train, y_train, is_training=True)
        val_dataset = self.data_loader.create_tf_dataset(X_val, y_val)
        
        
        steps_per_epoch = len(X_train) // self.config['batch_size']
        validation_steps = len(X_val) // self.config['batch_size']
        
        
        callbacks = [
            
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            
            tf.keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(self.model_dir, 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            
            tf.keras.callbacks.TensorBoard(
                log_dir=self.log_dir,
                histogram_freq=1,
                update_freq='batch'
            ),
            
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=3,
                min_lr=1e-6,
                verbose=1
            )
        ]
        
        
        class_weights = self.data_loader.get_class_weights(y_train)
        
        
        logger.info("Starting model training...")
        
        history = self.model.model.fit(
            train_dataset,
            epochs=self.config['epochs'],
            steps_per_epoch=steps_per_epoch,
            validation_data=val_dataset,
            validation_steps=validation_steps,
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1
        )
        
        
        final_model_path = os.path.join(self.model_dir, 'final_model.h5')
        self.model.save(final_model_path)
        logger.info(f"Training completed. Model saved to {final_model_path}")
        
        return history

if __name__ == "__main__":
    
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        try:
            for device in physical_devices:
                tf.config.experimental.set_memory_growth(device, True)
            logger.info("GPU memory growth enabled")
        except RuntimeError as e:
            logger.error(f"Error setting GPU memory growth: {e}")
    
    
    trainer = EmotionRecognitionTrainer()
    trainer.train()
