# Harvey AI Assistant - Production Docker Environment
# Harvey 的 Python 进化基础设施

# ── 使用国内镜像加速 ────────────────────────────────
# python:3.12-slim-bookworm (国内可用镜像)
FROM docker.m.daocloud.io/library/python:3.12-slim-bookworm

# ── 系统依赖 ────────────────────────────────────────
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    git curl wget vim \
    && rm -rf /var/lib/apt/lists/*

# ── 工作目录 ────────────────────────────────────────
WORKDIR /workspace

# ── Python 依赖 ──────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── SkillHub CLI ─────────────────────────────────────
RUN curl -fsSL https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh | bash -s -- --cli-only && \
    mv /root/.local/bin/skillhub /usr/local/bin/skillhub

# ── OpenClaw workspace ───────────────────────────────
COPY . /workspace/

# ── 验证 ────────────────────────────────────────────
RUN python3 --version && \
    mypy --version && \
    pytest --version && \
    skillhub --version

# ── 入口点 ──────────────────────────────────────────
ENTRYPOINT ["/bin/bash", "-c"]
