"""
WebSocket 服务器基础教程
========================

这个文件演示了如何使用 FastAPI 创建一个简单的 WebSocket 服务器。
WebSocket 允许服务器和客户端之间进行双向实时通信。

作者：AI助手
适合人群：Python初学者
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from typing import List, Dict
import json
from datetime import datetime

# 创建 FastAPI 应用实例
app = FastAPI(
    title="WebSocket 服务器教程",
    description="学习 WebSocket 服务器的基本用法"
)

# 存储所有连接的 WebSocket 客户端
connected_clients: List[WebSocket] = []

# 存储聊天历史记录
chat_history: List[Dict] = []

@app.get("/")
async def root():
    """
    根路径 - 返回简单的 HTML 页面
    这个页面包含一个简单的 WebSocket 客户端
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket 教程</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #messages { border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
            #messageInput { width: 70%; padding: 5px; }
            button { padding: 5px 10px; }
            .message { margin: 5px 0; padding: 5px; background: #f5f5f5; border-radius: 3px; }
            .timestamp { color: #666; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <h1>WebSocket 聊天室教程</h1>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="输入消息..." onkeypress="handleKeyPress(event)">
        <button onclick="sendMessage()">发送</button>
        <button onclick="clearMessages()">清空消息</button>

        <script>
            // 创建 WebSocket 连接
            const ws = new WebSocket('ws://localhost:8000/ws/chat');

            // 连接成功时的处理
            ws.onopen = function(event) {
                console.log('WebSocket 连接已建立');
                addMessage('系统', '已连接到聊天室');
            };

            // 接收消息时的处理
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data.username, data.message, data.timestamp);
            };

            // 连接关闭时的处理
            ws.onclose = function(event) {
                console.log('WebSocket 连接已关闭');
                addMessage('系统', '连接已断开');
            };

            // 发生错误时的处理
            ws.onerror = function(error) {
                console.error('WebSocket 错误:', error);
                addMessage('系统', '连接出现错误');
            };

            // 发送消息的函数
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();

                if (message && ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    input.value = '';
                }
            }

            // 处理键盘按键
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            // 清空消息的函数
            function clearMessages() {
                document.getElementById('messages').innerHTML = '';
            }

            // 添加消息到显示区域的函数
            function addMessage(username, message, timestamp) {
                const messagesDiv = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';

                const timeStr = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
                messageDiv.innerHTML = `<strong>${username}:</strong> ${message} <span class="timestamp">${timeStr}</span>`;

                messagesDiv.appendChild(messageDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket 聊天端点
    处理客户端的 WebSocket 连接和消息
    """
    await websocket.accept()  # 接受 WebSocket 连接

    # 生成一个简单的用户名（在实际应用中应该使用用户认证）
    client_id = f"用户_{len(connected_clients) + 1}"

    # 将新客户端添加到连接列表
    connected_clients.append(websocket)

    try:
        # 发送欢迎消息
        welcome_message = {
            "type": "system",
            "username": "系统",
            "message": f"{client_id} 加入了聊天室",
            "timestamp": datetime.now().isoformat()
        }

        # 向所有客户端广播欢迎消息
        await broadcast_message(welcome_message)

        # 发送聊天历史记录给新用户
        for history_msg in chat_history[-10:]:  # 只发送最近10条消息
            await websocket.send_text(json.dumps(history_msg))

        # 循环监听客户端发送的消息
        while True:
            # 等待接收客户端发送的数据
            data = await websocket.receive_text()

            # 创建消息对象
            message_data = {
                "type": "chat",
                "username": client_id,
                "message": data,
                "timestamp": datetime.now().isoformat()
            }

            # 将消息添加到历史记录
            chat_history.append(message_data)

            # 限制历史记录长度（避免内存占用过大）
            if len(chat_history) > 100:
                chat_history.pop(0)

            # 向所有客户端广播消息
            await broadcast_message(message_data)

    except WebSocketDisconnect:
        # 处理客户端断开连接的情况
        print(f"客户端 {client_id} 断开连接")

        # 从连接列表中移除客户端
        if websocket in connected_clients:
            connected_clients.remove(websocket)

        # 发送离开消息
        leave_message = {
            "type": "system",
            "username": "系统",
            "message": f"{client_id} 离开了聊天室",
            "timestamp": datetime.now().isoformat()
        }

        await broadcast_message(leave_message)

    except Exception as e:
        # 处理其他异常
        print(f"WebSocket 错误: {e}")

        # 从连接列表中移除客户端
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_message(message: Dict):
    """
    向所有连接的客户端广播消息

    Args:
        message: 要广播的消息字典
    """
    # 将消息转换为 JSON 字符串
    message_json = json.dumps(message)

    # 创建要移除的客户端列表（避免在遍历时修改列表）
    clients_to_remove = []

    # 遍历所有连接的客户端
    for client in connected_clients:
        try:
            # 向客户端发送消息
            await client.send_text(message_json)
        except Exception as e:
            # 如果发送失败，标记为要移除的客户端
            print(f"发送消息失败: {e}")
            clients_to_remove.append(client)

    # 移除发送失败的客户端
    for client in clients_to_remove:
        if client in connected_clients:
            connected_clients.remove(client)

@app.get("/stats")
async def get_stats():
    """
    获取服务器统计信息
    返回当前连接的客户端数量和消息历史长度
    """
    return {
        "connected_clients": len(connected_clients),
        "total_messages": len(chat_history),
        "server_status": "running"
    }

@app.on_event("startup")
async def startup_event():
    """服务器启动时执行的函数"""
    print("WebSocket 服务器正在启动...")
    print("访问 http://localhost:8000 查看聊天室")

@app.on_event("shutdown")
async def shutdown_event():
    """服务器关闭时执行的函数"""
    print("WebSocket 服务器正在关闭...")
    print(f"共有 {len(connected_clients)} 个客户端连接")

if __name__ == "__main__":
    # 启动服务器
    print("启动 WebSocket 服务器...")
    print("访问地址：")
    print("- 聊天室: http://localhost:8000")
    print("- 统计信息: http://localhost:8000/stats")
    print("\n按 Ctrl+C 停止服务器")

    uvicorn.run(
        "websocket_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
