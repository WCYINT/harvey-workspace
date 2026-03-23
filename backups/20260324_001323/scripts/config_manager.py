#!/usr/bin/env python3
"""
统一配置管理 - H6 产出物
使用 pydantic 做配置验证，rich 美化输出
"""

from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional


class FeishuConfig(BaseModel):
    app_id: str = Field(description="飞书应用 ID")
    app_secret: str = Field(description="飞书应用密钥")
    user_open_id: str = Field(description="James 的 Open ID")


class MiniMaxConfig(BaseModel):
    api_key: str = Field(description="MiniMax API Key")
    model: str = Field(default="MiniMax-M2.7")
    base_url: str = Field(default="https://api.minimaxi.com")
    max_tokens: int = Field(default=2048, ge=1, le=32000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class SchedulerConfig(BaseModel):
    max_concurrency: int = Field(default=20, ge=1, le=200)
    default_timeout_sec: float = Field(default=60.0, gt=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay_sec: float = Field(default=1.0, ge=0)


class SkillHubConfig(BaseModel):
    cmd: str = Field(default="/Users/fhjtech/.local/bin/skillhub")
    categories: list[str] = Field(default_factory=lambda: [
        "agent", "ai", "coding", "data", "writing", "communication", "security"
    ])
    max_install_per_run: int = Field(default=100, ge=1)


class Config(BaseModel):
    """全局配置（所有字段由 pydantic 验证）"""
    feishu: FeishuConfig
    minimax: MiniMaxConfig
    scheduler: SchedulerConfig = Field(default_factory=SchedulerConfig)
    skillhub: SkillHubConfig = Field(default_factory=SkillHubConfig)
    log_level: str = Field(default="INFO")


def load_config(config_path: str | Path = "/Users/fhjtech/.openclaw/workspace/.config.json") -> Config:
    """从 JSON 文件加载并验证配置"""
    import json, sys
    try:
        data = json.loads(Path(config_path).read_text())
    except FileNotFoundError:
        print(f"[Config] {config_path} not found, using defaults")
        # 用环境变量或默认值填充
        data = _default_config_data()

    try:
        return Config.model_validate(data)
    except Exception as e:
        print(f"[Config] Validation error: {e}")
        sys.exit(1)


def _default_config_data() -> dict:
    """从环境/已知凭证构建默认配置"""
    import json
    with open("/Users/fhjtech/.openclaw/openclaw.json") as f:
        openclaw = json.load(f)

    feishu_cfg = openclaw["channels"]["feishu"]["accounts"]["default"]
    minimax_cfg = openclaw["agents"]["main"]["agent"]["models.json"]  # placeholder

    return {
        "feishu": {
            "app_id": feishu_cfg["appId"],
            "app_secret": feishu_cfg["appSecret"],
            "user_open_id": "ou_7bc224841d2a1064cf5a7fbf67824227",
        },
        "minimax": {
            "api_key": "sk-cp-dqbbK2L9amD_oI6KJPIpPOitKtgbvpQqEcKIh58MV_aKRHAfGXDshr7bavfxkr0Q229FoYVHrRrSJtQV50U-mTfVQQFWk03oPwFGEvPzCxstbXlytd5E8sc",
        },
        "scheduler": {
            "max_concurrency": 20,
            "default_timeout_sec": 60.0,
            "max_retries": 3,
        },
        "skillhub": {
            "max_install_per_run": 100,
        },
        "log_level": "INFO",
    }


if __name__ == "__main__":
    import rich.console, rich.table
    cfg = load_config()
    c = rich.console.Console()
    c.print("\n[bold cyan]⚙️  配置验证通过[/bold cyan]")
    t = rich.table.Table(show_header=False)
    t.add_column("项目", style="green")
    t.add_column("值")
    t.add_row("MiniMax 模型", cfg.minimax.model)
    t.add_row("并发上限", str(cfg.scheduler.max_concurrency))
    t.add_row("超时时间", f"{cfg.scheduler.default_timeout_sec}s")
    t.add_row("每日安装上限", str(cfg.skillhub.max_install_per_run))
    c.print(t)
    print("\n✅ H6 pydantic 配置验证 - 通过")
