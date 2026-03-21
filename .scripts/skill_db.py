#!/usr/bin/env python3
"""
Harvey 技能追踪系统 - SQLAlchemy ORM 生产级实战
H7-FastAPI 延伸：Skill 数据库持久化管理
用途：记录技能安装历史、使用次数、分类、状态
"""

import asyncio
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

from sqlalchemy import (
    create_engine, select, update, delete,
    func, and_, or_,
    String, Integer, Float, Boolean, DateTime, JSON, Text,
    Index,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, Session,
    sessionmaker, relationship,
)
from sqlalchemy.dialects.sqlite import insert
from pydantic import BaseModel, Field
import rich.console, rich.table

TZ_CST = timezone(timedelta(hours=8))
DB_PATH = Path("/Users/fhjtech/.openclaw/workspace/.learnings/harvey_skills.db")
_engine = None
_SessionLocal = None


# ══════════════════════════════════════════════
# ORM Model
# ══════════════════════════════════════════════
class Base(DeclarativeBase):
    pass


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")  # active | disabled | uninstalled
    installed_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    use_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    avg_duration_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tags: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # JSON list
    extra_data: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)  # JSON dict (renamed from metadata)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    safety_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)  # 0-1
    integrated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(TZ_CST)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(TZ_CST),
        onupdate=lambda: datetime.now(TZ_CST)
    )

    __table_args__ = (
        Index("idx_category_status", "category", "status"),
        Index("idx_slug", "slug"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "slug": self.slug,
            "category": self.category,
            "description": self.description,
            "status": self.status,
            "installed_date": self.installed_date,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
            "avg_duration_ms": self.avg_duration_ms,
            "tags": self.tags,
            "extra_data": self.extra_data,
            "version": self.version,
            "safety_score": self.safety_score,
            "integrated": self.integrated,
        }


# ══════════════════════════════════════════════
# Database Manager
# ══════════════════════════════════════════════
def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{DB_PATH}",
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
        )
        Base.metadata.create_all(_engine)
        _SessionLocal = sessionmaker(bind=_engine)
    return _engine, _SessionLocal


def get_session() -> Session:
    _, SessionLocal = get_engine()
    return SessionLocal()


# ══════════════════════════════════════════════
# Skill CRUD Operations
# ══════════════════════════════════════════════
class SkillRepo:
    """技能仓库（Repository 模式）"""

    def __init__(self, session: Session):
        self._s = session

    def upsert(self, slug: str, **kwargs) -> Skill:
        """插入或更新"""
        skill = self._s.query(Skill).filter_by(slug=slug).first()
        if skill:
            for k, v in kwargs.items():
                if hasattr(skill, k) and v is not None:
                    setattr(skill, k, v)
            skill.updated_at = datetime.now(TZ_CST)
        else:
            skill = Skill(slug=slug, **kwargs)
            self._s.add(skill)
        self._s.commit()
        self._s.refresh(skill)
        return skill

    def get_by_slug(self, slug: str) -> Optional[Skill]:
        return self._s.query(Skill).filter_by(slug=slug).first()

    def get_all(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> list[Skill]:
        q = self._s.query(Skill)
        if category:
            q = q.filter_by(category=category)
        if status:
            q = q.filter_by(status=status)
        return q.order_by(Skill.use_count.desc()).limit(limit).all()

    def record_usage(self, slug: str, duration_ms: float) -> None:
        """记录技能使用，更新统计"""
        skill = self.get_by_slug(slug)
        if not skill:
            return
        skill.use_count += 1
        skill.last_used = datetime.now(TZ_CST)
        # 滑动平均更新 avg_duration
        n = skill.use_count
        skill.avg_duration_ms = (skill.avg_duration_ms * (n - 1) + duration_ms) / n
        skill.updated_at = datetime.now(TZ_CST)
        self._s.commit()

    def get_top_used(self, n: int = 10) -> list[Skill]:
        return self._s.query(Skill).order_by(Skill.use_count.desc()).limit(n).all()

    def get_stats(self) -> dict:
        """全局统计"""
        stats = self._s.query(
            func.count(Skill.id).label("total"),
            func.sum(Skill.use_count).label("total_uses"),
            func.avg(Skill.safety_score).label("avg_safety"),
        ).first()
        by_category = self._s.query(
            Skill.category, func.count(Skill.id)
        ).group_by(Skill.category).all()
        by_status = self._s.query(
            Skill.status, func.count(Skill.id)
        ).group_by(Skill.status).all()
        return {
            "total_skills": stats.total or 0,
            "total_uses": stats.total_uses or 0,
            "avg_safety": round(stats.avg_safety or 1.0, 3),
            "by_category": {k: v for k, v in by_category},
            "by_status": {k: v for k, v in by_status},
        }


# ══════════════════════════════════════════════
# 从现有 skills_usage.json 迁移到 SQLAlchemy
# ══════════════════════════════════════════════
def migrate_from_json():
    """一次性迁移：将旧的 JSON 数据迁移到 SQLAlchemy"""
    json_path = Path("/Users/fhjtech/.openclaw/workspace/.learnings/skills_usage.json")
    if not json_path.exists():
        print("No skills_usage.json found, skipping migration")
        return

    import json
    with open(json_path) as f:
        data = json.load(f)

    session = get_session()
    repo = SkillRepo(session)
    migrated = 0
    for slug, info in data.get("skills", {}).items():
        repo.upsert(
            slug=slug,
            category=info.get("category", "unknown"),
            description=info.get("description", ""),
            status=info.get("status", "active"),
            installed_date=info.get("installed_date"),
            version=info.get("version"),
            safety_score=info.get("safety_score", 1.0),
            integrated=info.get("status") == "auto-installed",
        )
        migrated += 1

    session.close()
    print(f"✅ Migrated {migrated} skills to SQLAlchemy")
    return migrated


# ══════════════════════════════════════════════
# Pydantic 模型（API 用）
# ══════════════════════════════════════════════
class SkillCreate(BaseModel):
    slug: str
    category: str = "unknown"
    description: str = ""
    version: Optional[str] = None


class SkillUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None


# ══════════════════════════════════════════════
# Demo / Report
# ══════════════════════════════════════════════
def print_stats_report():
    session = get_session()
    repo = SkillRepo(session)
    stats = repo.get_stats()
    top = repo.get_top_used(10)

    c = rich.console.Console()
    c.print("\n[bold cyan]📊 Harvey Skills DB Report[/bold cyan]")
    st = rich.table.Table(show_header=True)
    st.add_column("指标", style="green")
    st.add_column("数值", justify="right")
    st.add_row("总技能数", str(stats["total_skills"]))
    st.add_row("总使用次数", str(stats["total_uses"]))
    st.add_row("平均安全分", f"{stats['avg_safety']:.3f}")
    c.print(st)

    if top:
        c.print("\n[bold]🏆 Top 10 使用技能[/bold]")
        tt = rich.table.Table(show_header=True)
        tt.add_column("技能", style="cyan")
        tt.add_column("使用次数", justify="right")
        tt.add_column("平均耗时", justify="right")
        tt.add_column("分类", style="yellow")
        for s in top:
            tt.add_row(s.slug, str(s.use_count), f"{s.avg_duration_ms:.0f}ms", s.category)
        c.print(tt)
    session.close()


if __name__ == "__main__":
    migrate_from_json()
    print_stats_report()
