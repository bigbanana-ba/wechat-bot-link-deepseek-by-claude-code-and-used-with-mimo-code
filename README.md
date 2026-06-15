# MiMo MCP Server

通过 MCP (Model Context Protocol) 协议提供 MiMo 模型调用能力。

## 功能

- 调用小米 MiMo 模型回答问题
- 支持数学推理、代码生成、创意写作等任务
- 通过 stdio 与 MCP 客户端通信

## 快速开始

### 1. 安装 MiMo CLI

```bash
npm install -g @mimo-ai/cli
```

### 2. 启动 MCP 服务器

```bash
python mimo_mcp_server.py
```

### 3. 在你的项目中使用

```python
from mcp_client import MCPClient

# 创建客户端
client = MCPClient("mimo", ["python", "mimo_mcp_server.py"])

# 启动服务器
if client.start():
    # 调用工具
    result = client.call_tool("mimo_chat", {"message": "你好"})
    print(result)
    
    # 停止服务器
    client.stop()
```

## MCP 工具

### mimo_chat

调用 MiMo 模型回答问题。

**参数:**
- `message` (必需): 用户的问题或指令
- `model` (可选): 模型 ID，默认 `mimo/mimo-auto`
  - `mimo/mimo-auto` - 自动选择
  - `xiaomi/mimo-v2-flash` - 快速模型
  - `xiaomi/mimo-v2.5-pro` - 专业模型

**示例:**
```json
{
  "message": "请解释量子计算的基本原理",
  "model": "mimo/mimo-auto"
}
```

## 配置

### 环境变量

- `MIMO_BIN`: MiMo CLI 路径（默认自动检测）
- `MIMO_MODE`: 运行模式，`cli`（免费）或 `api`（需 API Key）

### 在其他项目中集成

```python
import os
from mcp_client import init_mcp, call_mcp_tool, stop_all_mcp

# 配置 MCP 服务器
MCP_SERVERS = [
    {"name": "mimo", "command": ["python", "/path/to/mimo_mcp_server.py"]},
]

# 初始化
tools = init_mcp(MCP_SERVERS)

# 使用
result = call_mcp_tool("mcp_mimo_mimo_chat", {"message": "你好"})

# 清理
stop_all_mcp()
```

## 依赖

- Python 3.8+
- MiMo CLI (`npm install -g @mimo-ai/cli`)

## License

MIT