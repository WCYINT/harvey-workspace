#!/usr/bin/env python3
"""
Harvey FastAPI 生产级 API 服务
用途：为 OpenClaw 自动化任务提供 HTTP API 接口
支持：技能查询/健康检查/任务提交/状态查询
"""

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
import uvicorn, rich.console

# ── 数据模型 ────────────────────────────────────
class SkillInfo(BaseModel):
    slug: str
    category: str = "unknown"
    description: str = ""
    status: str = "active"
    installed_date: Optional[str] = None


class TaskSubmit(BaseModel):
    task_type: str = Field(..., description="chat | install | report | health")
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    timeout_sec: float = Field(default=60.0, gt=0)


class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending | running | done | failed
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    submitted_at: float = 0.0


class HealthResponse(BaseModel):
    status: str
    uptime_sec: float
    total_skills: int
    active_tasks: int
    python_version: str
    timestamp: float


# ── 全局状态 ────────────────────────────────────
SKILLS_DIR = Path("/Users/fhjtech/.openclaw/workspace/skills")
SKILLS_DB = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
START_TIME = time.time()

_tasks: dict[str, TaskStatus] = {}
_console = rich.console.Console()


# ── FastAPI App ─────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    _console.print("[green]🚀 Harvey API Server started[/green]")
    yield
    _console.print("[red]👋 Harvey API Server stopped[/red]")


app = FastAPI(
    title="Harvey AI API",
    description="Harvey 助手自动化任务 HTTP 接口",
    version="1.0.0",
    lifespan=lifespan,
)


# ── API 路由 ────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    """Web UI 入口"""
    return """
    <html><head><title>Harvey API</title></head>
    <body><h1>🤖 Harvey AI API</h1>
    <p><a href="/docs">📖 API 文档</a></p>
    <p><a href="/health">💚 健康检查</a></p>
    <p><a href="/skills">📦 技能列表</a></p>
    </body></html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    try:
        total = len(list(SKILLS_DIR.iterdir())) if SKILLS_DIR.exists() else 0
    except:
        total = 0
    return HealthResponse(
        status="healthy",
        uptime_sec=time.time() - START_TIME,
        total_skills=total,
        active_tasks=sum(1 for t in _tasks.values() if t.status == "running"),
        python_version="3.12+",
        timestamp=time.time(),
    )


@app.get("/skills", response_model=list[SkillInfo])
async def list_skills(
    category: Optional[str] = Query(None, description="按类别过滤"),
    limit: int = Query(50, ge=1, le=500),
):
    """列出所有已安装技能"""
    try:
        with open(SKILLS_DB) as f:
            import json
            data = json.load(f)
    except:
        return []

    skills = []
    for slug, info in data.get("skills", {}).items():
        if category and info.get("category") != category:
            continue
        skills.append(SkillInfo(
            slug=slug,
            category=info.get("category", "unknown"),
            description=info.get("description", ""),
            status=info.get("status", "active"),
            installed_date=info.get("installed_date"),
        ))
    return skills[:limit]


@app.post("/tasks/submit", response_model=TaskStatus)
async def submit_task(task: TaskSubmit):
    """提交任务"""
    import uuid
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    _tasks[task_id] = TaskStatus(
        task_id=task_id,
        status="pending",
        submitted_at=time.time(),
    )
    # 后台执行
    asyncio.create_task(_run_task(task_id, task))
    return _tasks[task_id]


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task(task_id: str):
    """查询任务状态"""
    if task_id not in _tasks:
        raise HTTPException(404, f"Task not found: {task_id}")
    return _tasks[task_id]


@app.get("/tasks", response_model=list[TaskStatus])
async def list_tasks(running_only: bool = False):
    """列出所有任务"""
    tasks = list(_tasks.values())
    if running_only:
        tasks = [t for t in tasks if t.status == "running"]
    return sorted(tasks, key=lambda t: t.submitted_at, reverse=True)[:100]


async def _run_task(task_id: str, task: TaskSubmit) -> None:
    """后台执行任务"""
    _tasks[task_id].status = "running"
    start = time.monotonic()

    try:
        if task.task_type == "chat":
            from .minimax_client import chat
            prompt = task.payload.get("prompt", "")
            result = chat(prompt)
            _tasks[task_id].result = result

        elif task.task_type == "report":
            from .daily_skills_summary import generate_report, get_new_skills
            new_skills = get_new_skills()
            total = len(list(SKILLS_DIR.iterdir())) if SKILLS_DIR.exists() else 0
            report = generate_report(new_skills, total)
            _tasks[task_id].result = {"report_size": len(report), "skills_count": len(new_skills)}

        elif task.task_type == "health":
            _tasks[task_id].result = {"status": "ok", "tasks": len(_tasks)}

        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

        _tasks[task_id].status = "done"

    except Exception as e:
        _tasks[task_id].status = "failed"
        _tasks[task_id].error = f"{type(e).__name__}: {e}"

    _tasks[task_id].duration_ms = (time.monotonic() - start) * 1000


# ── 启动入口 ────────────────────────────────────
def run(host: str = "0.0.0.0", port: int = 18790):
    """启动 Harvey API 服务器"""
    _console.print(f"[cyan]Starting Harvey API on {host}:{port}[/cyan]")
    uvicorn.run(
        "harvey_api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    run()
