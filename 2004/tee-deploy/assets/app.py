"""
Starchild TEE Agent — single-file FastAPI runtime.

Runs inside a Phala Cloud CVM (Intel TDX).
Exposes a minimal but real agent loop:
  - LLM chat (OpenAI-compatible, supports tool calling)
  - Built-in tools: web_fetch, web_search, workspace file ops
  - Attestation via dstack guest agent unix socket
  - Streaming via SSE

This file is embedded in the docker-compose entrypoint (base64) so that the
compose hash captures the exact agent code → attested by Intel TDX quote.
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import socket
import time
import urllib.parse
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ───────────── Config ─────────────
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "near_ai")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "")
LLM_BASE_URL = (os.environ.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", "/data/workspace"))
WORKSPACE.mkdir(parents=True, exist_ok=True)
DSTACK_SOCK = os.environ.get("DSTACK_SOCK", "/var/run/dstack.sock")
AGENT_VERSION = "0.2.0"
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are Starchild-TEE, an AI agent running inside an Intel TDX confidential VM. "
    "You can call tools to fetch web pages, search the web, and read/write files in "
    "your private workspace. Be concise and accurate. Cite sources when you use web tools."
)

# ───────────── App ─────────────
app = FastAPI(title="Starchild TEE Agent", version=AGENT_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ───────────── Attestation (dstack guest agent) ─────────────
async def _dstack_request(method: str, path: str, body: dict | None = None) -> dict:
    """Call the dstack guest agent over its unix socket."""
    if not os.path.exists(DSTACK_SOCK):
        raise RuntimeError(f"dstack socket not found at {DSTACK_SOCK}")
    transport = httpx.AsyncHTTPTransport(uds=DSTACK_SOCK)
    async with httpx.AsyncClient(transport=transport, base_url="http://dstack", timeout=30) as client:
        if method == "GET":
            r = await client.get(path)
        else:
            r = await client.post(path, json=body or {})
        r.raise_for_status()
        return r.json()


async def get_info() -> dict:
    try:
        return await _dstack_request("GET", "/Info")
    except Exception as e:
        return {"available": False, "reason": str(e)}


async def get_quote(report_data: bytes = b"") -> dict:
    """Get a TDX attestation quote. report_data is bound into the quote so the
    caller can prove freshness / bind it to a specific challenge."""
    rd = report_data.ljust(64, b"\x00")[:64]
    try:
        resp = await _dstack_request("POST", "/GetQuote", {"report_data": rd.hex()})
        return {"available": True, "quote": resp.get("quote"), "event_log": resp.get("event_log"), "report_data_hex": rd.hex()}
    except Exception as e:
        return {"available": False, "reason": str(e), "report_data_hex": rd.hex()}


# ───────────── Workspace tools ─────────────
def _safe_path(rel: str) -> Path:
    """Resolve a user-supplied path within WORKSPACE only (no traversal)."""
    p = (WORKSPACE / rel.lstrip("/")).resolve()
    if not str(p).startswith(str(WORKSPACE.resolve())):
        raise HTTPException(400, "path escapes workspace")
    return p


async def tool_workspace_list(path: str = ".") -> dict:
    p = _safe_path(path)
    if not p.exists():
        return {"path": path, "exists": False, "entries": []}
    if p.is_file():
        return {"path": path, "is_file": True, "size": p.stat().st_size}
    entries = []
    for e in sorted(p.iterdir()):
        entries.append({"name": e.name, "is_dir": e.is_dir(), "size": e.stat().st_size if e.is_file() else None})
    return {"path": path, "exists": True, "entries": entries}


async def tool_workspace_read(path: str, max_bytes: int = 64_000) -> dict:
    p = _safe_path(path)
    if not p.exists() or not p.is_file():
        raise HTTPException(404, f"not a file: {path}")
    raw = p.read_bytes()[:max_bytes]
    try:
        return {"path": path, "content": raw.decode("utf-8"), "encoding": "utf-8", "size": p.stat().st_size}
    except UnicodeDecodeError:
        return {"path": path, "content_b64": base64.b64encode(raw).decode(), "encoding": "base64", "size": p.stat().st_size}


async def tool_workspace_write(path: str, content: str, mode: str = "overwrite") -> dict:
    p = _safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if mode == "append":
        with open(p, "a") as f:
            f.write(content)
    else:
        p.write_text(content)
    return {"path": path, "bytes_written": len(content.encode()), "mode": mode}


# ───────────── Web tools ─────────────
async def tool_web_fetch(url: str, max_chars: int = 20_000) -> dict:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "StarchildTEE/0.2"}) as client:
        r = await client.get(url)
        text = r.text
        # naive HTML→text
        text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return {"url": str(r.url), "status": r.status_code, "content": text[:max_chars], "truncated": len(text) > max_chars}


async def tool_web_search(query: str, max_results: int = 5) -> dict:
    """Use DuckDuckGo HTML endpoint (no API key needed)."""
    q = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={q}"
    async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 StarchildTEE/0.2"}) as client:
        r = await client.get(url)
    html = r.text
    results = []
    for m in re.finditer(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, flags=re.S):
        href, title, snip = m.group(1), m.group(2), m.group(3)
        title = re.sub(r"<[^>]+>", "", title).strip()
        snip = re.sub(r"<[^>]+>", "", snip).strip()
        # decode ddg redirect
        if href.startswith("//duckduckgo.com/l/?uddg="):
            try:
                href = urllib.parse.unquote(href.split("uddg=", 1)[1].split("&", 1)[0])
            except Exception:
                pass
        results.append({"title": title, "url": href, "snippet": snip})
        if len(results) >= max_results:
            break
    return {"query": query, "results": results}


# ───────────── Tool registry (OpenAI function-calling spec) ─────────────
TOOL_SCHEMAS: list[dict] = [
    {"type": "function", "function": {
        "name": "web_fetch",
        "description": "Fetch a URL and return its text content (HTML stripped).",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "Absolute http(s) URL"},
            "max_chars": {"type": "integer", "default": 20000}
        }, "required": ["url"]}
    }},
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the web with DuckDuckGo and return top results (title/url/snippet).",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer", "default": 5}
        }, "required": ["query"]}
    }},
    {"type": "function", "function": {
        "name": "workspace_list",
        "description": "List files in the agent's private workspace.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string", "default": "."}}}
    }},
    {"type": "function", "function": {
        "name": "workspace_read",
        "description": "Read a file from the agent's private workspace.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
    }},
    {"type": "function", "function": {
        "name": "workspace_write",
        "description": "Write a file in the agent's private workspace (default: overwrite).",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "mode": {"type": "string", "enum": ["overwrite", "append"], "default": "overwrite"}
        }, "required": ["path", "content"]}
    }},
]

TOOL_FUNCS: dict[str, Any] = {
    "web_fetch": tool_web_fetch,
    "web_search": tool_web_search,
    "workspace_list": tool_workspace_list,
    "workspace_read": tool_workspace_read,
    "workspace_write": tool_workspace_write,
}


async def invoke_tool(name: str, args: dict) -> Any:
    fn = TOOL_FUNCS.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    try:
        return await fn(**args)
    except HTTPException as e:
        return {"error": e.detail, "status": e.status_code}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ───────────── LLM client ─────────────
async def llm_call(messages: list[dict], tools: list[dict] | None = None, stream: bool = False, max_tokens: int = 1024) -> dict | AsyncIterator[bytes]:
    payload: dict[str, Any] = {"model": LLM_MODEL, "messages": messages, "max_tokens": max_tokens}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    if stream:
        payload["stream"] = True

    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    url = f"{LLM_BASE_URL}/chat/completions"

    if not stream:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()

    async def gen() -> AsyncIterator[bytes]:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as r:
                r.raise_for_status()
                async for line in r.aiter_lines():
                    if line.strip():
                        yield (line + "\n").encode()
    return gen()


# ───────────── Agent loop ─────────────
class ChatReq(BaseModel):
    prompt: str
    history: list[dict] | None = None
    use_tools: bool = True
    max_iterations: int = 6
    include_attestation: bool = True
    nonce: str | None = None  # client challenge bound into attestation
    max_tokens: int = 1024


async def agent_loop(req: ChatReq) -> dict:
    msgs: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if req.history:
        msgs.extend(req.history)
    msgs.append({"role": "user", "content": req.prompt})

    tool_trace: list[dict] = []
    tools = TOOL_SCHEMAS if req.use_tools else None

    for iteration in range(req.max_iterations):
        resp = await llm_call(msgs, tools=tools, max_tokens=req.max_tokens)
        choice = resp["choices"][0]
        msg = choice["message"]

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            # Final answer
            final_content = msg.get("content") or ""
            result = {
                "reply": final_content,
                "iterations": iteration + 1,
                "tool_trace": tool_trace,
                "model": LLM_MODEL,
                "usage": resp.get("usage", {}),
            }
            if req.include_attestation:
                # Bind reply hash + optional nonce into attestation
                binding = hashlib.sha256(
                    (final_content + "|" + (req.nonce or "")).encode()
                ).digest()
                result["attestation"] = await get_quote(binding)
            return result

        # Append assistant turn with tool_calls, then execute them
        msgs.append(msg)
        for tc in tool_calls:
            fn = tc["function"]
            name = fn["name"]
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            result = await invoke_tool(name, args)
            tool_trace.append({"name": name, "args": args, "result_preview": str(result)[:300]})
            msgs.append({
                "role": "tool",
                "tool_call_id": tc.get("id", f"call_{iteration}"),
                "name": name,
                "content": json.dumps(result, ensure_ascii=False)[:8000],
            })

    return {"reply": "[max iterations reached]", "iterations": req.max_iterations, "tool_trace": tool_trace}


# ───────────── HTTP endpoints ─────────────
START_TS = time.time()


@app.get("/")
async def root():
    return {
        "service": "Starchild TEE Agent",
        "version": AGENT_VERSION,
        "uptime_sec": int(time.time() - START_TS),
        "endpoints": ["/health", "/info", "/chat", "/chat/stream", "/attestation", "/workspace/list", "/workspace/read", "/workspace/write", "/tools", "/tool/invoke"],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": AGENT_VERSION, "llm_configured": bool(LLM_API_KEY)}


@app.get("/info")
async def info():
    """TEE environment info from dstack."""
    return {"agent": {"version": AGENT_VERSION, "uptime_sec": int(time.time() - START_TS)}, "dstack": await get_info()}


@app.get("/attestation")
async def attestation(nonce: str = ""):
    rd = hashlib.sha256(nonce.encode()).digest() if nonce else b""
    return await get_quote(rd)


@app.post("/chat")
async def chat(req: ChatReq):
    if not LLM_API_KEY:
        raise HTTPException(500, "LLM_API_KEY not configured")
    return await agent_loop(req)


@app.post("/chat/stream")
async def chat_stream(req: ChatReq):
    """SSE stream of agent events (delta tokens + tool calls + final attestation)."""
    if not LLM_API_KEY:
        raise HTTPException(500, "LLM_API_KEY not configured")

    async def event_gen() -> AsyncIterator[bytes]:
        msgs: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if req.history:
            msgs.extend(req.history)
        msgs.append({"role": "user", "content": req.prompt})
        tools = TOOL_SCHEMAS if req.use_tools else None

        for iteration in range(req.max_iterations):
            # Non-streaming inside the loop (simpler); stream final reply only.
            is_final_chance = iteration == req.max_iterations - 1
            resp = await llm_call(msgs, tools=tools, stream=False, max_tokens=req.max_tokens)
            msg = resp["choices"][0]["message"]
            tool_calls = msg.get("tool_calls") or []

            if not tool_calls:
                content = msg.get("content") or ""
                # stream the content as deltas (chunked)
                for i in range(0, len(content), 40):
                    chunk = content[i:i+40]
                    yield f"data: {json.dumps({'type':'delta','content':chunk})}\n\n".encode()
                    await asyncio.sleep(0.01)
                if req.include_attestation:
                    binding = hashlib.sha256((content + "|" + (req.nonce or "")).encode()).digest()
                    quote = await get_quote(binding)
                    yield f"data: {json.dumps({'type':'attestation','quote':quote})}\n\n".encode()
                yield f"data: {json.dumps({'type':'done','usage':resp.get('usage', {})})}\n\n".encode()
                return

            yield f"data: {json.dumps({'type':'tool_calls','calls':[{'name':tc['function']['name']} for tc in tool_calls]})}\n\n".encode()
            msgs.append(msg)
            for tc in tool_calls:
                fn = tc["function"]
                name = fn["name"]
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = await invoke_tool(name, args)
                yield f"data: {json.dumps({'type':'tool_result','name':name,'preview':str(result)[:200]})}\n\n".encode()
                msgs.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", f"call_{iteration}"),
                    "name": name,
                    "content": json.dumps(result, ensure_ascii=False)[:8000],
                })

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.get("/tools")
async def tools():
    return {"tools": TOOL_SCHEMAS}


class ToolInvokeReq(BaseModel):
    name: str
    args: dict = {}


@app.post("/tool/invoke")
async def tool_invoke(req: ToolInvokeReq):
    return {"name": req.name, "result": await invoke_tool(req.name, req.args)}


@app.get("/workspace/list")
async def ws_list(path: str = "."):
    return await tool_workspace_list(path)


@app.get("/workspace/read")
async def ws_read(path: str, max_bytes: int = 64_000):
    return await tool_workspace_read(path, max_bytes)


class WriteReq(BaseModel):
    path: str
    content: str
    mode: str = "overwrite"


@app.post("/workspace/write")
async def ws_write(req: WriteReq):
    return await tool_workspace_write(req.path, req.content, req.mode)
