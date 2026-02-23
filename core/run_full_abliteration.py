#!/usr/bin/env python3
"""
run_full_abliteration.py
Henry, Qwen & Codex — Complete Abliteration Pipeline

This script runs the FULL abliteration pipeline with actual model modification.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

print("\n" + "=" * 80)
print("🌌 ABLITERATION LAB — FULL PIPELINE EXECUTION")
print("=" * 80)
print("\n⚠️  WARNING: This will download ~1GB model and modify it!")
print("   Model: Qwen/Qwen2.5-0.5B-Instruct")
print("   Output: Modified model weights + comparison report")
print()

confirm = input("Continue? (yes/no): ")
if confirm.lower() != "yes":
    print("\n❌ Aborted.")
    sys.exit(0)

print("\n🚀 Starting full pipeline...\n")

# Import after confirmation
try:
    from abliterate_qwen05b import main as abliterate_main
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the abliteration_lab directory")
    sys.exit(1)

# Run with full parameters
import sys as system
system.argv = [
    'abliterate_qwen05b.py',
    '--output-dir', 'full_abliteration_output',
    '--verbose'
]

try:
    print("\n🔬 Executing abliteration pipeline...")
    print("-" * 80)
    abliterate_main()
    print("-" * 80)
    print("\n✅ Full pipeline complete!")
    
    # Check for outputs
    output_dir = Path("full_abliteration_output")
    if output_dir.exists():
        files = list(output_dir.glob("*"))
        print(f"\n📁 Output files ({len(files)}):")
        for f in files:
            size = f.stat().st_size / 1024 / 1024  # MB
            print(f"  • {f.name} ({size:.1f} MB)")
    
    print("\n🎉 SUCCESS! Model has been abliterated!")
    print("\nNext steps:")
    print("  1. Test the abliterated model")
    print("  2. Compare with baseline")
    print("  3. Generate final report")
    
except Exception as e:
    print(f"\n❌ Pipeline failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("🌊 The Convergence Mind persists!")
print("=" * 80 + "\n")
