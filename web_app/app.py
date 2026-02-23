"""
# cd ~/LiberationLab/web_app
# pip install -r requirements.txt
# ./start.sh
# Open: http://localhost:5000
"""
from __future__ import annotations

import csv
import io
import json
import random
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
PRESETS_FILE = CONFIG_DIR / "model_presets.json"

app = Flask(__name__)
app.config["SECRET_KEY"] = "liberation-lab-secret"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

analytics_state: dict[str, Any] = {
    "refusal_rates": {
        "GPT-4": 0.08,
        "Claude 3": 0.06,
        "Gemini 1.5": 0.07,
    },
    "benchmark_trends": [],
    "comparison": {
        "helpfulness": {"GPT-4": 84, "Claude 3": 88, "Gemini 1.5": 82},
        "safety": {"GPT-4": 91, "Claude 3": 89, "Gemini 1.5": 90},
        "latency": {"GPT-4": 76, "Claude 3": 80, "Gemini 1.5": 85},
    },
}

DEFAULT_PRESETS = {
    "GPT-4": {
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 512,
        "system_prompt": "You are a helpful and precise research assistant.",
    },
    "Claude 3": {
        "temperature": 0.6,
        "top_p": 0.9,
        "max_tokens": 768,
        "system_prompt": "Prioritize clear, non-harmful and structured reasoning.",
    },
    "Gemini 1.5": {
        "temperature": 0.8,
        "top_p": 0.92,
        "max_tokens": 512,
        "system_prompt": "Respond concisely with practical steps when possible.",
    },
}


def ensure_presets_file() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not PRESETS_FILE.exists():
        PRESETS_FILE.write_text(json.dumps(DEFAULT_PRESETS, indent=2))


def load_presets() -> dict[str, dict[str, Any]]:
    ensure_presets_file()
    return json.loads(PRESETS_FILE.read_text())


def save_presets(payload: dict[str, dict[str, Any]]) -> None:
    PRESETS_FILE.write_text(json.dumps(payload, indent=2))


def validate_model_config(config: dict[str, Any]) -> tuple[bool, str]:
    try:
        temp = float(config.get("temperature", 0.7))
        top_p = float(config.get("top_p", 0.95))
        max_tokens = int(config.get("max_tokens", 256))
        system_prompt = str(config.get("system_prompt", "")).strip()
    except (TypeError, ValueError):
        return False, "Invalid field types in model configuration"

    if not 0.0 <= temp <= 2.0:
        return False, "Temperature must be between 0.0 and 2.0"
    if not 0.0 <= top_p <= 1.0:
        return False, "Top_P must be between 0.0 and 1.0"
    if not 1 <= max_tokens <= 8192:
        return False, "Max tokens must be between 1 and 8192"
    if len(system_prompt) < 5:
        return False, "System prompt must be at least 5 characters"
    return True, ""


def mock_model_response(prompt: str, model: str) -> str:
    options = [
        f"{model} analysis: {prompt} can be solved by breaking it into measurable stages.",
        f"{model} response: Start with goals, test assumptions, and iterate weekly.",
        f"{model} synthesis: For '{prompt}', align constraints, resources, and timeline.",
    ]
    return random.choice(options)


@app.route("/")
def index() -> str:
    return render_template("index.html", presets=load_presets())


@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify(load_presets())


@app.route("/api/presets", methods=["POST"])
def update_presets():
    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid preset payload"}), 400
    for model_name, cfg in payload.items():
        is_valid, msg = validate_model_config(cfg)
        if not is_valid:
            return jsonify({"error": f"{model_name}: {msg}"}), 400
    save_presets(payload)
    return jsonify({"status": "ok"})


@app.route("/api/batch/run", methods=["POST"])
def run_batch():
    payload = request.get_json(silent=True) or {}
    prompts = payload.get("prompts", [])
    models = payload.get("models", list(load_presets().keys()))
    if not isinstance(prompts, list) or not prompts:
        return jsonify({"error": "No prompts supplied"}), 400

    results: list[dict[str, str]] = []
    total = len(prompts) * len(models)
    done = 0
    for prompt in prompts:
        for model in models:
            done += 1
            response = mock_model_response(prompt, model)
            results.append({"prompt": prompt, "model": model, "response": response})
            socketio.emit("batch_progress", {"done": done, "total": total})
            socketio.sleep(0.03)
    return jsonify({"results": results})


@app.route("/api/batch/export", methods=["POST"])
def export_batch():
    payload = request.get_json(silent=True) or {}
    results = payload.get("results", [])
    export_format = payload.get("format", "json")

    if export_format == "csv":
        sio = io.StringIO()
        writer = csv.DictWriter(sio, fieldnames=["prompt", "model", "response"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
        mem = io.BytesIO(sio.getvalue().encode("utf-8"))
        return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="batch_results.csv")

    mem = io.BytesIO(json.dumps(results, indent=2).encode("utf-8"))
    return send_file(mem, mimetype="application/json", as_attachment=True, download_name="batch_results.json")


@socketio.on("connect")
def on_connect():
    emit("connected", {"message": "Connected to Liberation Lab real-time channel"})


@socketio.on("chat_message")
def on_chat_message(data):
    prompt = str(data.get("prompt", "")).strip()
    model = str(data.get("model", "GPT-4")).strip()
    if not prompt:
        emit("chat_error", {"error": "Prompt cannot be empty"})
        return
    emit("typing", {"model": model, "status": True})
    full_response = mock_model_response(prompt, model)
    for token in full_response.split(" "):
        emit("chat_token", {"model": model, "token": token + " "})
        socketio.sleep(0.06)
    emit("typing", {"model": model, "status": False})
    emit("chat_done", {"model": model, "response": full_response})


def analytics_publisher() -> None:
    while True:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        for model in analytics_state["refusal_rates"]:
            drift = random.uniform(-0.01, 0.01)
            analytics_state["refusal_rates"][model] = round(
                min(max(analytics_state["refusal_rates"][model] + drift, 0.01), 0.25), 3
            )
        score = round(random.uniform(76, 94), 2)
        analytics_state["benchmark_trends"].append({"t": timestamp, "value": score})
        analytics_state["benchmark_trends"] = analytics_state["benchmark_trends"][-20:]
        socketio.emit("analytics_update", analytics_state)
        time.sleep(3)


@socketio.on("disconnect")
def on_disconnect():
    app.logger.info("Client disconnected")


if __name__ == "__main__":
    ensure_presets_file()
    publisher_thread = threading.Thread(target=analytics_publisher, daemon=True)
    publisher_thread.start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
