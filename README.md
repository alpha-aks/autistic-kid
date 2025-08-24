# Speech Emotion Recognition using CRNN

This project implements a hybrid Convolutional Recurrent Neural Network (CRNN) for speech emotion recognition. The model processes audio files, extracts Mel spectrogram features using a CNN, and captures temporal patterns with an LSTM to classify emotions in speech.

## Features

- Audio preprocessing with Mel spectrogram extraction
- Hybrid CRNN architecture for emotion recognition
- Support for multiple emotion classes
- Training and evaluation scripts
- Inference pipeline for real-time prediction
- TensorBoard integration for training visualization

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd speech-emotion-recognition
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
speech-emotion-recognition/
├── config/                    # Configuration files
│   └── config.yaml            # Main configuration
├── data/                      # Data directories
│   ├── raw/                   # Raw audio files
│   └── processed/             # Processed spectrograms
├── logs/                      # Training logs for TensorBoard
├── models/                    # Saved models
├── src/                       # Source code
│   ├── data/                  # Data loading and processing
│   │   └── data_loader.py
│   ├── models/                # Model definitions
│   │   └── crnn.py
│   └── utils/                 # Utility functions
│       └── audio_processor.py
├── tests/                     # Unit tests
├── train.py                   # Training script
├── predict.py                 # Inference script
└── requirements.txt           # Python dependencies
```

## Usage

### Training

1. Prepare your dataset:
   - Place your audio files in the `data/raw` directory
   - Organize them in subdirectories by emotion class
   - Update the configuration in `config/config.yaml` if needed

2. Start training:
   ```bash
   python src/train.py
   ```
   - Training progress can be monitored using TensorBoard:
     ```bash
     tensorboard --logdir=logs/
     ```

### Inference

To predict emotion from an audio file:

```bash
python src/predict.py path/to/audio_file.wav
```

Optional arguments:
- `--model`: Path to a custom trained model (default: models/best_model.h5)
- `--config`: Path to a custom config file (default: config/config.yaml)

## Model Architecture

The CRNN model consists of:

1. **Feature Extraction (CNN)**
   - Multiple Conv2D + BatchNorm + MaxPooling blocks
   - Learns local patterns in Mel spectrograms

2. **Temporal Processing (LSTM)**
   - Bidirectional LSTM layer
   - Captures sequential dependencies in audio features

3. **Classification Head**
   - Dense layers with dropout
   - Softmax output for emotion classification

## Configuration

Edit `config/config.yaml` to adjust:
- Audio processing parameters
- Model architecture
- Training hyperparameters
- File paths and directories

## Dataset

This implementation is designed to work with any speech emotion dataset. The expected structure is:

```
data/raw/
├── happy/
│   ├── audio1.wav
│   └── audio2.wav
├── sad/
│   ├── audio3.wav
│   └── audio4.wav
└── ...
```

## Performance

Model performance depends on the dataset and training configuration. Typical metrics to monitor:
- Training/validation accuracy
- Training/validation loss
- Per-class precision, recall, and F1-score

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This implementation is based on the hybrid CRNN architecture for speech emotion recognition.
- Uses Librosa for audio processing and TensorFlow/Keras for deep learning.
