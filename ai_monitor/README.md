# WebSocket 监控系统

## 项目简介

这是一个功能强大的 WebSocket 监控系统，专门用于实时监控 WebSocket 服务器的聊天消息和用户活动。系统可以在不需要服务器源码的情况下，通过 WebSocket 客户端连接来监控所有聊天数据。

### 主要功能

- 🔍 **实时监控**: 实时捕获和显示 WebSocket 聊天消息
- 📊 **数据分析**: 提供详细的统计分析和可视化图表
- 💾 **数据存储**: 自动保存所有监控数据到 SQLite 数据库
- 🌐 **Web界面**: 现代化的 Web 监控面板
- 🔄 **自动重连**: 智能重连机制，确保监控连续性
- 🔍 **消息搜索**: 支持关键词搜索历史消息
- 📈 **实时统计**: 实时显示用户活动和消息统计

## 系统架构

```
ai_monitor/
├── main.py              # 主启动文件
├── monitor_client.py    # WebSocket监控客户端
├── web_interface.py     # Web监控界面
├── config.json          # 配置文件
├── requirements.txt     # 依赖包列表
├── templates/           # HTML模板
│   └── dashboard.html   # 监控面板模板
├── static/              # 静态文件目录
├── logs/                # 日志文件目录
└── data/                # 数据库文件目录
```

## 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8+：

```bash
python --version
```

### 2. 安装依赖

```bash
cd ai_monitor
pip install -r requirements.txt
```

### 3. 配置系统

编辑 `config.json` 文件，设置要监控的 WebSocket 服务器地址：

```json
{
    "websocket_url": "ws://localhost:8000/ws/chat",
    "web_port": 8001,
    "reconnect_interval": 5,
    "max_reconnect_attempts": 10
}
```

### 4. 启动监控系统

#### 方式一：完整启动（推荐）
同时启动监控客户端和 Web 界面：

```bash
python main.py all
```

#### 方式二：仅启动监控客户端
```bash
python main.py monitor
```

#### 方式三：仅启动 Web 界面
```bash
python main.py web
```

### 5. 访问监控面板

启动后访问：http://localhost:8001

## 详细使用说明

### 监控客户端功能

**WebSocket 连接监控**
- 自动连接到目标 WebSocket 服务器
- 实时捕获所有聊天消息
- 智能重连机制，网络中断后自动恢复

**数据存储**
- 所有消息自动保存到 SQLite 数据库
- 支持消息类型分类（聊天、系统消息等）
- 记录详细的时间戳和用户信息

**日志记录**
- 详细的运行日志记录
- 按日期分类保存消息日志
- 支持不同日志级别配置

### Web 监控界面功能

**实时监控面板**
- 实时显示监控统计数据
- 消息总数、活跃用户数、今日消息数
- 监控状态实时更新

**数据可视化**
- 每日消息趋势图表
- 24小时消息分布图
- 活跃用户排行榜

**消息管理**
- 实时消息流显示
- 支持关键词搜索
- 消息类型分类显示

**统计分析**
- 用户活动分析
- 消息频率统计
- 时间分布分析

## 配置选项详解

### config.json 配置文件

```json
{
    "websocket_url": "ws://localhost:8000/ws/chat",  // 目标WebSocket地址
    "web_port": 8001,                                // Web界面端口
    "reconnect_interval": 5,                         // 重连间隔（秒）
    "max_reconnect_attempts": 10,                    // 最大重连次数
    "database_path": "data/chat_monitor.db",         // 数据库文件路径
    "log_level": "INFO",                             // 日志级别
    "enable_notifications": false,                   // 是否启用通知
    "notification_keywords": ["重要", "紧急"],        // 通知关键词
    "max_messages_in_memory": 1000,                  // 内存中最大消息数
    "auto_backup_hours": 24,                         // 自动备份间隔
    "web_refresh_interval": 5                        // Web界面刷新间隔
}
```

### 命令行参数

```bash
python main.py [mode] [options]

位置参数:
  mode              运行模式: monitor/web/all

可选参数:
  --url URL         WebSocket服务器地址
  --port PORT       Web界面端口
  --config CONFIG   配置文件路径
```

## 部署建议

### 开发环境部署

1. 克隆项目到本地
2. 安装依赖包
3. 修改配置文件
4. 启动监控系统

### 生产环境部署

**使用 Docker 部署（推荐）**

创建 Dockerfile：

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "main.py", "all"]
```

构建和运行：

```bash
docker build -t websocket-monitor .
docker run -p 8001:8001 -v $(pwd)/data:/app/data websocket-monitor
```

**使用 systemd 服务**

创建服务文件 `/etc/systemd/system/websocket-monitor.service`：

```ini
[Unit]
Description=WebSocket Monitor Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/ai_monitor
ExecStart=/usr/bin/python3 main.py all
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable websocket-monitor
sudo systemctl start websocket-monitor
```

## 故障排除

### 常见问题

**1. 无法连接到 WebSocket 服务器**
- 检查 WebSocket 服务器是否正在运行
- 验证 `config.json` 中的 URL 是否正确
- 检查防火墙设置

**2. Web 界面无法访问**
- 检查端口是否被占用：`netstat -an | grep 8001`
- 确认防火墙允许对应端口
- 查看启动日志中的错误信息

**3. 数据库错误**
- 检查 `data` 目录权限
- 确保磁盘空间充足
- 查看错误日志获取详细信息

**4. 内存占用过高**
- 调整 `max_messages_in_memory` 配置
- 定期清理历史数据
- 重启监控服务

### 日志查看

**运行时日志**
```bash
tail -f logs/monitor.log
```

**消息日志**
```bash
tail -f logs/messages_20231201.json
```

### 数据备份

**手动备份数据库**
```bash
cp data/chat_monitor.db data/backup_$(date +%Y%m%d_%H%M%S).db
```

**导出消息数据**
```bash
sqlite3 data/chat_monitor.db ".output messages_export.csv" ".mode csv" "SELECT * FROM chat_messages;"
```

## 高级功能

### 自定义监控规则

您可以修改 `monitor_client.py` 中的消息处理逻辑来实现：

- 关键词过滤和告警
- 特定用户监控
- 消息内容分析
- 自动响应机制

### 扩展数据分析

系统支持集成更多分析工具：

- 情感分析
- 用户行为分析
- 异常检测
- 报表生成

### API 集成

Web 界面提供 RESTful API：

- `GET /api/stats` - 获取统计数据
- `GET /api/messages` - 获取消息列表
- `GET /api/search` - 搜索消息

## 技术栈

- **后端**: Python 3.8+, FastAPI, WebSockets
- **数据库**: SQLite
- **前端**: HTML5, Bootstrap 5, Chart.js
- **部署**: Docker, systemd

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues]
- 邮箱: [your-email@example.com]

---

**注意**: 使用本监控系统时请确保遵守相关法律法规和隐私政策。
