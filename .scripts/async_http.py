#!/usr/bin/env python3
"""
异步 HTTP 客户端 - H7 产出物
基于 httpx，支持重试、超时、自动跟随重定向
"""

import asyncio
import httpx
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class HTTPResult:
    status: int
    body: str
    headers: dict
    elapsed_ms: float
    success: bool


class AsyncHTTPClient:
    """
    asyncio HTTP 客户端
    特性：重试机制、超时控制、自动 JSON 解析、连接复用
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout_sec: float = 30.0,
        max_connections: int = 20,
    ) -> None:
        self._max_retries = max_retries
        self._timeout = httpx.Timeout(timeout_sec, connect=5.0)
        self._limits = httpx.Limits(max_connections=max_connections)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncHTTPClient":
        self._client = httpx.AsyncClient(
            timeout=self._timeout,
            limits=self._limits,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()

    async def get(self, url: str, headers: Optional[dict] = None) -> HTTPResult:
        return await self._do("GET", url, headers=headers)

    async def post(
        self, url: str, data: Optional[dict] = None, json: Optional[dict] = None
    ) -> HTTPResult:
        return await self._do("POST", url, data=data, json=json)

    async def _do(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> HTTPResult:
        if not self._client:
            raise RuntimeError("Use 'async with AsyncHTTPClient() as client:'")

        last_error = ""
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await self._client.request(
                    method, url, headers=headers, data=data, json=json
                )
                elapsed_ms = response.elapsed.total_seconds() * 1000
                body = response.text
                return HTTPResult(
                    status=response.status_code,
                    body=body,
                    headers=dict(response.headers),
                    elapsed_ms=elapsed_ms,
                    success=response.status_code < 400,
                )
            except httpx.TimeoutException:
                last_error = f"Timeout on attempt {attempt}/{self._max_retries}"
                if attempt == self._max_retries:
                    return HTTPResult(
                        status=0, body=last_error, headers={}, elapsed_ms=0, success=False
                    )
                await asyncio.sleep(2 ** attempt * 0.5)
            except httpx.HTTPError as e:
                last_error = str(e)
                if attempt == self._max_retries:
                    return HTTPResult(
                        status=0, body=last_error, headers={}, elapsed_ms=0, success=False
                    )
                await asyncio.sleep(attempt * 0.5)

        return HTTPResult(
            status=0, body=last_error, headers={}, elapsed_ms=0, success=False
        )


# ── Benchmark ────────────────────────────────────
async def benchmark_http():
    """对比串行 vs 并发 HTTP 请求性能"""
    import time

    urls = [
        "https://api.github.com",
        "https://httpbin.org/get",
        "https://httpbin.org/ip",
        "https://api.github.com/users",
    ] * 5  # 20 个请求

    print("\n⚡ Benchmark: HTTP 并发 vs 串行")
    print(f"请求数: {len(urls)}")

    # 串行
    async with AsyncHTTPClient(max_connections=1) as client:
        t0 = time.monotonic()
        results = []
        for url in urls:
            r = await client.get(url)
            results.append(r)
        serial_time = time.monotonic() - t0

    ok_serial = sum(1 for r in results if r.success)
    print(f"串行: {serial_time:.2f}s, 成功: {ok_serial}/{len(results)}")

    # 并发
    async with AsyncHTTPClient(max_connections=20) as client:
        t0 = time.monotonic()
        tasks = [client.get(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_time = time.monotonic() - t0

    ok_concurrent = sum(1 for r in results if isinstance(r, HTTPResult) and r.success)
    print(f"并发: {concurrent_time:.2f}s, 成功: {ok_concurrent}/{len(urls)}")
    print(f"提升: {serial_time/concurrent_time:.1f}x")

    return serial_time, concurrent_time


if __name__ == "__main__":
    asyncio.run(benchmark_http())
