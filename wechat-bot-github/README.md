# WeChat AI Agent

> 把 DeepSeek 变成微信聊天机器人 — 支持工具调用、联网搜索、图片识别、文件操作、记忆系统

## 功能

| 能力 | 说明 |
|------|------|
| 智能对话 | DeepSeek V3/V4/R1 多模型自由切换 |
| 联网搜索 | Chrome 浏览器 + Bing HTTP 双保险 |
| 图片识别 | Qwen3-VL-Plus 最新模型 |
| GitHub 搜索 | 搜索开源项目和代码 |
| 文件操作 | 读写文件、生成 Excel/Word |
| 命令执行 | Python 脚本、Shell、系统工具 |
| 记忆系统 | 人类可读 preferences.txt |
| 发送文件 | cc-connect send 原生支持 |
| 视频分析 | ffmpeg 抽帧 + 视觉识别 |
| Token 优化 | 智能截断、分级上下文、省 60-90% |
| MCP 支持 | 可扩展连接任意 MCP Server |

## 架构

```
微信 → cc-connect → fake-claude.py → DeepSeek API
                   ├── 图片识别 → Qwen-VL API
                   ├── 联网搜索 → Chrome CDP (puppeteer)
                   └── 记忆系统 → preferences.txt + memory.json
```

## 快速开始

### 1. 安装依赖

```powershell
# Node.js 22+
# Python 3.12+
# Chrome 浏览器

npm install -g cc-connect@beta puppeteer-core
pip install -r requirements.txt

# 安装并配置 web-access skill（可选，增强联网能力）
npx skills add eze-is/web-access@web-access -g -y
```

### 2. 配置 API Key

复制配置文件并填入你的 API Key：

```powershell
# Windows
copy fake-claude.py.example fake-claude.py
copy chrome-browse.js.example chrome-browse.js

# Linux/Mac
cp fake-claude.py.example fake-claude.py
cp chrome-browse.js.example chrome-browse.js
```

打开 `fake-claude.py`，填入你的 API Key：

```python
DEEPSEEK_API_KEY = "sk-你的DeepSeek-Key"
QWEN_API_KEY = "sk-你的千问-Key"  # 阿里云百炼，用于图片识别
```

### 3. 扫码登录微信

```powershell
cc-connect weixin setup --project wechat-bot
```

用微信扫描终端显示的二维码。

### 4. 启动机器人

```powershell
cc-connect --force
```

## 文件结构

```
wechat-bot/
├── fake-claude.py          # AI 核心（工具调用、记忆、搜索）
├── chrome-browse.js        # Chrome 浏览器自动化脚本
├── edge-browse.js          # Edge 浏览器自动化脚本
├── mcp_client.py           # MCP 客户端
├── mimo_mcp_server.py      # MiMo MCP 服务器
├── requirements.txt        # Python 依赖
├── package.json            # Node.js 依赖
└── README.md
```

## 可用工具

机器人可以自主选择使用以下工具：

- `web_search` - 用 Chrome 搜索网页
- `bash` - 执行 Shell 命令和 Python 脚本
- `read` / `write` / `list_dir` / `grep` - 文件操作
- `send_to_wechat` - 发送文件/图片到微信
- `ask_model` - 调用更强的模型（deepseek-v4-pro / deepseek-reasoner）
- `remember_preference` / `forget_preferences` - 记忆偏好
- `read_docx` - 读取 Word 文档
- `analyze_video` - 分析视频内容

## 微信聊天命令

| 命令 | 作用 |
|------|------|
| `/reset` | 重置对话历史和偏好 |
| `通过mimo <问题>` | 调用 MiMo 模型回答 |

## MCP 扩展

项目支持 MCP (Model Context Protocol)，可以扩展连接任意 MCP Server。

### 配置 MCP 服务器

编辑 `mcp_client.py` 中的 `MCP_SERVERS` 列表：

```python
MCP_SERVERS = [
    # MiMo MCP - 调用小米 MiMo 模型（免费，无需 API Key）
    {"name": "mimo", "command": ["python", "mimo_mcp_server.py"]},
    # 文件系统 MCP - 提供更丰富的文件操作
    # {"name": "fs", "command": ["uvx", "mcp-server-filesystem", "."]},
    # Brave 搜索 MCP - 提供网页搜索
    # {"name": "brave", "command": ["uvx", "mcp-server-brave-search"]},
]
```

## 注意事项

- 需要一台 Windows 电脑保持开机运行
- Chrome 需要保持打开（或开启 CDP 调试端口）
- DeepSeek 和千问 API 都按量计费，日常聊天用 deepseek-chat 很便宜（月均几块钱）
- 微信 iLink 协议仅供个人学习和研究使用

## License

MIT

## 致谢

- [cc-connect](https://github.com/chenhg5/cc-connect) - 微信桥接
- [DeepSeek](https://platform.deepseek.com) - AI 模型
- [Qwen-VL](https://dashscope.aliyun.com) - 图片识别
- [web-access](https://github.com/eze-is/web-access) - 浏览器自动化 Skill