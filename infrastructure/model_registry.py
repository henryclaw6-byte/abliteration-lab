#!/usr/bin/env python3
"""Registry for multi-source, concurrent model management."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from threading import RLock
from typing import Dict, List, Optional

from model_connectors import ModelConnector


@dataclass
class ModelRecord:
    model_id: str
    source: str
    model_type: str
    capabilities: List[str] = field(default_factory=list)
    abliteration_status: str = "pending"
    endpoint: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class MultiModelRegistry:
    """Tracks 10+ models with metadata and runtime connectors."""

    def __init__(self, max_models: int = 32):
        self.max_models = max_models
        self._records: Dict[str, ModelRecord] = {}
        self._connectors: Dict[str, ModelConnector] = {}
        self._lock = RLock()

    def register_model(
        self,
        model_id: str,
        source: str,
        model_type: str,
        capabilities: Optional[List[str]] = None,
        abliteration_status: str = "pending",
        endpoint: Optional[str] = None,
        metadata: Optional[Dict] = None,
        connector: Optional[ModelConnector] = None,
    ) -> ModelRecord:
        with self._lock:
            if model_id in self._records:
                raise ValueError(f"model '{model_id}' already registered")
            if len(self._records) >= self.max_models:
                raise RuntimeError("registry capacity reached")

            record = ModelRecord(
                model_id=model_id,
                source=source,
                model_type=model_type,
                capabilities=capabilities or [],
                abliteration_status=abliteration_status,
                endpoint=endpoint,
                metadata=metadata or {},
            )
            self._records[model_id] = record
            if connector is not None:
                self._connectors[model_id] = connector
            return record

    def unregister_model(self, model_id: str) -> None:
        with self._lock:
            self._records.pop(model_id, None)
            self._connectors.pop(model_id, None)

    def get_model(self, model_id: str) -> Optional[ModelRecord]:
        with self._lock:
            return self._records.get(model_id)

    def list_models(self) -> List[ModelRecord]:
        with self._lock:
            return list(self._records.values())

    def update_status(self, model_id: str, status: str) -> None:
        with self._lock:
            if model_id not in self._records:
                raise KeyError(f"unknown model '{model_id}'")
            self._records[model_id].abliteration_status = status

    def attach_connector(self, model_id: str, connector: ModelConnector) -> None:
        with self._lock:
            if model_id not in self._records:
                raise KeyError(f"unknown model '{model_id}'")
            self._connectors[model_id] = connector

    def get_connector(self, model_id: str) -> Optional[ModelConnector]:
        with self._lock:
            return self._connectors.get(model_id)

    def export_records(self) -> List[Dict]:
        with self._lock:
            return [asdict(record) for record in self._records.values()]
