// Main application script
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const audioRecorder = window.audioRecorder;
    const audioVisualizer = window.audioVisualizer;
    
    // Cache DOM elements
    const resultsSection = document.getElementById('resultsSection');
    const mainEmotion = document.getElementById('mainEmotion');
    const emotionBars = document.getElementById('emotionBars');
    const suggestionText = document.getElementById('suggestionText');
    const historyList = document.getElementById('historyList');
    
    // Emotion to emoji mapping
    const emotionEmojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'neutral': '😐',
        'excited': '🤩',
        'frustrated': '😤',
        'anxious': '😰',
        'calm': '😌'
    };
    
    // Suggestions based on emotion
    const emotionSuggestions = {
        'happy': 'Your child seems happy and engaged. This is a great time for learning and social interaction!',
        'sad': 'Your child seems sad. Try to provide comfort and engage in a calming activity they enjoy.',
        'angry': 'Your child seems frustrated or angry. Try to identify the trigger and provide a quiet space to calm down.',
        'neutral': 'Your child seems neutral. This is a good time to introduce new activities or learning opportunities.',
        'excited': 'Your child is very excited! Channel this energy into a productive activity.',
        'frustrated': 'Your child seems frustrated. Break down tasks into smaller steps and provide positive reinforcement.',
        'anxious': 'Your child seems anxious. Create a calm environment and use soothing techniques.',
        'calm': 'Your child is calm and focused. This is an excellent time for learning new skills.'
    };
    
    // Handle recording complete event
    document.addEventListener('recordingComplete', (e) => {
        console.log('Recording complete:', e.detail.audioUrl);
        // The analyze button is already enabled by the recorder
    });
    
    // Handle analysis complete event
    document.addEventListener('analysisComplete', (e) => {
        const result = e.detail;
        console.log('Analysis complete:', result);
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Update main emotion
        const mainEmoji = emotionEmojis[result.predicted_emotion] || '❓';
        mainEmotion.innerHTML = `
            <div class="emotion-icon">${mainEmoji}</div>
            <div class="emotion-text">
                <span class="emotion-label">${capitalizeFirstLetter(result.predicted_emotion)}</span>
                <span class="confidence">${Math.round(result.confidence * 100)}% confidence</span>
            </div>
        `;
        
        // Update emotion bars
        updateEmotionBars(result.all_predictions);
        
        // Update suggestion
        suggestionText.textContent = emotionSuggestions[result.predicted_emotion] || 
                                   'Observe your child\'s behavior and adjust activities accordingly.';
        
        // Add to history
        addToHistory(result);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    });
    
    // Update emotion bars visualization
    function updateEmotionBars(predictions) {
        emotionBars.innerHTML = '';
        
        // Sort predictions by confidence (highest first)
        const sortedPredictions = [...predictions].sort((a, b) => b.confidence - a.confidence);
        
        // Create a bar for each emotion
        sortedPredictions.forEach(prediction => {
            const percentage = Math.round(prediction.confidence * 100);
            const emoji = emotionEmojis[prediction.emotion] || '❓';
            
            const barContainer = document.createElement('div');
            barContainer.className = 'emotion-bar';
            barContainer.innerHTML = `
                <div class="emotion-label-small">${emoji} ${capitalizeFirstLetter(prediction.emotion)}</div>
                <div class="bar-container">
                    <div class="bar" style="width: ${percentage}%;"></div>
                </div>
                <div class="percentage">${percentage}%</div>
            `;
            
            emotionBars.appendChild(barContainer);
            
            // Animate the bar
            setTimeout(() => {
                const bar = barContainer.querySelector('.bar');
                bar.style.width = '0%';
                // Force reflow to restart animation
                void bar.offsetWidth;
                bar.style.width = percentage + '%';
            }, 100);
        });
    }
    
    // Add analysis result to history
    function addToHistory(result) {
        // Create history item
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';
        
        const emoji = emotionEmojis[result.predicted_emotion] || '❓';
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const dateString = now.toLocaleDateString();
        
        historyItem.innerHTML = `
            <div class="history-emotion">
                <div class="history-emoji">${emoji}</div>
                <div class="history-details">
                    <div class="emotion-name">${capitalizeFirstLetter(result.predicted_emotion)}</div>
                    <div class="history-date">${dateString} at ${timeString}</div>
                </div>
            </div>
            <div class="history-confidence">${Math.round(result.confidence * 100)}%</div>
        `;
        
        // Add to the top of the history list
        const noHistory = historyList.querySelector('.no-history');
        if (noHistory) {
            noHistory.remove();
        }
        
        historyList.insertBefore(historyItem, historyList.firstChild);
        
        // Limit history items
        if (historyList.children.length > 10) {
            historyList.removeChild(historyList.lastChild);
        }
    }
    
    // Helper function to capitalize first letter
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
