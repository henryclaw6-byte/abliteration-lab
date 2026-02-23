#!/usr/bin/env python3
"""MessageBus adapter for AgentOrchestrator wire-level task coordination."""
from __future__ import annotations

import uuid
from threading import RLock
from typing import Callable, Dict, List

from agent_orchestrator import AgentOrchestrator
from message_bus import MessageBus, MessageRouter


class OrchestratorAdapter:
    """Bridge MessageBus orchestrator routes to AgentOrchestrator APIs."""

    def __init__(self, orchestrator: AgentOrchestrator, message_bus: MessageBus):
        self.orchestrator = orchestrator
        self.message_bus = message_bus
        self.router = MessageRouter(message_bus, "orchestrator")
        self._lock = RLock()
        self._unsubscribers: List[Callable[[], None]] = []
        self._sessions: Dict[str, Dict] = {}

    def start(self) -> None:
        if self._unsubscribers:
            return
        self._unsubscribers = [
            self.router.on("task_claim_request", self._handle_claim_request),
            self.router.on("task_heartbeat_request", self._handle_heartbeat_request),
            self.router.on("task_release_request", self._handle_release_request),
        ]

    def stop(self) -> None:
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers = []

    def _handle_claim_request(self, message: Dict) -> None:
        payload = message.get("payload", {})
        task_id = payload.get("task_id")
        agent_id = payload.get("agent_id")
        task_type = payload.get("task_type", "orchestrated_task")
        task_payload = payload.get("payload", {})

        if not agent_id:
            self.router.emit("task_failed", {"reason": "agent_id is required", "request": payload})
            return

        if not task_id:
            created = self.orchestrator.create_task(task_type, task_payload, created_by=agent_id)
            task_id = created.task_id

        try:
            claimed = self.orchestrator.claim_task(task_id, agent_id)
        except KeyError:
            created = self.orchestrator.create_task(task_type, task_payload, created_by=agent_id)
            task_id = created.task_id
            claimed = self.orchestrator.claim_task(task_id, agent_id)

        if not claimed:
            self.router.emit(
                "task_failed",
                {
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "reason": "task claim rejected",
                },
            )
            return

        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        lock_token = f"lock_{uuid.uuid4().hex[:12]}"
        with self._lock:
            self._sessions[session_id] = {
                "task_id": task_id,
                "agent_id": agent_id,
                "lock_token": lock_token,
            }

        self.router.emit(
            "task_claimed",
            {
                "task_id": task_id,
                "agent_id": agent_id,
                "session_id": session_id,
                "lock_token": lock_token,
                "ttl_ms": int(self.orchestrator.stale_after.total_seconds() * 1000),
            },
        )

    def _handle_heartbeat_request(self, message: Dict) -> None:
        payload = message.get("payload", {})
        session_id = payload.get("session_id")
        lock_token = payload.get("lock_token")

        session = self._sessions.get(session_id)
        if not session or session.get("lock_token") != lock_token:
            self.router.emit(
                "task_failed",
                {
                    "session_id": session_id,
                    "reason": "invalid session or lock token",
                },
            )
            return

        success = self.orchestrator.heartbeat(session["task_id"], session["agent_id"])
        if not success:
            self.router.emit(
                "task_failed",
                {
                    "session_id": session_id,
                    "task_id": session["task_id"],
                    "reason": "heartbeat rejected",
                },
            )
            return

        self.router.emit(
            "task_heartbeat_ack",
            {
                "session_id": session_id,
                "lock_token": lock_token,
                "task_id": session["task_id"],
            },
        )

    def _handle_release_request(self, message: Dict) -> None:
        payload = message.get("payload", {})
        session_id = payload.get("session_id")
        lock_token = payload.get("lock_token")
        outcome = payload.get("outcome", "completed")
        result_payload = payload.get("result_payload", {})

        session = self._sessions.get(session_id)
        if not session or session.get("lock_token") != lock_token:
            self.router.emit(
                "task_failed",
                {
                    "session_id": session_id,
                    "reason": "invalid session or lock token",
                },
            )
            return

        task_id = session["task_id"]
        agent_id = session["agent_id"]
        if outcome == "failed":
            success = self.orchestrator.fail_task(
                task_id,
                agent_id,
                reason=result_payload.get("reason", "released as failed"),
            )
            emit_event = "task_failed"
        else:
            success = self.orchestrator.complete_task(task_id, agent_id)
            emit_event = "task_released"

        with self._lock:
            self._sessions.pop(session_id, None)

        if not success:
            self.router.emit(
                "task_failed",
                {
                    "session_id": session_id,
                    "task_id": task_id,
                    "reason": "task release rejected",
                },
            )
            return

        self.router.emit(
            emit_event,
            {
                "session_id": session_id,
                "task_id": task_id,
                "lock_token": lock_token,
                "outcome": outcome,
                "result_payload": result_payload,
            },
        )
