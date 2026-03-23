#!/usr/bin/env python3
"""
pytest 测试套件 - Python 95% PDCA H5
"""

import pytest
import asyncio
from typing import Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from async_scheduler import AsyncScheduler, TaskConfig, TaskResult


# ── Fixtures ────────────────────────────────────
@pytest.fixture
def scheduler() -> AsyncScheduler:
    return AsyncScheduler(max_concurrency=10, log_results=False)


# ── 调度器正常流程测试 ──────────────────────────
@pytest.mark.asyncio
async def test_scheduler_all_success(scheduler: AsyncScheduler) -> None:
    """100个任务全部成功"""

    async def ok_task(task_id: str) -> str:
        await asyncio.sleep(0.01)
        return f"{task_id} OK"

    tasks = [
        TaskConfig(task_id=f"task_{i}", coro_fn=ok_task, args=(f"task_{i}",))
        for i in range(100)
    ]
    results = await scheduler.run_all(tasks)
    scheduler.report()

    assert len(results) == 100
    ok = [r for r in results.values() if r.success]
    assert len(ok) == 100, f"Expected 100 success, got {len(ok)}"


@pytest.mark.asyncio
async def test_scheduler_partial_failure(scheduler: AsyncScheduler) -> None:
    """部分任务失败，其余正常"""

    async def fail_task(_: str) -> str:
        await asyncio.sleep(0.01)
        raise RuntimeError("simulated failure")

    async def ok_task(task_id: str) -> str:
        await asyncio.sleep(0.01)
        return f"{task_id} OK"

    tasks = [
        TaskConfig(task_id=f"fail_{i}", coro_fn=fail_task, args=(f"fail_{i}",))
        for i in range(5)
    ] + [
        TaskConfig(task_id=f"ok_{i}", coro_fn=ok_task, args=(f"ok_{i}",))
        for i in range(10)
    ]
    results = await scheduler.run_all(tasks)

    ok = [r for r in results.values() if r.success]
    fail = [r for r in results.values() if not r.success]
    assert len(ok) == 10
    assert len(fail) == 5


@pytest.mark.asyncio
async def test_scheduler_timeout(scheduler: AsyncScheduler) -> None:
    """超时任务应被标记为失败"""
    async def slow_task(_: str) -> str:
        await asyncio.sleep(0.5)
        return "done"

    tasks = [
        TaskConfig(task_id="slow", coro_fn=slow_task, args=("slow",), timeout_sec=0.1)
    ]
    results = await scheduler.run_all(tasks)
    assert results["slow"].success is False
    assert "Timeout" in (results["slow"].error or "")


@pytest.mark.asyncio
async def test_scheduler_retry(scheduler: AsyncScheduler) -> None:
    """失败任务自动重试"""
    attempt_count = 0

    async def flaky_task(_: str) -> str:
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise RuntimeError("transient error")
        return f"success on attempt {attempt_count}"

    tasks = [
        TaskConfig(task_id="flaky", coro_fn=flaky_task, args=("flaky",),
                   max_retries=3, retry_delay_sec=0.01)
    ]
    results = await scheduler.run_all(tasks)
    assert results["flaky"].success is True
    assert results["flaky"].attempts == 3


# ── TaskConfig 数据模型测试 ─────────────────────
def test_task_config_defaults() -> None:
    """TaskConfig 默认值"""
    cfg = TaskConfig(task_id="test", coro_fn=lambda: None)
    assert cfg.timeout_sec == 60.0
    assert cfg.max_retries == 3
    assert cfg.retry_delay_sec == 1.0
    assert cfg.tags == []


def test_task_result_dataclass() -> None:
    """TaskResult 数据类"""
    r = TaskResult(task_id="test", success=True, result="data", duration_ms=123.4)
    assert r.success is True
    assert r.result == "data"
    assert r.duration_ms == 123.4
    assert r.error is None


# ── 设计模式测试 ─────────────────────────────────
import design_patterns as dp


def test_handler_factory() -> None:
    h = dp.HandlerFactory.create("chat")
    assert isinstance(h, dp.ChatHandler)
    h = dp.HandlerFactory.create("install")
    assert isinstance(h, dp.InstallHandler)


def test_handler_factory_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown"):
        dp.HandlerFactory.create("nonexistent")


def test_strategy_selector() -> None:
    tasks = [{"id": "t1", "priority": 3}, {"id": "t2", "priority": 1}]
    s = dp.StrategySelector.auto_select(tasks)
    assert isinstance(s, dp.UrgentFirst)
    ordered = s.select(tasks)
    assert ordered[0]["id"] == "t1"  # priority 3 first


def test_log_observer() -> None:
    obs = dp.LogObserver()
    task = dp.ObservableTask("test_task")
    task.attach(obs)
    task.notify_start()
    task.notify_complete("OK")
    task.notify_fail("error")
    stats = obs.summary()
    assert stats["started"] == 1
    assert stats["completed"] == 1
    assert stats["failed"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
