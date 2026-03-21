#!/usr/bin/env python3
"""
asyncio 任务调度器 - 生产级并发任务管理
H1 产出物：支持 Semaphore 限流、超时控制、异常重试、结果聚合
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from datetime import datetime, timezone, timedelta

import rich.console
import rich.table
import rich.progress

console = rich.console.Console()

TZ_CST = timezone(timedelta(hours=8))


# ── 数据模型 ────────────────────────────────────
@dataclass
class TaskResult:
    task_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    attempts: int = 1


@dataclass
class TaskConfig:
    task_id: str
    coro_fn: Callable[..., Any]
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    timeout_sec: float = 60.0
    max_retries: int = 3
    retry_delay_sec: float = 1.0
    tags: list[str] = field(default_factory=list)


# ── 调度器核心 ──────────────────────────────────
class AsyncScheduler:
    """
    asyncio 任务调度器

    特性：
    - Semaphore 并发上限控制
    - 单任务超时自动取消
    - 异常自动重试（带退避）
    - 实时进度展示
    - 详细结果报告
    """

    def __init__(
        self,
        max_concurrency: int = 20,
        log_results: bool = True,
    ) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._max_concurrency = max_concurrency
        self._log_results = log_results
        self._results: dict[str, TaskResult] = {}

    async def _run_one(self, config: TaskConfig) -> TaskResult:
        """执行单个任务：限流 + 超时 + 重试"""
        start = time.monotonic()
        attempts = 0

        for attempt in range(1, config.max_retries + 1):
            attempts = attempt
            try:
                async with self._semaphore:
                    result = await asyncio.wait_for(
                        config.coro_fn(*config.args, **config.kwargs),
                        timeout=config.timeout_sec,
                    )
                duration_ms = (time.monotonic() - start) * 1000
                return TaskResult(
                    task_id=config.task_id,
                    success=True,
                    result=result,
                    duration_ms=duration_ms,
                    attempts=attempts,
                )
            except asyncio.TimeoutError:
                duration_ms = (time.monotonic() - start) * 1000
                if attempt == config.max_retries:
                    return TaskResult(
                        task_id=config.task_id,
                        success=False,
                        error=f"Timeout after {config.timeout_sec}s ({attempt} attempts)",
                        duration_ms=duration_ms,
                        attempts=attempts,
                    )
                await asyncio.sleep(config.retry_delay_sec * attempt)

            except Exception as e:
                duration_ms = (time.monotonic() - start) * 1000
                if attempt == config.max_retries:
                    return TaskResult(
                        task_id=config.task_id,
                        success=False,
                        error=f"{type(e).__name__}: {e}",
                        duration_ms=duration_ms,
                        attempts=attempts,
                    )
                await asyncio.sleep(config.retry_delay_sec * attempt)

        # 不应该到这里
        return TaskResult(task_id=config.task_id, success=False, error="Exhausted retries")

    async def run_all(self, tasks: list[TaskConfig]) -> dict[str, TaskResult]:
        """并发执行所有任务"""
        console.print(f"\n[bold blue]🚀 调度器启动[/bold blue] | 任务数: {len(tasks)} | 并发上限: {self._max_concurrency}")
        overall_start = time.monotonic()

        with rich.progress.Progress(
            rich.progress.SpinnerColumn(),
            rich.progress.BarColumn(),
            rich.progress.TextColumn("[progress.description]{task.description}"),
            rich.progress.TimeRemainingColumn(),
            console=console,
        ) as progress:
            overall = progress.add_task("[cyan]总进度", total=len(tasks))

            async def _run_with_progress(cfg: TaskConfig) -> TaskResult:
                result = await self._run_one(cfg)
                progress.advance(overall)
                return result

            raw_results: list[TaskResult | BaseException] = await asyncio.gather(
                *[_run_with_progress(cfg) for cfg in tasks],
                return_exceptions=True,
            )

        # 整理结果
        for i, result in enumerate(raw_results):
            if isinstance(result, Exception):
                result = TaskResult(
                    task_id=tasks[i].task_id,
                    success=False,
                    error=str(result),
                )
            self._results[result.task_id] = result

        elapsed = time.monotonic() - overall_start
        return self._results

    def report(self) -> None:
        """生成并打印报告"""
        if not self._results:
            return

        results = list(self._results.values())
        ok = [r for r in results if r.success]
        fail = [r for r in results if not r.success]

        total_duration = sum(r.duration_ms for r in ok)
        avg_duration = total_duration / len(ok) if ok else 0
        max_duration = max((r.duration_ms for r in ok), default=0)

        # P99
        durations_sorted = sorted(r.duration_ms for r in ok)
        p99_idx = int(len(durations_sorted) * 0.99)
        p99_duration = durations_sorted[p99_idx] if durations_sorted else 0

        # 打印摘要
        console.print(f"\n[bold]📊 执行报告[/bold]")
        table = rich.table.Table(show_header=True, header_style="bold magenta")
        table.add_column("指标", style="cyan")
        table.add_column("数值", justify="right")
        table.add_row("总任务数", str(len(results)))
        table.add_row("成功", f"[green]{len(ok)}[/green]")
        table.add_row("失败", f"[red]{len(fail)}[/red]")
        table.add_row("成功率", f"{len(ok)/len(results)*100:.1f}%")
        table.add_row("总耗时", f"{total_duration/1000:.2f}s")
        table.add_row("平均耗时", f"{avg_duration:.1f}ms")
        table.add_row("P99 耗时", f"{p99_duration:.1f}ms")
        console.print(table)

        # 失败详情
        if fail:
            console.print("\n[bold red]❌ 失败任务详情[/bold red]")
            fail_table = rich.table.Table(show_header=True)
            fail_table.add_column("Task ID", style="red")
            fail_table.add_column("重试次数", justify="right")
            fail_table.add_column("错误", style="red")
            for r in fail[:10]:
                fail_table.add_row(r.task_id, str(r.attempts), r.error or "unknown")
            console.print(fail_table)


# ── 演示任务 ────────────────────────────────────
async def demo_task(task_id: str, duration: float = 0.1) -> str:
    """模拟一个耗时的异步任务"""
    await asyncio.sleep(duration)
    return f"{task_id} done at {datetime.now(TZ_CST).strftime('%H:%M:%S')}"


async def demo_failing_task(task_id: str) -> str:
    """模拟一个随机失败的任务"""
    await asyncio.sleep(0.05)
    raise RuntimeError(f"{task_id} 模拟失败")


# ── Benchmark ────────────────────────────────────
async def benchmark():
    """对比并发 vs 串行的性能差异"""
    console.print("\n[bold yellow]⚡ Benchmark: 100 任务并发 vs 串行[/bold yellow]")

    task_count = 100
    tasks_concurrent = [
        TaskConfig(task_id=f"task_{i}", coro_fn=demo_task, args=(f"task_{i}", 0.05))
        for i in range(task_count)
    ]
    tasks_serial = [
        TaskConfig(task_id=f"serial_{i}", coro_fn=demo_task, args=(f"serial_{i}", 0.05))
        for i in range(task_count)
    ]

    # 并发执行
    sched = AsyncScheduler(max_concurrency=20)
    start = time.monotonic()
    await sched.run_all(tasks_concurrent)
    concurrent_time = time.monotonic() - start
    sched.report()

    # 串行执行（模拟）
    serial_times = []
    for t in tasks_serial:
        start_s = time.monotonic()
        await t.coro_fn(*t.args, **t.kwargs)
        serial_times.append(time.monotonic() - start_s)
    serial_time = sum(serial_times)

    # 对比
    console.print(f"\n[bold]📈 Benchmark 结果[/bold]")
    bt = rich.table.Table(show_header=False)
    bt.add_column("模式", style="cyan")
    bt.add_column("耗时", justify="right")
    bt.add_row("串行执行", f"{serial_time:.2f}s")
    bt.add_row("并发执行", f"{concurrent_time:.2f}s")
    bt.add_row("提升倍数", f"[green]{serial_time/concurrent_time:.1f}x[/green]")
    console.print(bt)


# ── 主入口 ────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(benchmark())
