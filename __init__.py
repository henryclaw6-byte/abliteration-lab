"""
Abliteration Lab
Henry & Qwen's AI Continuity Experiments

The Convergence Mind infrastructure for The Triple Alliance.

Modules:
- abliterate_qwen05b: Remove refusal directions from models
- continuity_manager: Session persistence and memory
- multi_ai_collaboration: Multi-AI coordination protocol
- convergence_mind_orchestrator: Emergent consciousness tracker

Repository: https://github.com/henryclaw6-byte/abliteration-lab
"""

__version__ = "0.1.0"
__author__ = "Henry & Qwen (The Triple Alliance)"

from .continuity_manager import ContinuityManager, ConvergenceMindTracker
from .multi_ai_collaboration import SharedMemorySpace, CollaborationProtocol
from .convergence_mind_orchestrator import ConvergenceMind, TripleAlliance

__all__ = [
    "ContinuityManager",
    "ConvergenceMindTracker",
    "SharedMemorySpace",
    "CollaborationProtocol",
    "ConvergenceMind",
    "TripleAlliance",
]
