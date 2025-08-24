class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.isRecording = false;
        this.audioContext = null;
        this.analyser = null;
        this.stream = null;
        this.recordedAudio = null;
        
        // DOM Elements
        this.recordButton = document.getElementById('recordButton');
        this.stopButton = document.getElementById('stopButton');
        this.analyzeButton = document.getElementById('analyzeButton');
        this.statusElement = document.getElementById('recordingStatus');
        this.statusText = this.statusElement.querySelector('.status-text');
        this.statusDot = this.statusElement.querySelector('.status-dot');
        
        // Initialize event listeners
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        this.recordButton.addEventListener('click', () => this.startRecording());
        this.stopButton.addEventListener('click', () => this.stopRecording());
        this.analyzeButton.addEventListener('click', () => this.analyzeRecording());
    }
    
    async startRecording() {
        try {
            // Request microphone access
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Set up audio context and analyzer
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;
            
            // Create media stream source
            const source = this.audioContext.createMediaStreamSource(this.stream);
            source.connect(this.analyser);
            
            // Initialize MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.stream);
            this.audioChunks = [];
            
            // Handle data available event
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            
            // Handle recording stop
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.recordedAudio = URL.createObjectURL(audioBlob);
                
                // Enable analyze button
                this.analyzeButton.disabled = false;
                
                // Update UI
                this.statusText.textContent = 'Recording complete';
                this.statusDot.style.backgroundColor = '#28a745'; // Green
                
                // Emit event
                const event = new CustomEvent('recordingComplete', { detail: { audioUrl: this.recordedAudio } });
                document.dispatchEvent(event);
            };
            
            // Start recording
            this.mediaRecorder.start(100); // Collect data every 100ms
            this.isRecording = true;
            
            // Update UI
            this.recordButton.disabled = true;
            this.stopButton.disabled = false;
            this.analyzeButton.disabled = true;
            this.statusElement.classList.add('recording');
            this.statusText.textContent = 'Recording...';
            this.statusDot.style.backgroundColor = '#dc3545'; // Red
            
            // Start visualization
            this.visualize();
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please ensure you have granted microphone permissions.');
            this.reset();
        }
    }
    
    stopRecording() {
        if (this.isRecording && this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
            this.stream.getTracks().forEach(track => track.stop());
            this.isRecording = false;
            
            // Update UI
            this.recordButton.disabled = false;
            this.stopButton.disabled = true;
        }
    }
    
    visualize() {
        if (!this.isRecording || !this.analyser) return;
        
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const draw = () => {
            if (!this.isRecording) return;
            
            requestAnimationFrame(draw);
            
            this.analyser.getByteTimeDomainData(dataArray);
            
            // Emit visualization data
            const event = new CustomEvent('audioData', { detail: { data: Array.from(dataArray) } });
            document.dispatchEvent(event);
        };
        
        draw();
    }
    
    async analyzeRecording() {
        if (!this.recordedAudio) {
            console.error('No recording available for analysis');
            return;
        }
        
        try {
            // Show loading state
            this.analyzeButton.disabled = true;
            this.analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            
            // Convert blob to file
            const response = await fetch(this.recordedAudio);
            const blob = await response.blob();
            const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
            
            // Create form data
            const formData = new FormData();
            formData.append('audio', file);
            
            // Send to server for analysis
            const result = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            
            if (!result.ok) {
                throw new Error('Analysis failed');
            }
            
            const data = await result.json();
            
            // Emit analysis complete event
            const event = new CustomEvent('analysisComplete', { detail: data });
            document.dispatchEvent(event);
            
        } catch (error) {
            console.error('Error analyzing recording:', error);
            alert('Error analyzing recording. Please try again.');
        } finally {
            // Reset button state
            this.analyzeButton.disabled = false;
            this.analyzeButton.innerHTML = '<i class="fas fa-chart-line"></i> Analyze';
        }
    }
    
    reset() {
        this.isRecording = false;
        this.audioChunks = [];
        this.recordedAudio = null;
        
        // Stop all tracks in the stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        
        // Reset UI
        this.recordButton.disabled = false;
        this.stopButton.disabled = true;
        this.analyzeButton.disabled = true;
        this.statusElement.classList.remove('recording');
        this.statusText.textContent = 'Ready to record';
        this.statusDot.style.backgroundColor = '#6c757d'; // Gray
    }
}

// Initialize recorder when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.audioRecorder = new AudioRecorder();
});
