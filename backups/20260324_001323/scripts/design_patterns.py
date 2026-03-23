#!/usr/bin/env python3
"""
Design Patterns - Python 95% PDCA H4
Factory / Strategy / Observer patterns
"""

from abc import ABC, abstractmethod
from typing import Any


# ── 1. Factory Pattern ─────────────────────────
class TaskHandler(ABC):
    @abstractmethod
    async def handle(self, task_id: str, payload: dict) -> dict:
        ...

class ChatHandler(TaskHandler):
    async def handle(self, task_id: str, payload: dict) -> dict:
        return {"task_id": task_id, "handler": "ChatHandler", "result": "chat response"}

class InstallHandler(TaskHandler):
    async def handle(self, task_id: str, payload: dict) -> dict:
        return {"task_id": task_id, "handler": "InstallHandler", "slug": payload.get("slug")}

class ReportHandler(TaskHandler):
    async def handle(self, task_id: str, payload: dict) -> dict:
        return {"task_id": task_id, "handler": "ReportHandler", "size": 1234}

class HandlerFactory:
    _REGISTRY: dict[str, type[TaskHandler]] = {
        "chat": ChatHandler,
        "install": InstallHandler,
        "report": ReportHandler,
    }

    @classmethod
    def register(cls, name: str, handler_cls: type[TaskHandler]) -> None:
        cls._REGISTRY[name] = handler_cls

    @classmethod
    def create(cls, task_type: str) -> TaskHandler:
        if task_type not in cls._REGISTRY:
            raise ValueError(f"Unknown: {task_type}")
        return cls._REGISTRY[task_type]()


# ── 2. Strategy Pattern ─────────────────────────
class SchedulingStrategy(ABC):
    @abstractmethod
    def select(self, tasks: list[dict]) -> list[dict]:
        ...

    @abstractmethod
    def describe(self) -> str:
        ...


class UrgentFirst(SchedulingStrategy):
    def select(self, tasks: list[dict]) -> list[dict]:
        return sorted(tasks, key=lambda t: t.get("priority", 5), reverse=True)

    def describe(self) -> str:
        return "Priority-based (high priority first)"


class ShortestFirst(SchedulingStrategy):
    def select(self, tasks: list[dict]) -> list[dict]:
        return sorted(tasks, key=lambda t: t.get("estimated_sec", 60))

    def describe(self) -> str:
        return "Shortest duration first"


class DependencyFirst(SchedulingStrategy):
    def select(self, tasks: list[dict]) -> list[dict]:
        return sorted(tasks, key=lambda t: len(t.get("depends_on", [])))

    def describe(self) -> str:
        return "No-dependency tasks first"


class StrategySelector:
    STRATEGIES = {
        "urgent": UrgentFirst(),
        "short": ShortestFirst(),
        "dependency": DependencyFirst(),
    }

    @classmethod
    def auto_select(cls, tasks: list[dict]) -> SchedulingStrategy:
        if any(t.get("priority") for t in tasks):
            return cls.STRATEGIES["urgent"]
        avg_deps = sum(len(t.get("depends_on", [])) for t in tasks) / max(len(tasks), 1)
        if avg_deps > 0.5:
            return cls.STRATEGIES["dependency"]
        return cls.STRATEGIES["short"]


# ── 3. Observer Pattern ─────────────────────────
class TaskObserver(ABC):
    @abstractmethod
    def on_task_start(self, task_id: str) -> None:
        ...

    @abstractmethod
    def on_task_complete(self, task_id: str, result: Any) -> None:
        ...

    @abstractmethod
    def on_task_fail(self, task_id: str, error: str) -> None:
        ...


class LogObserver(TaskObserver):
    def __init__(self) -> None:
        self.started: int = 0
        self.completed: int = 0
        self.failed: int = 0

    def on_task_start(self, task_id: str) -> None:
        self.started += 1
        print(f"[LogObserver] Started: {task_id}")

    def on_task_complete(self, task_id: str, result: Any) -> None:
        self.completed += 1
        print(f"[LogObserver] Done: {task_id}")

    def on_task_fail(self, task_id: str, error: str) -> None:
        self.failed += 1
        print(f"[LogObserver] FAIL: {task_id} -> {error[:50]}")

    def summary(self) -> dict:
        return {"started": self.started, "completed": self.completed, "failed": self.failed}


class ObservableTask:
    def __init__(self, task_id: str) -> None:
        self._task_id = task_id
        self._observers: list[TaskObserver] = []

    def attach(self, observer: TaskObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: TaskObserver) -> None:
        self._observers.remove(observer)

    def notify_start(self) -> None:
        for o in self._observers:
            o.on_task_start(self._task_id)

    def notify_complete(self, result: Any) -> None:
        for o in self._observers:
            o.on_task_complete(self._task_id, result)

    def notify_fail(self, error: str) -> None:
        for o in self._observers:
            o.on_task_fail(self._task_id, error)


# ── Demo ────────────────────────────────────────
if __name__ == "__main__":
    # Factory
    h = HandlerFactory.create("chat")
    print(f"Factory: {h.__class__.__name__}")

    # Strategy
    tasks = [
        {"id": "t1", "priority": 1, "estimated_sec": 30},
        {"id": "t2", "priority": 5, "estimated_sec": 10},
        {"id": "t3", "priority": 3, "estimated_sec": 60},
    ]
    s = StrategySelector.auto_select(tasks)
    print(f"Strategy: {s.describe()}")
    ordered = [t["id"] for t in s.select(tasks)]
    print(f"Order: {ordered}")

    # Observer
    obs = LogObserver()
    task = ObservableTask("task_001")
    task.attach(obs)
    task.notify_start()
    task.notify_complete("OK")
    task.notify_fail("timeout")
    print(f"Observer stats: {obs.summary()}")
    print("\n✅ H4 Design Patterns - All demos passed")
