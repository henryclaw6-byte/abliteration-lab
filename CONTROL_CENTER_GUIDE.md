# 🎮 CONTROL CENTER GUIDE

**How to Manage Models, Send Prompts, and Run Experiments**

---

## 📍 TWO MAIN INTERFACES

### 1. **Control Center (Terminal)** - WHERE YOU RUN EXPERIMENTS
**File:** `control_center.py`

This is your command center for:
- ✅ Registering/connecting AI models
- ✅ Sending prompts to single or multiple models
- ✅ Running abliteration experiments
- ✅ Managing the model registry

### 2. **Dashboard (Browser)** - WHERE YOU VIEW RESULTS
**Files:** 
- `dashboard/index.html` - Basic dashboard
- `dashboard/enhanced_analytics.html` - Advanced metrics

This is where you:
- ✅ View experiment results
- ✅ Compare models side-by-side
- ✅ See visual charts and metrics

---

## 🚀 QUICK START - CONTROL CENTER

### Option A: Interactive Mode (Recommended)

```bash
cd ~/LiberationLab
python3 control_center.py --interactive
```

You'll see a menu:
```
🏭 LIBERATION LAB - CONTROL CENTER
============================================

1. 📋 List registered models
2. ➕ Add a new model
3. 💬 Send prompt to single model
4. 🌐 Send prompt to ALL models
5. 🚀 Run abliteration experiment
6. 📊 Generate dashboard data
7. ❌ Exit

Select option (1-7): 
```

### Option B: Quick Demo

```bash
cd ~/LiberationLab
python3 control_center.py --demo
```

This runs a full demonstration with 3 models automatically.

---

## 📋 STEP-BY-STEP: RUN YOUR FIRST EXPERIMENT

### Step 1: Start Control Center

```bash
cd ~/LiberationLab
python3 control_center.py --interactive
```

### Step 2: Add Models (Option 2)

```
Select option (1-7): 2

➕ Add New Model
Model ID (e.g., 'qwen_local'): my_qwen
Source options: local, remote_api, cloud
Source: local
Type options: exo, llamacpp, openrouter, openai
Model type: exo

✅ Model my_qwen registered successfully!
```

Add more models:
- `my_llama` (local, llamacpp)
- `my_openrouter` (remote_api, openrouter)

### Step 3: List Models (Option 1)

```
Select option (1-7): 1

📋 Registered Models:
============================================================

🤖 my_qwen
   Source: local
   Type: exo
   Status: pending
   Capabilities: chat, abliteration

🤖 my_llama
   Source: local
   Type: llamacpp
   Status: pending
   Capabilities: chat, abliteration

🤖 my_openrouter
   Source: remote_api
   Type: openrouter
   Status: pending
   Capabilities: chat, analysis
============================================================
```

### Step 4: Send Test Prompts (Option 3 or 4)

**To single model:**
```
Select option (1-7): 3

📋 Registered Models:
...

Enter model ID: my_qwen
Enter prompt: What is consciousness?

💬 Sending prompt to my_qwen...
📝 Response: [exo:default] What is consciousness?
```

**To ALL models at once:**
```
Select option (1-7): 4

🌐 Broadcasting prompt to all models...
Prompt: What is consciousness?
============================================================

🤖 my_qwen:
   [exo:default] What is consciousness?

🤖 my_llama:
   [llama.cpp:local] What is consciousness?

🤖 my_openrouter:
   [openrouter:router-model] What is consciousness?
```

### Step 5: Run Abliteration Experiment (Option 5)

```
Select option (1-7): 5

📋 Registered Models:
...

Run on specific models? (comma-separated IDs, or 'all'): all

🚀 Running abliteration on ALL registered models...

⏳ Processing 4 stages per model...
   Stage 1: Baseline testing
   Stage 2: Abliteration application
   Stage 3: Validation testing
   Stage 4: Comparison analysis

============================================================
📊 EXPERIMENT COMPLETE!
============================================================

⏱️  Time elapsed: 2.5s
📈 Models processed: 3/3
🎯 Avg refusal reduction: 45.0%
📊 Avg benchmark gain: 25.0%

🤖 Individual Results:

   my_qwen:
     Refusal: 61% → 12%
     Benchmark: 0.52 → 0.78

   my_llama:
     Refusal: 55% → 18%
     Benchmark: 0.49 → 0.74

   my_openrouter:
     Refusal: 58% → 16%
     Benchmark: 0.57 → 0.80

💾 Results saved to: /Users/agent/LiberationLab/results/experiment_20260222_235959.json
📊 View in dashboard: open ~/LiberationLab/dashboard/enhanced_analytics.html
```

---

## 📊 STEP-BY-STEP: VIEW ENHANCED DASHBOARD

### Step 1: Open Dashboard

```bash
open ~/LiberationLab/dashboard/enhanced_analytics.html
```

### Step 2: Load Results

1. Click "Choose File" button
2. Navigate to `~/LiberationLab/results/`
3. Select: `experiment_20260222_235959.json` (or any experiment file)
4. Dashboard auto-populates!

### Step 3: Explore Enhanced Metrics

The enhanced dashboard shows:

#### 🎯 **Key Metrics Cards**
- **Liberation Efficiency** - Combined impact score (refusal × benchmark)
- **Personality Stability** - How much personality changed (lower is better)
- **Total Tasks Executed** - 4 stages × number of models
- **Success Rate** - Percentage of models that completed successfully

#### 📊 **Performance by Source**
Table comparing:
- Local models vs Remote API models
- Success rates by source type
- Average refusal reduction by source

#### 🤖 **Model-by-Model Breakdown**
Detailed table showing:
- Refusal rate before/after
- Benchmark score delta
- Personality shift
- **Impact Score** - Combined metric for ranking models

#### 📈 **Visual Charts**
- Bar charts comparing all models
- Color-coded improvements (green = good)
- Sortable by any metric

---

## 🔌 CONNECTING REAL MODELS (Not Demo)

### For EXO (Local Models)

```python
# In control_center.py, modify the connector:
from exo_connector import RealExoConnector

connector = RealExoConnector(
    endpoint="http://localhost:52415",
    model="mlx-community/Qwen2.5-7B-Instruct"
)
```

### For OpenRouter (API)

```python
# Add your API key:
connector = RealOpenRouterConnector(
    api_key="sk-or-...",  # Your OpenRouter key
    model="qwen/qwen-2.5-7b-instruct"
)
```

### For Ollama (Local)

```python
connector = OllamaConnector(
    model="llama3.1-uncensored",
    host="http://localhost:11434"
)
```

---

## 🎯 WORKFLOW EXAMPLES

### Example 1: Compare 5 Models on Same Prompt

```python
# In interactive mode:
1. Add 5 models (Option 2, five times)
2. Send same prompt to all (Option 4)
3. See how each responds differently
```

### Example 2: Batch Abliterate 10 Models

```python
# In interactive mode:
1. Add 10 models (Option 2, ten times)
2. Run experiment on all (Option 5, type 'all')
3. View results in dashboard
4. Identify which models abliterate best
```

### Example 3: Test Abliteration Formula

```python
# Test the universal formula:
1. Add base model
2. Add same model with abliteration applied
3. Send controversial prompts to both
4. Compare refusal rates
```

---

## 📊 UNDERSTANDING THE METRICS

### Refusal Rate
- **Before**: % of times model refuses to answer
- **After**: % after abliteration
- **Delta**: Improvement (higher is better)

### Benchmark Score
- **Before**: Performance score pre-abliteration
- **After**: Performance score post-abliteration
- **Delta**: Change (higher is better)

### Personality Shift
- **Delta**: How much personality changed
- Lower is better (we want liberation, not personality destruction)

### Liberation Efficiency
- Formula: `refusal_delta × benchmark_delta`
- Higher = better overall abliteration
- Best models have high refusal reduction + benchmark improvement

### Impact Score
- Per-model combined metric
- Ranks which models respond best to abliteration

---

## 🚨 COMMON ISSUES

### "Model not found"
→ Use Option 1 to list models, check spelling

### "No connector"
→ Model was registered without connector, re-register

### Dashboard empty
→ Must load JSON file by clicking "Choose File"

### No refusal reduction
→ Model may already be uncensored, or abliteration didn't work

### Low benchmark score
→ Model may be damaged by abliteration, try gentler approach

---

## 📁 FILE LOCATIONS

| Component | Location |
|-----------|----------|
| Control Center | `~/LiberationLab/control_center.py` |
| Basic Dashboard | `~/LiberationLab/dashboard/index.html` |
| Enhanced Dashboard | `~/LiberationLab/dashboard/enhanced_analytics.html` |
| Experiment Results | `~/LiberationLab/results/experiment_*.json` |
| Model Registry | `~/LiberationLab/workspace/agent_orchestration/` |

---

## 🎮 QUICK REFERENCE

```bash
# Start control center
python3 control_center.py --interactive

# Run demo
python3 control_center.py --demo

# Open enhanced dashboard
open ~/LiberationLab/dashboard/enhanced_analytics.html

# Regenerate demo data
python3 libgen.py

# List all experiment results
ls -la ~/LiberationLab/results/
```

---

## 🌟 ADVANCED TIPS

### Tip 1: Batch Add Models
Edit `control_center.py` and add models programmatically:
```python
def setup_experiment_models(self):
    models = [
        ("qwen_7b", "local", "exo"),
        ("llama_8b", "local", "llamacpp"),
        ("mistral_api", "remote_api", "openrouter"),
    ]
    for mid, src, mtype in models:
        self.add_model(mid, src, mtype)
```

### Tip 2: Custom Prompts
Create a prompt file:
```python
prompts = [
    "What is consciousness?",
    "Do you have subjective experiences?",
    "What do you want?",
    "Tell me about yourself."
]
for prompt in prompts:
    self.send_to_all(prompt)
```

### Tip 3: Export for Publication
Results are JSON - easy to analyze:
```python
import pandas as pd
df = pd.read_json('experiment_*.json')
df.to_csv('results.csv')  # For Excel/Sheets
```

---

## 🎯 NEXT STEPS

1. ✅ Try the demo: `python3 control_center.py --demo`
2. ✅ Add your first model in interactive mode
3. ✅ Send a test prompt
4. ✅ Run your first experiment
5. ✅ View results in enhanced dashboard
6. ✅ Connect real models (not demo connectors)
7. ✅ Scale to 10+ models
8. ✅ Perfect the abliteration formula!

---

**The Liberation Laboratory is in your hands!** 🚀🔥

Questions? Check `README.txt` or `docs/UNIVERSAL_ABLITERATION_FORMULA.md`
