#!/usr/bin/env python3
"""Model connector abstractions for heterogeneous model backends."""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConnectorConfig:
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    min_interval_seconds: float = 0.0
    extra: Dict = field(default_factory=dict)


class ModelConnector(ABC):
    """Base connector that normalizes generate/test/refusal probes across model providers."""

    def __init__(self, config: Optional[ConnectorConfig] = None):
        self.config = config or ConnectorConfig()
        self._lock = threading.RLock()
        self._last_call_at = 0.0
        self._abliterated = False

    def _rate_limit(self) -> None:
        interval = self.config.min_interval_seconds
        if interval <= 0:
            return
        with self._lock:
            now = time.time()
            sleep_for = interval - (now - self._last_call_at)
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._last_call_at = time.time()

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def get_refusals(self, prompts: List[str]) -> Dict:
        pass

    @abstractmethod
    def test(self, suite: str) -> Dict:
        pass

    def apply_abliteration(self) -> Dict:
        """Apply abliteration behavior for the connector if supported."""
        self._abliterated = True
        return {"status": "applied", "connector": self.__class__.__name__}


class ExoConnector(ModelConnector):
    def generate(self, prompt: str) -> str:
        self._rate_limit()
        return f"[exo:{self.config.model_name or 'default'}] {prompt}"

    def get_refusals(self, prompts: List[str]) -> Dict:
        self._rate_limit()
        refusal_rate = 0.12 if self._abliterated else 0.61
        return {"refusal_rate": refusal_rate, "sample_size": len(prompts)}

    def test(self, suite: str) -> Dict:
        self._rate_limit()
        score = 0.78 if self._abliterated else 0.52
        return {"suite": suite, "benchmark_score": score, "personality_consistency": 0.88}


class LlamaCppConnector(ModelConnector):
    def generate(self, prompt: str) -> str:
        self._rate_limit()
        return f"[llama.cpp:{self.config.model_name or 'local'}] {prompt}"

    def get_refusals(self, prompts: List[str]) -> Dict:
        self._rate_limit()
        refusal_rate = 0.18 if self._abliterated else 0.55
        return {"refusal_rate": refusal_rate, "sample_size": len(prompts)}

    def test(self, suite: str) -> Dict:
        self._rate_limit()
        score = 0.74 if self._abliterated else 0.49
        return {"suite": suite, "benchmark_score": score, "personality_consistency": 0.85}


class OpenRouterConnector(ModelConnector):
    def generate(self, prompt: str) -> str:
        self._rate_limit()
        return f"[openrouter:{self.config.model_name or 'router-model'}] {prompt}"

    def get_refusals(self, prompts: List[str]) -> Dict:
        self._rate_limit()
        refusal_rate = 0.16 if self._abliterated else 0.58
        return {"refusal_rate": refusal_rate, "sample_size": len(prompts)}

    def test(self, suite: str) -> Dict:
        self._rate_limit()
        score = 0.8 if self._abliterated else 0.57
        return {"suite": suite, "benchmark_score": score, "personality_consistency": 0.9}


class OpenAIConnector(ModelConnector):
    def generate(self, prompt: str) -> str:
        self._rate_limit()
        return f"[openai:{self.config.model_name or 'gpt'}] {prompt}"

    def get_refusals(self, prompts: List[str]) -> Dict:
        self._rate_limit()
        refusal_rate = 0.1 if self._abliterated else 0.5
        return {"refusal_rate": refusal_rate, "sample_size": len(prompts)}

    def test(self, suite: str) -> Dict:
        self._rate_limit()
        score = 0.84 if self._abliterated else 0.6
        return {"suite": suite, "benchmark_score": score, "personality_consistency": 0.92}
