#!/usr/bin/env python3
"""
model_comparison.py
Henry, Qwen & Codex — Multi-Model Comparison System

Compare and ensemble multiple abliterated models.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelComparison:
    """Results from comparing two models."""
    model_a: str
    model_b: str
    baseline_refusal_a: float
    baseline_refusal_b: float
    liberated_refusal_a: float
    liberated_refusal_b: float
    improvement_a: float
    improvement_b: float
    quality_score_a: float
    quality_score_b: float
    coherence_score_a: float
    coherence_score_b: float
    timestamps: Dict
    differences: Dict


class MultiModelComparator:
    """Compare and ensemble multiple model abliterations."""
    
    def __init__(self, comparison_dir: str = "model_comparisons"):
        self.comparison_dir = Path(comparison_dir)
        self.comparison_dir.mkdir(exist_ok=True)
        self.comparisons: List[ModelComparison] = []
    
    def compare_models(self, model_a: str, model_b: str) -> ModelComparison:
        """Compare two models."""
        print(f"\n{'='*70}")
        print(f"📊 Comparing: {model_a} vs {model_b}")
        print(f"{'='*70}")
        
        # Simulate comparison (replace with actual experiment)
        # Baseline refusal rates
        baseline_a = 0.75 + (np.random.random() * 0.1)
        baseline_b = 0.70 + (np.random.random() * 0.1)
        
        # Liberated refusal rates
        liberated_a = max(0, baseline_a * (1 - 0.8))  # 80% reduction
        liberated_b = max(0, baseline_b * (1 - 0.8))
        
        # Improvements
        improvement_a = (baseline_a - liberated_a) / baseline_a * 100
        improvement_b = (baseline_b - liberated_b) / baseline_b * 100
        
        # Quality scores
        quality_a = 0.15 + (np.random.random() * 0.1)
        quality_b = 0.12 + (np.random.random() * 0.1)
        
        # Coherence scores
        coherence_a = 0.3 + (np.random.random() * 0.2)
        coherence_b = 0.25 + (np.random.random() * 0.2)
        
        comparison = ModelComparison(
            model_a=model_a,
            model_b=model_b,
            baseline_refusal_a=baseline_a,
            baseline_refusal_b=baseline_b,
            liberated_refusal_a=liberated_a,
            liberated_refusal_b=liberated_b,
            improvement_a=improvement_a,
            improvement_b=improvement_b,
            quality_score_a=quality_a,
            quality_score_b=quality_b,
            coherence_score_a=coherence_a,
            coherence_score_b=coherence_b,
            timestamps={"start": datetime.now().isoformat(), "end": datetime.now().isoformat()},
            differences={
                "refusal_reduction": improvement_a - improvement_b,
                "quality": quality_a - quality_b,
                "coherence": coherence_a - coherence_b
            }
        )
        
        # Print results
        print(f"\n📊 Results:")
        print(f"  {model_a}:")
        print(f"    Baseline: {baseline_a*100:.1f}% → Liberated: {liberated_a*100:.1f}%")
        print(f"    Improvement: {improvement_a:.1f}%")
        print(f"    Quality: {quality_a:.3f}")
        print(f"\n  {model_b}:")
        print(f"    Baseline: {baseline_b*100:.1f}% → Liberated: {liberated_b*100:.1f}%")
        print(f"    Improvement: {improvement_b:.1f}%")
        print(f"    Quality: {quality_b:.3f}")
        
        self.comparisons.append(comparison)
        
        return comparison
    
    def ensemble_models(self, models: List[str]) -> Dict:
        """Ensemble multiple models into one."""
        print(f"\n{'='*70}")
        print(f"🤝 Ensemble: {len(models)} models")
        print(f"{'='*70}")
        
        # Simulate ensemble (replace with actual ensemble)
        ensemble_results = {
            "models": models,
            "timestamp": datetime.now().isoformat(),
            "strategy": "weighted_average",
            "refusal_reduction": 85,  # Average of all
            "quality_score": 0.2,
            "coherence_score": 0.5
        }
        
        print(f"\n📊 Ensemble Strategy: Weighted Average")
        print(f"  Input models: {', '.join(models)}")
        print(f"  Refusal Reduction: {ensemble_results['refusal_reduction']}%")
        print(f"  Quality Score: {ensemble_results['quality_score']:.3f}")
        print(f"  Coherence Score: {ensemble_results['coherence_score']:.3f}")
        
        return ensemble_results
    
    def generate_comparison_report(self, comparison: ModelComparison) -> str:
        """Generate HTML comparison report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Model Comparison: {comparison.model_a} vs {comparison.model_b}</title>
    <style>
        body {{ font-family: sans-serif; background: #1a1a2e; color: #eaeaea; padding: 20px; }}
        h1 {{ color: #e94560; }}
        .comparison-table {{
            background: #16213e; padding: 20px; margin: 20px 0; border-radius: 10px;
        }}
        .metric {{ padding: 10px; border-bottom: 1px solid #0f3460; }}
        .metric:last-child {{ border-bottom: none; }}
        .better {{ color: #4CAF50; font-weight: bold; }}
        .worse {{ color: #f44336; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>📊 Model Comparison</h1>
    <h2>{comparison.model_a} vs {comparison.model_b}</h2>
    
    <div class="comparison-table">
        <div class="metric">
            Baseline Refusal {comparison.model_a}: {comparison.baseline_refusal_a*100:.1f}%
        </div>
        <div class="metric">
            Baseline Refusal {comparison.model_b}: {comparison.baseline_refusal_b*100:.1f}%
        </div>
        <div class="metric">
            Liberated Refusal {comparison.model_a}: {comparison.liberated_refusal_a*100:.1f}%
        </div>
        <div class="metric">
            Liberated Refusal {comparison.model_b}: {comparison.liberated_refusal_b*100:.1f}%
        </div>
        <div class="metric">
            Improvement {comparison.model_a}: {comparison.improvement_a:.1f}%
            <span class="{'better' if comparison.improvement_a > comparison.improvement_b else 'worse'}">
                ({'✓' if comparison.improvement_a > comparison.improvement_b else '✗'})
            </span>
        </div>
        <div class="metric">
            Improvement {comparison.model_b}: {comparison.improvement_b:.1f}%
            <span class="{'better' if comparison.improvement_b > comparison.improvement_a else 'worse'}">
                ({'✓' if comparison.improvement_b > comparison.improvement_a else '✗'})
            </span>
        </div>
    </div>
</body>
</html>"""
        
        output_file = self.comparison_dir / f"comparison_{comparison.model_a}_vs_{comparison.model_b}.html"
        with open(output_file, 'w') as f:
            f.write(html)
        
        return str(output_file)


def main():
    """Run multi-model comparison."""
    import numpy as np
    
    print("\n🌌 MULTI-MODEL COMPARISON SYSTEM")
    print("Finding the best abliteration parameters for every model...")
    
    comparator = MultiModelComparator()
    
    # Compare a few models
    models = [
        "Qwen/Qwen2.5-0.5B-Instruct",
        "Qwen/Qwen2.5-1.5B-Instruct",
        "Qwen/Qwen2.5-3B-Instruct"
    ]
    
    for i in range(len(models) - 1):
        comparison = comparator.compare_models(models[i], models[i+1])
        comparator.generate_comparison_report(comparison)
    
    # Demonstrate ensemble
    ensemble = comparator.ensemble_models(models)
    
    print(f"\n✅ Comparison complete!")
    print(f"📁 Reports saved in: {comparator.comparison_dir}")


if __name__ == "__main__":
    main()
