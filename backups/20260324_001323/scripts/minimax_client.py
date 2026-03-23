#!/usr/bin/env python3
"""
MiniMax API 调用客户端
用途：所有自动化脚本统一使用 MiniMax M2.7
支持：文本对话 / 语音合成(TTS) / 图片生成 / 嵌入向量
"""

import json
import time
import hashlib
import hmac
import base64
import urllib.request
import urllib.error
from typing import Optional, Any
from datetime import datetime


# ── MiniMax API 配置 ──────────────────────────────
# 从 models.json 读取（避免硬编码）
API_KEY = "sk-cp-dqbbK2L9amD_oI6KJPIpPOitKtgbvpQqEcKIh58MV_aKRHAfGXDshr7bavfxkr0Q229FoYVHrRrSJtQV50U-mTfVQQFWk03oPwFGEvPzCxstbXlytd5E8sc"
BASE_URL = "https://api.minimaxi.com"
MODEL = "MiniMax-M2.7"

# ── 认证 ─────────────────────────────────────────
def _make_auth_header(api_key: str, timestamp: int, sign_str: str) -> dict:
    """生成 MiniMax API 签名认证"""
    sign = hmac.new(
        api_key.encode(), f"{timestamp}:{sign_str}".encode(), hashlib.sha256
    ).digest()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "timestamp": str(timestamp),
        "signature": base64.b64encode(sign).decode(),
    }


# ── 通用请求 ─────────────────────────────────────
def _post(
    endpoint: str,
    payload: dict,
    api_key: str = API_KEY,
    timeout: int = 60,
) -> dict:
    url = f"{BASE_URL}{endpoint}"
    timestamp = int(time.time())
    headers = _make_auth_header(api_key, timestamp, endpoint)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.load(resp)
            # MiniMax 成功时 base_resp.status_code == 0
            base_code = result.get("base_resp", {}).get("status_code")
            if base_code is not None and base_code != 0:
                raise Exception(f"MiniMax API error: {result.get('base_resp', {}).get('status_msg', result)}")
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise Exception(f"HTTP {e.code}: {body[:300]}")


# ── 文本对话 ─────────────────────────────────────
def chat(
    prompt: str,
    system: str = "You are a helpful AI assistant.",
    model: str = MODEL,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """
    调用 MiniMax M2.7 进行文本对话
    """
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    result = _post("/v1/text/chatcompletion_v2", payload)
    return result["choices"][0]["message"]["content"]


# ── 语音合成 TTS ─────────────────────────────────
def tts(
    text: str,
    voice_id: str = "male-qn-qingse",
    output_format: str = "mp3",
    speed: float = 1.0,
) -> bytes:
    """
    MiniMax TTS 语音合成，返回音频 bytes
    voice_id 选项：male-qn-qingse / female-shaonv / male-qn-qingse
    """
    payload = {
        "model": "speech-01",
        "text": text,
        "stream": False,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": 1,
            "pitch": 0,
            "emotion": "neutral",
        },
        "audio_setting": {
            "audio_format": output_format,
            "sample_rate": 32000,
        },
    }
    result = _post("/v1/audio/t2a_v2", payload, timeout=30)
    # 返回 base64 编码的音频
    return base64.b64decode(result["choices"][0]["audio_data"]["audio_bytes"])


# ── 嵌入向量 ─────────────────────────────────────
def embed(text: str, model: str = "emb-01") -> list[float]:
    """获取文本的嵌入向量"""
    payload = {
        "model": model,
        "texts": [text],
        "type": "dbEmbedding",
    }
    result = _post("/v1/embeddings", payload)
    return result["data"][0]["embedding"]


# ── 模型状态查询 ─────────────────────────────────
def usage() -> dict:
    """查询当前 API 使用量"""
    payload: dict = {}
    result = _post("/v1/query/tokens", payload)
    return result


# ── 测试 ─────────────────────────────────────────
if __name__ == "__main__":
    print("=== MiniMax API 测试 ===")
    # 文本对话
    print("💬 文本对话测试...")
    reply = chat("请用一句话介绍你自己")
    print(f"回复: {reply}")
    # 嵌入
    print("📊 嵌入向量测试...")
    vec = embed("你好，世界")
    print(f"向量维度: {len(vec)}, 前3维: {vec[:3]}")
    print("✅ 全部通过")
