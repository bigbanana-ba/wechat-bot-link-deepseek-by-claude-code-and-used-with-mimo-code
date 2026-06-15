#!/usr/bin/env python3
"""
MiMo MCP Server — 通过 MCP 协议提供 MiMo 模型调用能力。
当前使用 mimo run CLI（免费），未来可切换为 API 调用。
"""

import sys
import json
import subprocess
import os

# MiMo CLI 路径
MIMO_BIN = os.environ.get(
    "MIMO_BIN",
    r"C:\Users\big\AppData\Roaming\npm\node_modules\@mimo-ai\cli\node_modules\@mimo-ai\mimocode-windows-x64\bin\mimo.exe"
)

# 切换模式: "cli" = mimo run (免费), "api" = MiMo API (需 key)
MIMO_MODE = os.environ.get("MIMO_MODE", "cli")

# ========== API 模式配置（未来使用） ==========
# MIMO_API_KEY = os.environ.get("MIMO_API_KEY", "")
# MIMO_API_URL = os.environ.get("MIMO_API_URL", "https://api.xiaomimimo.com/v1/chat/completions")
# MIMO_API_MODEL = os.environ.get("MIMO_API_MODEL", "mimo-auto")


def mimo_chat_via_cli(message, model="mimo/mimo-auto", timeout=60):
    """通过 mimo run CLI 调用 MiMo"""
    cmd = [MIMO_BIN, "run", message, "--format", "json", "--model", model]
    env = {**os.environ, "PYTHONUTF8": "1"}
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            encoding="utf-8", errors="replace", env=env
        )
        reply_parts = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                if event.get("type") == "text":
                    reply_parts.append(event["part"]["text"])
            except (json.JSONDecodeError, KeyError):
                continue
        return "".join(reply_parts) if reply_parts else "[MiMo 无响应]"
    except subprocess.TimeoutExpired:
        return "[错误] MiMo 调用超时"
    except Exception as e:
        return f"[错误] {str(e)[:200]}"


# def mimo_chat_via_api(message, model="mimo-auto", timeout=60):
#     """通过 MiMo API 调用（未来方案，取消注释并配置 key 即可使用）"""
#     import urllib.request
#     payload = json.dumps({
#         "model": model,
#         "messages": [{"role": "user", "content": message}],
#         "max_tokens": 4096,
#         "temperature": 0.7,
#     }).encode("utf-8")
#     req = urllib.request.Request(
#         MIMO_API_URL,
#         data=payload,
#         headers={
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {MIMO_API_KEY}",
#         },
#     )
#     try:
#         with urllib.request.urlopen(req, timeout=timeout) as resp:
#             data = json.loads(resp.read().decode("utf-8"))
#             return data["choices"][0]["message"]["content"]
#     except Exception as e:
#         return f"[错误] {str(e)[:200]}"


def mimo_chat(message, model="mimo/mimo-auto"):
    """统一入口，根据 MIMO_MODE 选择实现"""
    if MIMO_MODE == "api":
        # return mimo_chat_via_api(message, model)
        return "[错误] API 模式尚未配置，请设置 MIMO_API_KEY 环境变量"
    return mimo_chat_via_cli(message, model)


# ========== MCP 协议实现 ==========

TOOLS = [
    {
        "name": "mimo_chat",
        "description": "调用小米 MiMo 模型回答问题。支持数学推理、代码生成、创意写作等任务。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "用户的问题或指令"
                },
                "model": {
                    "type": "string",
                    "description": "模型 ID，可选值: mimo/mimo-auto, xiaomi/mimo-v2-flash, xiaomi/mimo-v2.5-pro",
                    "default": "mimo/mimo-auto"
                }
            },
            "required": ["message"]
        }
    }
]


def send_response(response):
    """发送 JSON-RPC 响应到 stdout"""
    line = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def handle_request(msg):
    """处理 JSON-RPC 请求"""
    method = msg.get("method", "")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mimo-mcp", "version": "1.0.0"}
            }
        })

    elif method == "notifications/initialized":
        pass  # 通知，无需响应

    elif method == "tools/list":
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": TOOLS}
        })

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "mimo_chat":
            message = arguments.get("message", "")
            model = arguments.get("model", "mimo/mimo-auto")
            result_text = mimo_chat(message, model)
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": result_text}]
                }
            })
        else:
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
            })

    elif msg_id is not None:
        send_response({
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"}
        })


def main():
    """MCP stdio 主循环"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            handle_request(msg)
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    main()
