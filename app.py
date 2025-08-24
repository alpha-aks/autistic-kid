import os
import base64
import tempfile
import numpy as np
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import soundfile as sf
import io


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")






@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_audio():
    
    try:
        
        audio_data = request.files.get('audio')
        
        if not audio_data:
            return jsonify({'error': 'No audio data provided'}), 400
        
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_data.save(temp_audio.name)
            
            
            
            
            
            result = {
                'success': True,
                'predicted_emotion': 'happy',  
                'confidence': 0.87,  
                'all_predictions': [
                    {'emotion': 'happy', 'confidence': 0.87},
                    {'emotion': 'neutral', 'confidence': 0.10},
                    {'emotion': 'sad', 'confidence': 0.02},
                    {'emotion': 'angry', 'confidence': 0.01}
                ]
            }
            
            
            os.unlink(temp_audio.name)
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('start_recording')
def handle_start_recording():
    
    emit('recording_status', {'status': 'started'})

@socketio.on('stop_recording')
def handle_stop_recording():
    
    emit('recording_status', {'status': 'stopped'})

if __name__ == '__main__':
    
    os.makedirs('static/recordings', exist_ok=True)
    
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
