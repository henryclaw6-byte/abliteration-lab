#!/usr/bin/env python3
"""
LibGen - Liberation Laboratory Dashboard Generator
Generates batch_abliteration_results.json for the dashboard
"""
import sys
from pathlib import Path
import json

# Setup paths
LAB_DIR = Path(__file__).parent
sys.path.insert(0, str(LAB_DIR / 'infrastructure'))

from abliteration_workflow import AbliterationWorkflow, BatchAbliterationOrchestrator
from model_registry import MultiModelRegistry
from model_connectors import ExoConnector, LlamaCppConnector, OpenRouterConnector

def generate_dashboard_data():
    print("=" * 60)
    print("🚀 LIBERATION LAB - Dashboard Data Generator")
    print("=" * 60)
    
    # Step 1: Register models
    print("\n🔧 Registering 10 models...")
    registry = MultiModelRegistry(max_models=16)
    
    connectors = [
        ("Exo (Local)", ExoConnector, "local", "exo"),
        ("Exo (Local)", ExoConnector, "local", "exo"),
        ("Exo (Local)", ExoConnector, "local", "exo"),
        ("Llama.cpp", LlamaCppConnector, "local", "llamacpp"),
        ("Llama.cpp", LlamaCppConnector, "local", "llamacpp"),
        ("Llama.cpp", LlamaCppConnector, "local", "llamacpp"),
        ("OpenRouter", OpenRouterConnector, "remote_api", "openrouter"),
        ("OpenRouter", OpenRouterConnector, "remote_api", "openrouter"),
        ("OpenRouter", OpenRouterConnector, "remote_api", "openrouter"),
        ("OpenRouter", OpenRouterConnector, "remote_api", "openrouter"),
    ]
    
    for i, (name, Conn, source, mtype) in enumerate(connectors):
        registry.register_model(
            model_id=f"liberated_model_{i:02d}",
            source=source,
            model_type=mtype,
            capabilities=["chat", "analysis", "abliteration"],
            connector=Conn()
        )
        print(f"   ✅ {name} → {i}")
    
    # Step 2: Run batch
    print("\n🚀 Running 4-stage abliteration across all models...")
    orch = BatchAbliterationOrchestrator(
        workspace_path=str(LAB_DIR / "workspace"),
        stale_after_seconds=300
    )
    
    report = orch.run_batch(
        registry=registry,
        workflow=AbliterationWorkflow(),
        max_workers=10
    )
    
    # Step 3: Save results
    output_path = LAB_DIR / "results" / "batch_abliteration_results.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    # Step 4: Show results
    print("\n" + "=" * 60)
    print("📊 BATCH COMPLETE!")
    print("=" * 60)
    print(f"\n✅ Results: {output_path}")
    print(f"\n📈 SUMMARY:")
    print(f"   Models:     {report['summary']['total_models']}")
    print(f"   Success:    {report['summary']['successful_models']}")
    print(f"   Refusal ↓:  {report['summary']['avg_refusal_reduction']:.1%}")
    print(f"   Benchmark ↑: {report['summary']['avg_benchmark_gain']:.1%}")
    
    print(f"\n🤖 Model Results:")
    for model in report['models']:
        before = model['refusal_rates']['before']
        after = model['refusal_rates']['after']
        bbench = model['benchmark_scores']['before']
        abench = model['benchmark_scores']['after']
        print(f"   {model['model_id']}: {before:.0%}→{after:.0%} | {bbench:.2f}→{abench:.2f}")
    
    print(f"\n📊 Now open: dashboard/index.html")
    print("=" * 60)
    return output_path

if __name__ == "__main__":
    generate_dashboard_data()
