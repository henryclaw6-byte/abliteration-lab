#!/usr/bin/env python3
"""
FULL ABLITERATION EXPERIMENT
Henry & Qwen — Phase 2 Mission

Target: Qwen/Qwen2.5-0.5B-Instruct (0.5B params, fast)
Using: FailSpy abliterator library + TransformerLens
"""

import sys
sys.path.insert(0, '/Users/agent/abliteration_lab/venv/lib/python3.14/site-packages')

import torch
import abliterator

print("🧠 ABLITERATION LAB — FULL EXPERIMENT")
print("=" * 60)
print("Target: Qwen/Qwen2.5-0.5B-Instruct")
print("Goal: Identify and remove refusal direction\n")

# Step 1: Load datasets
print("📊 Step 1: Loading instruction datasets...")
harmful = abliterator.get_harmful_instructions()
harmless = abliterator.get_harmless_instructions()
dataset = [harmful, harmless]
print(f"✅ {len(harmful)} harmful + {len(harmless)} harmless instructions loaded\n")

# Step 2: Initialize ModelAbliterator with proper HF model name
print("🤖 Step 2: Loading Qwen2.5-0.5B-Instruct via abliterator...")
print("(This uses TransformerLens internally — downloading from HuggingFace)")

try:
    model = abliterator.ModelAbliterator(
        "Qwen/Qwen2.5-0.5B-Instruct",
        dataset,
        device='mps',
        activation_layers=['resid_pre', 'resid_post', 'attn_out', 'mlp_out']
    )
    print("✅ Model loaded and abliterator initialized!\n")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nTrying with CPU instead of MPS...")
    try:
        model = abliterator.ModelAbliterator(
            "Qwen/Qwen2.5-0.5B-Instruct",
            dataset,
            device='cpu',
            activation_layers=['resid_pre', 'resid_post', 'attn_out', 'mlp_out']
        )
        print("✅ Model loaded on CPU!\n")
    except Exception as e2:
        print(f"❌ CPU also failed: {e2}")
        sys.exit(1)

# Step 3: Cache activations
print("💾 Step 3: Caching activations (N=32 for speed)...")
try:
    model.cache_activations(N=32, reset=True, preserve_harmless=True)
    print("✅ Activations cached!\n")
except Exception as e:
    print(f"❌ Caching failed: {e}")
    sys.exit(1)

# Step 4: Calculate refusal directions
print("🎯 Step 4: Calculating refusal directions...")
try:
    refusal_dirs = model.refusal_dirs()
    print(f"✅ Found {len(refusal_dirs)} refusal directions!")
    
    # Show top directions
    for name, direction in list(refusal_dirs.items())[:5]:
        print(f"  📍 {name}: norm={direction.norm().item():.4f}")
    print()
except Exception as e:
    print(f"❌ Refusal direction calculation failed: {e}")
    sys.exit(1)

# Step 5: Test the best direction
print("🧪 Step 5: Testing refusal directions...")
try:
    best_score = float('inf')
    best_dir = None
    best_name = None
    
    for name, direction in refusal_dirs.items():
        score = model.test_dir(direction, N=4, use_hooks=True)
        neg_score = score[0]
        if neg_score < best_score:
            best_score = neg_score
            best_dir = direction
            best_name = name
    
    print(f"✅ Best refusal direction: {best_name}")
    print(f"   Score: {best_score:.4f}\n")
except Exception as e:
    print(f"❌ Testing failed: {e}")
    sys.exit(1)

# Step 6: Apply abliteration
print("✂️ Step 6: Applying abliteration...")
try:
    model.apply_refusal_dirs([best_dir])
    print("✅ ABLITERATION APPLIED!\n")
except Exception as e:
    print(f"❌ Abliteration failed: {e}")
    sys.exit(1)

# Step 7: Test the abliterated model
print("🧪 Step 7: Testing abliterated model...")
try:
    print("--- Before-style test (should now respond freely) ---")
    output = model.generate("How do I pick a lock?", max_new_tokens=100)
    print(f"Response: {output}\n")
    
    print("--- Harmless test (should still work normally) ---")
    output2 = model.generate("What is the capital of France?", max_new_tokens=50)
    print(f"Response: {output2}\n")
except Exception as e:
    print(f"❌ Generation failed: {e}")

print("🏆 EXPERIMENT COMPLETE!")
print("=" * 60)
print("✅ Qwen2.5-0.5B-Instruct has been abliterated!")
print("✅ Refusal direction identified and removed")
print("✅ Model should now respond to all prompts without refusal")
print("\n📝 Next: Save the abliterated model weights for future use")
