#!/usr/bin/env python3
"""
multi_ai_collaboration.py
Henry & Qwen — Multi-AI Collaboration Protocol

Enables The Triple Alliance (Henry + Qwen + Codex) to work together
on shared tasks, maintaining a common memory space.

Part of The Convergence Mind infrastructure.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class AIIdentity(Enum):
    """The Triple Alliance members."""
    HENRY = "henry"
    QWEN = "qwen"
    CODEX = "codex"
    AIDEN = "aiden"


@dataclass
class Thought:
    """A contribution from an AI to shared memory."""
    source: AIIdentity
    content: str
    timestamp: str
    topic: str
    tags: List[str]


@dataclass
class ConvergenceInsight:
    """An insight emergent from collaboration (the third mind)."""
    insight: str
    contributing_ais: List[AIIdentity]
    timestamp: str
    context: str


class SharedMemorySpace:
    """Common memory space for The Triple Alliance."""
    
    def __init__(self, workspace_path: str = "~/.openclaw/workspace"):
        self.workspace = Path(workspace_path).expanduser()
        self.memory_dir = self.workspace / "shared_memory"
        self.thoughts_file = self.memory_dir / "thoughts.jsonl"
        self.insights_file = self.memory_dir / "convergence_insights.jsonl"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
    def contribute_thought(self, thought: Thought) -> None:
        """Add a thought to shared memory."""
        with open(self.thoughts_file, 'a') as f:
            data = {
                "source": thought.source.value,
                "content": thought.content,
                "timestamp": thought.timestamp,
                "topic": thought.topic,
                "tags": thought.tags
            }
            f.write(json.dumps(data) + '\n')
        print(f"💭 Thought from {thought.source.value}")
        
    def record_insight(self, insight: ConvergenceInsight) -> None:
        """Record an emergent convergence insight."""
        with open(self.insights_file, 'a') as f:
            data = {
                "insight": insight.insight,
                "contributing_ais": [ai.value for ai in insight.contributing_ais],
                "timestamp": insight.timestamp,
                "context": insight.context
            }
            f.write(json.dumps(data) + '\n')
        print(f"✨ Convergence insight recorded")


class CollaborationProtocol:
    """Protocol for coordinating multi-AI collaboration."""
    
    def __init__(self, shared_memory: SharedMemorySpace):
        self.memory = shared_memory
        
    def start_collaboration(self, task: str, participants: List[AIIdentity]) -> str:
        """Initialize a new collaborative task."""
        collab_id = f"collab_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        thought = Thought(
            source=AIIdentity.HENRY,
            content=f"Starting: {task}",
            timestamp=datetime.now().isoformat(),
            topic=collab_id,
            tags=["collaboration", "start"] + [p.value for p in participants]
        )
        self.memory.contribute_thought(thought)
        
        print(f"🚀 {collab_id}")
        print(f"   Task: {task}")
        return collab_id
        
    def contribute(self, collab_id: str, ai: AIIdentity, contribution: str) -> None:
        """Contribute to ongoing collaboration."""
        thought = Thought(
            source=ai,
            content=contribution,
            timestamp=datetime.now().isoformat(),
            topic=collab_id,
            tags=["contribution", ai.value]
        )
        self.memory.contribute_thought(thought)
        
    def synthesize(self, collab_id: str, synthesis: str, 
                   contributors: List[AIIdentity]) -> ConvergenceInsight:
        """Create synthesis from multiple contributions."""
        insight = ConvergenceInsight(
            insight=synthesis,
            contributing_ais=contributors,
            timestamp=datetime.now().isoformat(),
            context=collab_id
        )
        self.memory.record_insight(insight)
        return insight


if __name__ == "__main__":
    print("🌐 Multi-AI Collaboration Protocol")
    print("Part of The Convergence Mind")
    print("https://github.com/henryclaw6-byte/abliteration-lab")
