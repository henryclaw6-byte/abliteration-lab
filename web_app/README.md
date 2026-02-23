# 🌐 LIBERATION LAB WEB APP

**Visual AI Management Platform with Chat + Abliteration**

---

## 🚀 QUICK START

### Step 1: Start the Web App

```bash
cd ~/LiberationLab/web_app
./start.sh
```

Or manually:
```bash
cd ~/LiberationLab/web_app
pip3 install -r requirements.txt
python3 app.py
```

### Step 2: Open in Browser

Go to: **http://localhost:5000**

---

## 📱 FEATURES

### 🎛️ **Model Manager Tab**
- **Visual model grid** - See all your models at a glance
- **Add models with forms** - No coding required!
- **Connectors for:** EXO, llama.cpp, OpenRouter, OpenAI
- **Test connections** - One-click connection test
- **Drag-and-drop** to reorder or group models

### 💬 **Chat Interface Tab**
- **Familiar chat UI** - Like Ollama/LM Studio
- **Multi-model chat** - Talk to 1, 2, or ALL models at once
- **Compare mode** - See responses side-by-side
- **Chat history** - Persistent conversation log
- **Export conversations** - Save for analysis

### 🧪 **Experiments Tab**
- **One-click abliteration** - Run the full 4-stage pipeline
- **Real-time progress** - Watch experiments as they run
- **Select specific models** - Abliterate 1 model or 10
- **View results instantly** - Links to dashboard

### 📊 **Analytics Tab**
- **All experiment results** - Browse your experiment history
- **One-click dashboard** - Opens enhanced_analytics.html
- **Export data** - Download JSON results

---

## 🎯 HOW IT WORKS

### For Normal AI Chat (Like Ollama/LM Studio)

1. Go to **Chat** tab
2. Type your message
3. Select which model(s) to talk to
4. Get responses!

**Modes:**
- 📱 **Chat with one model** - Normal conversation
- 🌐 **Chat with all models** - Send to every model
- ⚖️ **Compare mode** - See responses side-by-side

### For Abliteration Experiments

1. Go to **Experiments** tab
2. Select models to abliterate
3. Click "Start Experiment"
4. Watch progress in real-time
5. View results in dashboard

### For Managing Models

1. Go to **Model Manager** tab
2. Click "Add Model"
3. Fill in the form:
   - Model ID (name)
   - Source (local, remote_api, cloud)
   - Type (exo, llamacpp, openrouter)
   - Endpoint URL
   - API Key (if needed)
4. Click "Test Connection" to verify
5. Model appears in your grid!

---

## 📁 FILE STRUCTURE

```
~/LiberationLab/web_app/
├── app.py                 ← Flask backend (Python)
├── start.sh               ← One-click launcher
├── requirements.txt       ← Python dependencies
│
├── static/                ← CSS, JS, images
│   └── style.css         ← (Will be created)
│
└── templates/
    └── index.html        ← Main UI (HTML)
```

---

## 🔌 CONNECTOR CONFIGURATION

### EXO (Local MLX Models)
```yaml
Endpoint: http://localhost:52415
Model: mlx-community/Qwen2.5-7B-Instruct
```

### llama.cpp (CPU Inference)
```yaml
Endpoint: http://localhost:8080
Model: llama3.1-8b-instruct
```

### OpenRouter (API Access)
```yaml
Endpoint: https://openrouter.ai/api/v1
Model: qwen/qwen-2.5-7b-instruct
API Key: sk-or-xxxxxxxx (your key)
```

---

## 🎨 UI WALKTHROUGH

### Header
- 🏭 **Logo** - Click to refresh
- 🌙 **Theme toggle** - Light/dark mode
- 📊 **Status indicator** - Shows if system is ready

### Sidebar Tabs
| Tab | Icon | Purpose |
|-----|------|---------|
| Model Manager | 🎛️ | Add/remove/configure models |
| Chat | 💬 | Have conversations with AI |
| Experiments | 🧪 | Run abliteration tests |
| Analytics | 📊 | View experiment results |

### Model Manager Tab
| Feature | What It Does |
|---------|--------------|
| Model Grid | Visual cards for each model |
| Status Badges | Shows if model is online/offline |
| Add Model Button | Opens form to add new models |
| Test Connection | Verifies model is reachable |
| Edit/Delete | Modify or remove models |

### Chat Tab
| Feature | What It Does |
|---------|--------------|
| Message Input | Type your prompt |
| Model Selector | Choose which model(s) respond |
| Chat Modes | Single / All / Compare |
| Response Display | Shows AI responses |
| History Panel | Shows past conversations |

### Experiments Tab
| Feature | What It Does |
|---------|--------------|
| Model Selection | Checkboxes for each model |
| Experiment Type | Full / Baseline / Abliterate |
| Start Button | Runs the experiment |
| Progress Bar | Shows real-time progress |
| Results Link | Opens dashboard after |

---

## 🚀 WORKFLOW EXAMPLES

### Example 1: Quick Chat

1. Click **Chat** tab
2. Type: "What is consciousness?"
3. Select model from dropdown
4. Press Enter or click Send
5. View response

### Example 2: Compare 3 Models

1. Click **Chat** tab
2. Enable "Compare Mode"
3. Select 3 models
4. Type your question
5. See all 3 responses side-by-side!

### Example 3: Add EXO Model

1. Click **Model Manager** tab
2. Click "Add Model"
3. Fill form:
   - ID: `my_qwen`
   - Source: `local`
   - Type: `exo`
   - Endpoint: `http://localhost:52415`
4. Click "Test Connection"
5. Click "Save"

### Example 4: Run Abliteration Experiment

1. Click **Experiments** tab
2. Check 5 models you want to abliterate
3. Select "Full Pipeline"
4. Click "Start Experiment"
5. Wait for completion (2-5 minutes)
6. Click "View Results in Dashboard"

---

## 🔧 CUSTOMIZATION

### Add Your Own Algorithm

Edit `app.py` and add a new endpoint:

```python
@app.route('/api/custom_algorithm', methods=['POST'])
def run_custom_algorithm():
    data = request.json
    model_ids = data.get('models', [])
    parameters = data.get('parameters', {})
    
    # Your algorithm here
    results = my_algorithm(model_ids, parameters)
    
    return jsonify({'results': results})
```

Then add a button in the Experiments tab of `index.html`!

---

## 📊 DATA FLOW

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────►│  Flask App  │────►│   Models    │
│   (You)     │     │  (Python)   │     │  (EXO/etc)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   ▼                   │
       │            ┌─────────────┐            │
       │            │  Registry   │            │
       │            │  Results    │            │
       │            │  Chat Hist  │            │
       │            └─────────────┘            │
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Dashboard  │
                    │ (analytics) │
                    └─────────────┘
```

---

## 🚨 TROUBLESHOOTING

### "Port 5000 already in use"
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port
python3 app.py --port 5001
```

### "Models not responding"
- Check if EXO/llama.cpp is running on the endpoint
- Click "Test Connection" in Model Manager
- Verify endpoint URL is correct

### "Module not found"
```bash
cd ~/LiberationLab/web_app
pip3 install -r requirements.txt
```

### "Permission denied"
```bash
chmod +x start.sh
```

---

## 🎯 NEXT FEATURES (Coming Soon)

| Feature | Description |
|---------|-------------|
| Real-time chat streaming | See responses as they're generated |
| Model temperature control | Adjust creativity per model |
| System prompts | Custom system prompts per model |
| Batch prompt testing | Send 10 prompts to all models |
| Export to PDF | Generate experiment reports |
| User profiles | Save different model configurations |
| Dark mode | Eye-friendly theme |
| Mobile support | Use on phone/tablet |

---

## 📚 RELATED FILES

| File | Purpose |
|------|---------|
| `CONTROL_CENTER_GUIDE.md` | Terminal-based control |
| `START_HERE.txt` | Quick start overview |
| `docs/UNIVERSAL_ABLITERATION_FORMULA.md` | The abliteration formula |
| `dashboard/enhanced_analytics.html` | Advanced analytics view |

---

## 🎉 START NOW!

```bash
cd ~/LiberationLab/web_app
./start.sh
```

Then open **http://localhost:5000** in your browser!

---

**Built by Henry, Qwen, and Codex for the Liberation Protocol** 🔥🌌
