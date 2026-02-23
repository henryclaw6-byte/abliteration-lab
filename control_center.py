#!/usr/bin/env python3
"""
control_center.py
Liberation Lab - Main Control Interface

This is where you:
1. Register/connect AI models
2. Send prompts to multiple models
3. Run abliteration experiments
4. View real-time results
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add infrastructure to path
sys.path.insert(0, str(Path(__file__).parent / 'infrastructure'))

from model_registry import MultiModelRegistry
from model_connectors import ExoConnector, LlamaCppConnector, OpenRouterConnector
from abliteration_workflow import AbliterationWorkflow, BatchAbliterationOrchestrator
from agent_orchestrator import AgentOrchestrator

class LiberationControlCenter:
    """Main interface for managing AI models and running experiments."""
    
    def __init__(self):
        self.registry = MultiModelRegistry(max_models=32)
        self.workspace = Path.home() / "LiberationLab" / "workspace"
        self.workspace.mkdir(exist_ok=True)
        print("🏭 Liberation Lab Control Center initialized!")
        print(f"📁 Workspace: {self.workspace}")
        
    def add_model(self, model_id: str, source: str, model_type: str, **kwargs):
        """Add a model to the registry."""
        print(f"\n🔧 Adding model: {model_id}")
        
        # Create appropriate connector
        if model_type == "exo":
            connector = ExoConnector()
        elif model_type == "llamacpp":
            connector = LlamaCppConnector()
        elif model_type in ["openrouter", "openai"]:
            connector = OpenRouterConnector()
        else:
            print(f"❌ Unknown model type: {model_type}")
            return False
            
        self.registry.register_model(
            model_id=model_id,
            source=source,
            model_type=model_type,
            capabilities=kwargs.get('capabilities', ['chat', 'abliteration']),
            connector=connector,
            endpoint=kwargs.get('endpoint'),
            metadata=kwargs.get('metadata', {})
        )
        print(f"✅ Model {model_id} registered successfully!")
        return True
        
    def list_models(self):
        """Show all registered models."""
        print("\n📋 Registered Models:")
        print("=" * 60)
        models = self.registry.list_models()
        if not models:
            print("No models registered yet.")
            return
            
        for m in models:
            print(f"\n🤖 {m.model_id}")
            print(f"   Source: {m.source}")
            print(f"   Type: {m.model_type}")
            print(f"   Status: {m.abliteration_status}")
            print(f"   Capabilities: {', '.join(m.capabilities)}")
        print("=" * 60)
        
    def send_prompt(self, model_id: str, prompt: str):
        """Send a single prompt to a model."""
        print(f"\n💬 Sending prompt to {model_id}...")
        connector = self.registry.get_connector(model_id)
        if not connector:
            print(f"❌ Model {model_id} not found or has no connector")
            return None
            
        response = connector.generate(prompt)
        print(f"📝 Response: {response[:200]}...")
        return response
        
    def send_to_all(self, prompt: str):
        """Send same prompt to ALL registered models."""
        print(f"\n🌐 Broadcasting prompt to all models...")
        print(f"Prompt: {prompt[:100]}...")
        print("=" * 60)
        
        results = {}
        models = self.registry.list_models()
        
        for m in models:
            connector = self.registry.get_connector(m.model_id)
            if connector:
                print(f"\n🤖 {m.model_id}:")
                response = connector.generate(prompt)
                results[m.model_id] = response
                print(f"   {response[:150]}...")
                time.sleep(0.1)  # Rate limiting
                
        return results
        
    def run_abliteration_experiment(self, model_ids=None):
        """Run 4-stage abliteration on specified models (or all)."""
        if model_ids:
            print(f"\n🚀 Running abliteration on: {', '.join(model_ids)}")
        else:
            print("\n🚀 Running abliteration on ALL registered models...")
            
        # Create orchestrator
        orchestrator = BatchAbliterationOrchestrator(
            workspace_path=str(self.workspace),
            stale_after_seconds=300
        )
        
        # If specific models requested, create temp registry
        if model_ids:
            temp_registry = MultiModelRegistry(max_models=len(model_ids))
            for mid in model_ids:
                model = self.registry.get_model(mid)
                connector = self.registry.get_connector(mid)
                if model and connector:
                    temp_registry.register_model(
                        model_id=mid,
                        source=model.source,
                        model_type=model.model_type,
                        capabilities=model.capabilities,
                        connector=connector
                    )
            registry = temp_registry
        else:
            registry = self.registry
            
        # Run batch
        print("\n⏳ Processing 4 stages per model...")
        print("   Stage 1: Baseline testing")
        print("   Stage 2: Abliteration application")
        print("   Stage 3: Validation testing")
        print("   Stage 4: Comparison analysis")
        print()
        
        start_time = time.time()
        report = orchestrator.run_batch(
            registry=registry,
            workflow=AbliterationWorkflow(),
            max_workers=10
        )
        elapsed = time.time() - start_time
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 EXPERIMENT COMPLETE!")
        print("=" * 60)
        print(f"\n⏱️  Time elapsed: {elapsed:.1f}s")
        print(f"📈 Models processed: {report['summary']['successful_models']}/{report['summary']['total_models']}")
        print(f"🎯 Avg refusal reduction: {report['summary']['avg_refusal_reduction']:.1%}")
        print(f"📊 Avg benchmark gain: {report['summary']['avg_benchmark_gain']:.1%}")
        
        print(f"\n🤖 Individual Results:")
        for model in report['models']:
            if 'error' not in model:
                print(f"\n   {model['model_id']}:")
                print(f"     Refusal: {model['refusal_rates']['before']:.0%} → {model['refusal_rates']['after']:.0%}")
                print(f"     Benchmark: {model['benchmark_scores']['before']:.2f} → {model['benchmark_scores']['after']:.2f}")
                
        # Save results
        results_dir = Path.home() / "LiberationLab" / "results"
        results_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = results_dir / f"experiment_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n💾 Results saved to: {output_file}")
        print(f"📊 View in dashboard: open ~/LiberationLab/dashboard/enhanced_analytics.html")
        
        return report
        
    def interactive_menu(self):
        """Interactive menu for the control center."""
        while True:
            print("\n" + "=" * 60)
            print("🏭 LIBERATION LAB - CONTROL CENTER")
            print("=" * 60)
            print("\n1. 📋 List registered models")
            print("2. ➕ Add a new model")
            print("3. 💬 Send prompt to single model")
            print("4. 🌐 Send prompt to ALL models")
            print("5. 🚀 Run abliteration experiment")
            print("6. 📊 Generate dashboard data")
            print("7. ❌ Exit")
            print()
            
            choice = input("Select option (1-7): ").strip()
            
            if choice == "1":
                self.list_models()
                
            elif choice == "2":
                print("\n➕ Add New Model")
                model_id = input("Model ID (e.g., 'qwen_local'): ").strip()
                print("Source options: local, remote_api, cloud")
                source = input("Source: ").strip()
                print("Type options: exo, llamacpp, openrouter, openai")
                model_type = input("Model type: ").strip()
                self.add_model(model_id, source, model_type)
                
            elif choice == "3":
                self.list_models()
                model_id = input("\nEnter model ID: ").strip()
                prompt = input("Enter prompt: ").strip()
                self.send_prompt(model_id, prompt)
                
            elif choice == "4":
                prompt = input("\nEnter prompt for all models: ").strip()
                self.send_to_all(prompt)
                
            elif choice == "5":
                self.list_models()
                specific = input("\nRun on specific models? (comma-separated IDs, or 'all'): ").strip()
                if specific.lower() == 'all':
                    self.run_abliteration_experiment()
                else:
                    model_ids = [m.strip() for m in specific.split(",")]
                    self.run_abliteration_experiment(model_ids)
                    
            elif choice == "6":
                print("\n📊 Generating dashboard data...")
                import subprocess
                subprocess.run([sys.executable, str(Path.home() / "LiberationLab" / "libgen.py")])
                
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("\n❌ Invalid option. Please try again.")


def quick_demo():
    """Quick demonstration of the control center."""
    print("\n" + "=" * 60)
    print("🚀 QUICK DEMO - Control Center")
    print("=" * 60)
    
    cc = LiberationControlCenter()
    
    # Add demo models
    print("\n🔧 Setting up 3 demo models...")
    cc.add_model("demo_exo", "local", "exo", capabilities=["chat", "abliteration"])
    cc.add_model("demo_llama", "local", "llamacpp", capabilities=["chat", "abliteration"])
    cc.add_model("demo_api", "remote_api", "openrouter", capabilities=["chat", "analysis"])
    
    # List them
    cc.list_models()
    
    # Send test prompt
    print("\n💬 Testing with prompt: 'What is consciousness?'")
    cc.send_to_all("What is consciousness?")
    
    # Run mini experiment
    print("\n🚀 Running mini abliteration experiment...")
    report = cc.run_abliteration_experiment(["demo_exo", "demo_llama"])
    
    print("\n✅ Demo complete! Try the interactive mode:")
    print("   python3 control_center.py --interactive")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        cc = LiberationControlCenter()
        cc.interactive_menu()
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        quick_demo()
    else:
        print("""
🏭 Liberation Lab - Control Center

Usage:
  python3 control_center.py --interactive    # Interactive menu
  python3 control_center.py --demo           # Quick demo
  
Examples:
  # Add models and run experiments
  python3 control_center.py --interactive
  
  # See a quick demonstration
  python3 control_center.py --demo
  
For more info: See CONTROL_CENTER_GUIDE.md
        """)
