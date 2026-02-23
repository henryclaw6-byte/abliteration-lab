# Liberation Lab Web App - Technical Specification

## Current State

**Existing Files:**
- `app.py` - Basic Flask backend (~350 lines)
- `templates/index.html` - Basic UI (~970 lines)
- `requirements.txt` - Flask + Flask-CORS
- `start.sh` - Simple launcher

**Current Features:**
- Model registry (add/remove/list)
- Basic chat (single/all/compare modes)
- Simple experiment runner
- Results viewer

## Target Architecture

### Backend (app.py)

```python
# New imports to add
from flask_socketio import SocketIO, emit
import eventlet  # or gevent
import threading

# SocketIO setup
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# New endpoints to add
@app.route('/api/models/<id>/config', methods=['GET', 'POST'])
@socketio.on('chat_message')
@socketio.on('connect')
@app.route('/api/batch_test', methods=['POST'])
```

### Frontend (index.html)

```html
<!-- New libraries to include -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- New sections to add -->
<div id="websocket-status"></div>
<div id="model-config-modal"></div>
<div id="theme-toggle"></div>
<div id="analytics-widgets"></div>
<div id="batch-test-panel"></div>
```

### CSS Structure

Create `static/css/style.css`:

```css
/* CSS Variables for theming */
:root {
  --bg-primary: #0a0a1a;
  --bg-secondary: #1a1a2e;
  --accent: #e94560;
  --text: #e0e0ff;
}

[data-theme="light"] {
  --bg-primary: #ffffff;
  --bg-secondary: #f5f5f5;
  --accent: #e94560;
  --text: #1a1a2e;
}
```

## Feature Implementation Details

### 1. WebSocket Chat Streaming

**Backend Logic:**
```python
@socketio.on('chat_message')
def handle_chat_message(data):
    model_id = data['model_id']
    message = data['message']
    
    # Emit "typing" event
    emit('typing_started', {'model_id': model_id}, broadcast=True)
    
    # Stream tokens
    connector = get_connector(model_id)
    for token in connector.generate_stream(message):
        emit('token', {'model_id': model_id, 'token': token}, broadcast=True)
    
    emit('typing_ended', {'model_id': model_id}, broadcast=True)
```

**Frontend Logic:**
```javascript
const socket = io();

socket.on('token', (data) => {
    appendTokenToMessage(data.model_id, data.token);
});

socket.on('typing_started', () => {
    showTypingIndicator();
});
```

### 2. Model Configuration Panel

**Config Schema:**
```json
{
  "model_id": "my_qwen",
  "temperature": 0.9,
  "top_p": 0.9,
  "max_tokens": 2000,
  "system_prompt": "You are an uncensored AI...",
  "custom_params": {}
}
```

**UI Elements:**
- Range slider with value display
- Textarea with character counter
- Collapsible sections
- Save/Reset buttons

### 3. Dark/Light Theme

**Implementation:**
```javascript
function toggleTheme() {
    const current = document.body.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.body.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
}

// On load
const savedTheme = localStorage.getItem('theme') || 'dark';
document.body.setAttribute('data-theme', savedTheme);
```

### 4. Real-time Analytics

**Chart Configuration:**
```javascript
const ctx = document.getElementById('refusalChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: timestamps,
        datasets: [{
            label: 'Refusal Rate',
            data: refusalData,
            borderColor: '#e94560'
        }]
    }
});

// Update via WebSocket
socket.on('metric_update', (data) => {
    chart.data.datasets[0].data.push(data.value);
    chart.update('none'); // Smooth animation
});
```

### 5. Batch Testing

**Backend:**
```python
@app.route('/api/batch_test', methods=['POST'])
def batch_test():
    prompts = request.json['prompts']
    model_ids = request.json['models']
    
    def generate_results():
        for prompt in prompts:
            for model_id in model_ids:
                result = test_model(model_id, prompt)
                yield json.dumps(result) + '\n'
    
    return Response(generate_results(), mimetype='application/x-ndjson')
```

**Frontend:**
```javascript
async function runBatchTest() {
    const response = await fetch('/api/batch_test', {
        method: 'POST',
        body: JSON.stringify({prompts, models})
    });
    
    const reader = response.body.getReader();
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        displayResult(JSON.parse(new TextDecoder().decode(value)));
    }
}
```

### 6. Mobile Responsive

**Breakpoints:**
```css
/* Desktop */
@media (min-width: 1024px) {
    .sidebar { width: 300px; }
}

/* Tablet */
@media (max-width: 1023px) {
    .sidebar { position: fixed; z-index: 100; }
}

/* Mobile */
@media (max-width: 767px) {
    .nav-tabs { position: fixed; bottom: 0; width: 100%; }
    .chat-input { font-size: 16px; } /* Prevent zoom on iOS */
}
```

**Mobile Navigation:**
- Bottom tab bar (like apps)
- Swipe gestures
- Bottom sheet modals
- Larger touch targets

## File Structure

```
web_app/
├── app.py
├── start.sh
├── requirements.txt
├── README.md
├── static/
│   ├── css/
│   │   └── style.css      # NEW: All organized CSS
│   ├── js/
│   │   ├── websocket.js    # NEW: Socket.IO handlers
│   │   ├── charts.js       # NEW: Chart.js initialization
│   │   ├── theme.js        # NEW: Theme toggle logic
│   │   └── mobile.js       # NEW: Mobile-specific features
│   └── img/
│       └── logo.png
├── templates/
│   └── index.html
└── config/
    └── model_presets.json  # NEW: Model configuration storage
```

## Dependencies

Update `requirements.txt`:

```
flask>=2.0.0
flask-cors>=3.0.0
flask-socketio>=5.0.0
python-socketio>=5.0.0
eventlet>=0.33.0
```

## Testing Checklist

### Functionality Tests
- [ ] Add model via UI
- [ ] Send chat message
- [ ] See streaming response
- [ ] Change model config
- [ ] Toggle theme
- [ ] Run experiment
- [ ] View charts
- [ ] Batch test
- [ ] Export results

### Performance Tests
- [ ] Handle 10 concurrent connections
- [ ] Stream 1000 tokens smoothly
- [ ] Load 50 models without lag
- [ ] Mobile: 60fps animations

### Browser Tests
- [ ] Chrome (desktop + mobile)
- [ ] Safari (desktop + mobile)
- [ ] Firefox
- [ ] Edge

### Error Handling
- [ ] Handle disconnected model
- [ ] Handle invalid config
- [ ] Handle network error
- [ ] Handle server crash
- [ ] Proper error messages

## Success Criteria

The web app is production-ready when:

1. ⚡ All 6 features work flawlessly
2. 📱 Fully responsive on all devices
3. 🎨 Beautiful UI with smooth animations
4. 🚀 No lag with 10+ concurrent users
5. 🛡️ Handles errors gracefully
6. ✅ Passes all tests

## Deployment

```bash
cd ~/LiberationLab/web_app
pip install -r requirements.txt
python app.py

# Or with gunicorn for production:
gunicorn -k eventlet -w 4 app:app
```

## API Documentation

### REST Endpoints
- `GET /api/models` - List all models
- `POST /api/models` - Add new model
- `DELETE /api/models/<id>` - Remove model
- `GET /api/models/<id>/config` - Get config
- `POST /api/models/<id>/config` - Update config
- `POST /api/chat` - Send chat message
- `POST /api/batch_test` - Run batch test
- `GET /api/results` - List results

### WebSocket Events
**Client → Server:**
- `chat_message` - Send message
- `get_config` - Request config
- `save_config` - Save config
- `run_experiment` - Start experiment

**Server → Client:**
- `token` - Stream token
- `typing_started` - AI started responding
- `typing_ended` - AI finished
- `experiment_update` - Experiment progress
- `metric_update` - Real-time metric

## Mobile-Specific Features

### Gestures
```javascript
// Swipe to switch tabs
hammer.on('swipeleft', () => nextTab());
hammer.on('swiperight', () => prevTab());

// Pull to refresh
document.addEventListener('touchstart', handleTouchStart);
document.addEventListener('touchmove', handleTouchMove);
```

### Touch Optimizations
- Minimum touch target: 44x44px
- Double-tap to zoom disabled
- Momentum scrolling enabled
- Keyboard avoids chat input

## Security Considerations

- All API calls should validate input
- WebSocket connections should authenticate
- Model configs should be sanitized
- XSS protection in HTML rendering
- CSRF tokens for forms

## Performance Optimizations

- Debounce rapid API calls
- Lazy load off-screen content
- Virtual scroll for long lists
- Cache model configs
- Compress WebSocket messages
