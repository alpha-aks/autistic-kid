import os
import numpy as np
import yaml
import argparse
import json
from pathlib import Path
import logging

import tensorflow as tf
import soundfile as sf


from models.crnn import CRNN
from utils.audio_processor import AudioProcessor


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionPredictor:
    def __init__(self, config_path='config/config.yaml', model_path=None):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        
        self.audio_processor = AudioProcessor(config_path)
        
        
        self.model = CRNN(config_path)
        if model_path is None:
            model_path = os.path.join(self.config['model_dir'], 'best_model.h5')
        
        if os.path.exists(model_path):
            self.model.load(model_path)
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.error(f"Model not found at {model_path}")
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        
        self.class_names = ['happy', 'sad', 'angry', 'neutral']
    
    def predict_emotion(self, audio_path):
        
        try:
            
            spectrogram = self.audio_processor.process_file(audio_path)
            
            if spectrogram is None:
                return {
                    'success': False,
                    'error': 'Failed to process audio file',
                    'predictions': None
                }
            
            
            spectrogram = np.expand_dims(spectrogram, axis=0)
            
            
            predictions = self.model.model.predict(spectrogram, verbose=0)
            
            
            predicted_class_idx = np.argmax(predictions[0])
            predicted_emotion = self.class_names[predicted_class_idx]
            predicted_confidence = float(predictions[0][predicted_class_idx])
            
            
            all_predictions = [
                {
                    'emotion': emotion,
                    'confidence': float(confidence)
                }
                for emotion, confidence in zip(self.class_names, predictions[0])
            ]
            
            
            all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return {
                'success': True,
                'predicted_emotion': predicted_emotion,
                'confidence': predicted_confidence,
                'all_predictions': all_predictions
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'predictions': None
            }

def main():
    
    parser = argparse.ArgumentParser(description='Predict emotion from speech')
    parser.add_argument('audio_file', type=str, help='Path to the audio file')
    parser.add_argument('--model', type=str, help='Path to the trained model')
    parser.add_argument('--config', type=str, default='config/config.yaml', 
                       help='Path to the config file')
    
    args = parser.parse_args()
    
    
    try:
        predictor = EmotionPredictor(
            config_path=args.config,
            model_path=args.model
        )
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {str(e)}")
        return
    
    
    result = predictor.predict_emotion(args.audio_file)
    
    
    if result['success']:
        print("\nEmotion Prediction Results:")
        print(f"Predicted Emotion: {result['predicted_emotion']}")
        print(f"Confidence: {result['confidence']:.2%}\n")
        
        print("All Predictions:")
        for pred in result['all_predictions']:
            print(f"- {pred['emotion']}: {pred['confidence']:.2%}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
