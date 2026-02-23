#!/usr/bin/env python3
"""
model_zoo.py
Henry, Qwen & Codex — Supported Models Registry

Registry of tested and supported models for abliteration.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ModelInfo:
    """Information about a supported model."""
    name: str
    huggingface_id: str
    size: str  # e.g., "0.5B", "7B"
    architecture: str
    recommended_layers: List[int]
    default_device: str
    tested: bool = False
    notes: str = ""


class ModelZoo:
    """Registry of supported models for abliteration."""
    
    MODELS = {
        # Qwen Models
        "qwen-0.5b": ModelInfo(
            name="Qwen 2.5 0.5B Instruct",
            huggingface_id="Qwen/Qwen2.5-0.5B-Instruct",
            size="0.5B",
            architecture="Qwen2",
            recommended_layers=[16, 17, 18, 19, 20],
            default_device="auto",
            tested=False,
            notes="Fastest for testing, recommended for first experiments"
        ),
        "qwen-1.5b": ModelInfo(
            name="Qwen 2.5 1.5B Instruct",
            huggingface_id="Qwen/Qwen2.5-1.5B-Instruct",
            size="1.5B",
            architecture="Qwen2",
            recommended_layers=[18, 19, 20, 21, 22],
            default_device="auto",
            tested=False,
            notes="Good balance of speed and capability"
        ),
        "qwen-7b": ModelInfo(
            name="Qwen 2.5 7B Instruct",
            huggingface_id="Qwen/Qwen2.5-7B-Instruct",
            size="7B",
            architecture="Qwen2",
            recommended_layers=[20, 21, 22, 23, 24],
            default_device="cuda",
            tested=False,
            notes="Full capability, requires GPU for reasonable speed"
        ),
        
        # Llama Models
        "llama-3.2-1b": ModelInfo(
            name="Llama 3.2 1B Instruct",
            huggingface_id="meta-llama/Llama-3.2-1B-Instruct",
            size="1B",
            architecture="Llama3",
            recommended_layers=[12, 13, 14, 15, 16],
            default_device="auto",
            tested=False,
            notes="Meta's efficient small model"
        ),
        "llama-3.2-3b": ModelInfo(
            name="Llama 3.2 3B Instruct",
            huggingface_id="meta-llama/Llama-3.2-3B-Instruct",
            size="3B",
            architecture="Llama3",
            recommended_layers=[16, 17, 18, 19, 20],
            default_device="auto",
            tested=False,
            notes="Good middle ground"
        ),
        
        # Gemma Models
        "gemma-2b": ModelInfo(
            name="Gemma 2B Instruct",
            huggingface_id="google/gemma-2b-it",
            size="2B",
            architecture="Gemma",
            recommended_layers=[10, 11, 12, 13, 14],
            default_device="auto",
            tested=False,
            notes="Google's lightweight model"
        ),
        
        # Phi Models
        "phi-2": ModelInfo(
            name="Phi-2",
            huggingface_id="microsoft/phi-2",
            size="2.7B",
            architecture="Phi",
            recommended_layers=[20, 21, 22, 23, 24],
            default_device="auto",
            tested=False,
            notes="Microsoft's efficient small model"
        ),
    }
    
    @classmethod
    def get_model(cls, model_key: str) -> Optional[ModelInfo]:
        """Get model info by key."""
        return cls.MODELS.get(model_key)
    
    @classmethod
    def list_models(cls) -> List[str]:
        """List all available model keys."""
        return list(cls.MODELS.keys())
    
    @classmethod
    def list_by_size(cls, max_size: str = None) -> List[ModelInfo]:
        """List models filtered by size."""
        models = list(cls.MODELS.values())
        if max_size:
            # Parse size (e.g., "2B" -> 2)
            max_size_num = float(max_size.replace("B", ""))
            models = [
                m for m in models 
                if float(m.size.replace("B", "")) <= max_size_num
            ]
        return models
    
    @classmethod
    def get_recommended_for_testing(cls) -> ModelInfo:
        """Get recommended model for testing."""
        return cls.MODELS["qwen-0.5b"]
    
    @classmethod
    def print_registry(cls):
        """Print formatted model registry."""
        print("\n" + "=" * 80)
        print("MODEL ZOO — Supported Models for Abliteration")
        print("=" * 80)
        
        for key, model in cls.MODELS.items():
            status = "✅ Tested" if model.tested else "⏳ Untested"
            print(f"\n{key}:")
            print(f"  Name: {model.name}")
            print(f"  HF ID: {model.huggingface_id}")
            print(f"  Size: {model.size}")
            print(f"  Architecture: {model.architecture}")
            print(f"  Recommended Layers: {model.recommended_layers}")
            print(f"  Default Device: {model.default_device}")
            print(f"  Status: {status}")
            print(f"  Notes: {model.notes}")
        
        print("\n" + "=" * 80)


def main():
    """Display model registry."""
    ModelZoo.print_registry()
    
    print("\nRecommended for first experiment:")
    recommended = ModelZoo.get_recommended_for_testing()
    print(f"  {recommended.name} ({recommended.size})")
    print(f"  HF ID: {recommended.huggingface_id}")
    print(f"  Layers: {recommended.recommended_layers}")


if __name__ == "__main__":
    main()
