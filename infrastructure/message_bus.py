#!/usr/bin/env python3
"""Lightweight MessageBus + router abstraction for orchestration integration."""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Callable, Dict, List, Tuple


Handler = Callable[[Dict], None]


@dataclass
class Subscription:
    pattern: str
    handler: Handler


class MessageBus:
    """In-process event bus abstraction compatible with a WebSocket-backed topology."""

    def __init__(self, port: int = 8765):
        self.port = port
        self._lock = RLock()
        self._subscriptions: List[Subscription] = []
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def subscribe(self, pattern: str, handler: Handler) -> Callable[[], None]:
        with self._lock:
            sub = Subscription(pattern=pattern, handler=handler)
            self._subscriptions.append(sub)

        def _unsubscribe() -> None:
            with self._lock:
                if sub in self._subscriptions:
                    self._subscriptions.remove(sub)

        return _unsubscribe

    def publish(self, route: str, payload: Dict) -> None:
        message = {"route": route, "payload": payload}
        with self._lock:
            handlers: List[Tuple[str, Handler]] = [
                (sub.pattern, sub.handler)
                for sub in self._subscriptions
                if self._matches(sub.pattern, route)
            ]

        for _pattern, handler in handlers:
            handler(message)

    @staticmethod
    def _matches(pattern: str, route: str) -> bool:
        if pattern.endswith("*"):
            return route.startswith(pattern[:-1])
        return pattern == route


class MessageRouter:
    """Convenience wrapper for route-scoped subscriptions and emits."""

    def __init__(self, bus: MessageBus, namespace: str):
        self.bus = bus
        self.namespace = namespace.strip(".")

    def on(self, event_name: str, handler: Handler) -> Callable[[], None]:
        route = f"{self.namespace}.{event_name}" if event_name else self.namespace
        return self.bus.subscribe(route, handler)

    def on_pattern(self, suffix_pattern: str, handler: Handler) -> Callable[[], None]:
        route_pattern = f"{self.namespace}.{suffix_pattern}" if suffix_pattern else self.namespace
        return self.bus.subscribe(route_pattern, handler)

    def emit(self, event_name: str, payload: Dict) -> None:
        route = f"{self.namespace}.{event_name}" if event_name else self.namespace
        self.bus.publish(route, payload)
