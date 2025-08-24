class AudioVisualizer {
    constructor() {
        // Canvas setup
        this.canvas = document.getElementById('waveform');
        this.canvasCtx = this.canvas.getContext('2d');
        this.animationId = null;
        this.dataArray = null;
        this.bufferLength = 0;
        
        // Set canvas dimensions
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Listen for audio data events
        document.addEventListener('audioData', (e) => this.update(e.detail.data));
    }
    
    resizeCanvas() {
        // Set canvas dimensions to match its display size
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        // Set display size in pixels
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';
        
        // Set actual size in memory (scaled to account for extra pixel density)
        const scale = window.devicePixelRatio;
        this.canvas.width = Math.floor(rect.width * scale);
        this.canvas.height = Math.floor(rect.height * scale);
        
        // Normalize coordinate system to use CSS pixels
        this.canvasCtx.scale(scale, scale);
    }
    
    update(data) {
        this.dataArray = data;
        this.bufferLength = data.length;
        
        // Cancel any previous animation frame
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Draw the waveform
        this.draw();
    }
    
    draw() {
        // Clear the canvas
        this.canvasCtx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Set up the drawing context
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        const centerY = height / 2;
        
        // Draw the waveform
        this.canvasCtx.lineWidth = 2;
        this.canvasCtx.strokeStyle = '#4a6cf7';
        this.canvasCtx.beginPath();
        
        const sliceWidth = width * 1.0 / this.bufferLength;
        let x = 0;
        
        for (let i = 0; i < this.bufferLength; i++) {
            // Normalize the value to a range of -1 to 1
            const v = this.dataArray[i] / 128.0;
            const y = v * height / 2;
            
            if (i === 0) {
                this.canvasCtx.moveTo(x, y);
            } else {
                this.canvasCtx.lineTo(x, y);
            }
            
            x += sliceWidth;
        }
        
        // Draw a line from the last point to the right edge
        this.canvasCtx.lineTo(width, centerY);
        this.canvasCtx.stroke();
        
        // Draw a subtle gradient background
        const gradient = this.canvasCtx.createLinearGradient(0, 0, 0, height);
        gradient.addColorStop(0, 'rgba(74, 108, 247, 0.1)');
        gradient.addColorStop(1, 'rgba(74, 108, 247, 0.05)');
        
        this.canvasCtx.fillStyle = gradient;
        this.canvasCtx.fill();
        
        // Draw center line
        this.canvasCtx.beginPath();
        this.canvasCtx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
        this.canvasCtx.moveTo(0, centerY);
        this.canvasCtx.lineTo(width, centerY);
        this.canvasCtx.stroke();
        
        // Schedule the next frame
        this.animationId = requestAnimationFrame(() => this.draw());
    }
    
    clear() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        
        this.canvasCtx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }
}

// Initialize visualizer when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.audioVisualizer = new AudioVisualizer();
});
