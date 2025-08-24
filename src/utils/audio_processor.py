import os
import numpy as np
import librosa
import soundfile as sf
import yaml
from pathlib import Path
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, config_path='../config/config.yaml'):
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        
        os.makedirs(self.config['processed_dir'], exist_ok=True)
    
    def load_audio(self, file_path):
        
        try:
            
            y, sr = librosa.load(file_path, sr=self.config['sample_rate'])
            return y, sr
        except Exception as e:
            logger.error(f"Error loading audio file {file_path}: {str(e)}")
            return None, None
    
    def preprocess_audio(self, y, sr):
        
        
        y_trimmed, _ = librosa.effects.trim(y)
        
        
        y_normalized = librosa.util.normalize(y_trimmed)
        
        
        target_length = self.config['duration'] * self.config['sample_rate']
        
        
        if len(y_normalized) > target_length:
            y_processed = y_normalized[:target_length]
        else:
            padding = target_length - len(y_normalized)
            y_processed = np.pad(y_normalized, (0, padding), mode='constant')
        
        return y_processed
    
    def extract_mel_spectrogram(self, y, sr):
        
        
        S = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=self.config['n_fft'],
            hop_length=self.config['hop_length'],
            n_mels=self.config['n_mels'],
            fmin=self.config['fmin'],
            fmax=self.config['fmax']
        )
        
        
        S_dB = librosa.power_to_db(S, ref=np.max)
        
        
        S_norm = (S_dB - S_dB.min()) / (S_dB.max() - S_dB.min())
        
        
        S_norm = np.expand_dims(S_norm, axis=-1)
        
        return S_norm
    
    def process_file(self, file_path, save=False):
        
        
        y, sr = self.load_audio(file_path)
        if y is None:
            return None
        
        
        y_processed = self.preprocess_audio(y, sr)
        
        
        spectrogram = self.extract_mel_spectrogram(y_processed, sr)
        
        
        if save:
            output_path = os.path.join(
                self.config['processed_dir'],
                f"{Path(file_path).stem}.npy"
            )
            np.save(output_path, spectrogram)
            logger.info(f"Processed and saved: {output_path}")
        
        return spectrogram
