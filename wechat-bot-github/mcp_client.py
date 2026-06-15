#!/usr/bin/env python3
"""
Minimal MCP (Model Context Protocol) client for fake-claude.py.
Connects to MCP servers via stdio and proxies tool calls.
"""

import subprocess
import json
import os
import sys
import threading
import time

class MCPClient:
    """Simple MCP stdio client for one server."""

    def __init__(self, name, command):
        self.name = name
        self.command = command  # list of args, e.g. ["uvx", "mcp-server-filesystem", "."]
        self.proc = None
        self.tools = []
        self.next_id = 1
        self._lock = threading.Lock()

    def start(self):
        """Launch the MCP server and initialize."""
        try:
            self.proc = subprocess.Popen(
                self.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            # Initialize
            init_resp = self._request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "fake-claude-mcp", "version": "1.0"},
            })
            if not init_resp:
                return False
            # Send initialized notification
            self._notify("notifications/initialized", {})
            # List tools
            tools_resp = self._request("tools/list", {})
            if tools_resp and "tools" in tools_resp:
                self.tools = tools_resp["tools"]
                sys.stderr.write(f"[MCP] {self.name}: {len(self.tools)} tools loaded\n")
                sys.stderr.flush()
                return True
            return False
        except Exception as e:
            sys.stderr.write(f"[MCP] {self.name} start failed: {e}\n")
            sys.stderr.flush()
            return False

    def _request(self, method, params):
        """Send a JSON-RPC request and wait for response."""
        with self._lock:
            req_id = self.next_id
            self.next_id += 1
            msg = json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
            try:
                self.proc.stdin.write(msg + "\n")
                self.proc.stdin.flush()
            except Exception as e:
                return None

            # Read response
            try:
                line = self.proc.stdout.readline()
                if line:
                    resp = json.loads(line)
                    if resp.get("id") == req_id:
                        return resp.get("result", {})
            except Exception:
                pass
            return None

    def _notify(self, method, params):
        """Send a JSON-RPC notification (no response expected)."""
        with self._lock:
            msg = json.dumps({"jsonrpc": "2.0", "method": method, "params": params})
            try:
                self.proc.stdin.write(msg + "\n")
                self.proc.stdin.flush()
            except Exception:
                pass

    def call_tool(self, tool_name, arguments):
        """Call an MCP tool and return the result."""
        result = self._request("tools/call", {
            "name": tool_name,
            "arguments": arguments,
        })
        if result and "content" in result:
            texts = []
            for c in result["content"]:
                if c.get("type") == "text":
                    texts.append(c["text"])
            return "\n".join(texts)
        return f"[MCP] Tool call failed: {result}"

    def stop(self):
        """Stop the MCP server."""
        if self.proc:
            try:
                self.proc.stdin.close()
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                pass


# Global MCP clients
_mcp_clients = []
_mcp_tool_map = {}  # tool_name -> (client, original_name)

def init_mcp(servers_config):
    """Start all MCP servers and collect their tools."""
    global _mcp_clients, _mcp_tool_map
    _mcp_clients = []
    _mcp_tool_map = {}

    for cfg in servers_config:
        client = MCPClient(cfg["name"], cfg["command"])
        if client.start():
            _mcp_clients.append(client)
            for tool in client.tools:
                mcp_name = f"mcp_{client.name}_{tool['name']}"
                _mcp_tool_map[mcp_name] = (client, tool["name"])

    tools_list = []
    for name, (client, orig_name) in _mcp_tool_map.items():
        for tool in client.tools:
            if tool["name"] == orig_name:
                tools_list.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": f"[MCP:{client.name}] {tool.get('description','')}",
                        "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                    }
                })
                break

    return tools_list


def call_mcp_tool(name, args):
    """Call an MCP tool by name."""
    if name in _mcp_tool_map:
        client, orig_name = _mcp_tool_map[name]
        return client.call_tool(orig_name, args)
    return f"[MCP] Unknown tool: {name}"


def stop_all_mcp():
    """Stop all MCP clients."""
    for client in _mcp_clients:
        client.stop()
    _mcp_clients.clear()
    _mcp_tool_map.clear()


# ============================================================
# 预置 MCP 服务器配置（用户可自行添加）
# ============================================================
MCP_SERVERS = [
    # MiMo MCP - 调用小米 MiMo 模型（免费，无需 API Key）
    {"name": "mimo", "command": ["python", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mimo_mcp_server.py")]},
    # 文件系统 MCP - 提供更丰富的文件操作
    # {"name": "fs", "command": ["uvx", "mcp-server-filesystem", "C:\\Users\\big"]},
    # Brave 搜索 MCP - 提供网页搜索
    # {"name": "brave", "command": ["uvx", "mcp-server-brave-search"]},
]
