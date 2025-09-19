"""
WebSocket 监控 Web 界面
====================

提供一个基于 FastAPI 的 Web 界面来展示监控数据。
包含实时消息显示、统计图表、用户活动分析等功能。

作者：AI助手
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import json
import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WebSocket 监控面板",
    description="实时监控 WebSocket 聊天数据"
)

# 设置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# WebSocket连接管理
connected_clients: List[WebSocket] = []

class MonitorWebInterface:
    """监控Web界面类"""
    
    def __init__(self, db_path: str = "data/chat_monitor.db"):
        self.db_path = db_path
    
    def get_statistics(self) -> Dict:
        """获取统计数据"""
        try:
            if not os.path.exists(self.db_path):
                return self._empty_stats()
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 基础统计
                cursor.execute("SELECT COUNT(*) FROM chat_messages")
                total_messages = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(DISTINCT username) FROM chat_messages WHERE username != '系统'")
                unique_users = cursor.fetchone()[0] or 0
                
                # 今日统计
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE DATE(received_at) = ? AND message_type = 'chat'
                """, (today,))
                today_messages = cursor.fetchone()[0] or 0
                
                # 活跃用户（今日）
                cursor.execute("""
                    SELECT username, COUNT(*) as count 
                    FROM chat_messages 
                    WHERE DATE(received_at) = ? AND message_type = 'chat' AND username != '系统'
                    GROUP BY username 
                    ORDER BY count DESC 
                    LIMIT 10
                """, (today,))
                active_users = cursor.fetchall()
                
                # 最近7天的消息统计
                cursor.execute("""
                    SELECT DATE(received_at) as date, COUNT(*) as count
                    FROM chat_messages 
                    WHERE received_at >= DATE('now', '-7 days') AND message_type = 'chat'
                    GROUP BY DATE(received_at)
                    ORDER BY date DESC
                """)
                daily_stats = cursor.fetchall()
                
                # 每小时消息分布（今日）
                cursor.execute("""
                    SELECT CAST(strftime('%H', received_at) AS INTEGER) as hour, COUNT(*) as count
                    FROM chat_messages 
                    WHERE DATE(received_at) = ? AND message_type = 'chat'
                    GROUP BY hour
                    ORDER BY hour
                """, (today,))
                hourly_stats = cursor.fetchall()
                
                return {
                    'total_messages': total_messages,
                    'unique_users': unique_users,
                    'today_messages': today_messages,
                    'active_users': active_users,
                    'daily_stats': daily_stats,
                    'hourly_stats': hourly_stats,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"获取统计数据失败: {e}")
            return self._empty_stats()
    
    def _empty_stats(self) -> Dict:
        """返回空的统计数据"""
        return {
            'total_messages': 0,
            'unique_users': 0,
            'today_messages': 0,
            'active_users': [],
            'daily_stats': [],
            'hourly_stats': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """获取最近的消息"""
        try:
            if not os.path.exists(self.db_path):
                return []
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, message_type, username, message, received_at
                    FROM chat_messages 
                    ORDER BY id DESC 
                    LIMIT ?
                """, (limit,))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'timestamp': row[0],
                        'message_type': row[1],
                        'username': row[2],
                        'message': row[3],
                        'received_at': row[4]
                    })
                
                return list(reversed(messages))
                
        except Exception as e:
            logger.error(f"获取最近消息失败: {e}")
            return []
    
    def search_messages(self, keyword: str, limit: int = 100) -> List[Dict]:
        """搜索消息"""
        try:
            if not os.path.exists(self.db_path):
                return []
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, message_type, username, message, received_at
                    FROM chat_messages 
                    WHERE message LIKE ? OR username LIKE ?
                    ORDER BY id DESC 
                    LIMIT ?
                """, (f'%{keyword}%', f'%{keyword}%', limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'timestamp': row[0],
                        'message_type': row[1],
                        'username': row[2],
                        'message': row[3],
                        'received_at': row[4]
                    })
                
                return messages
                
        except Exception as e:
            logger.error(f"搜索消息失败: {e}")
            return []

# 创建监控接口实例
monitor_interface = MonitorWebInterface()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """监控面板主页"""
    stats = monitor_interface.get_statistics()
    recent_messages = monitor_interface.get_recent_messages(20)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_messages": recent_messages
    })

@app.get("/api/stats")
async def get_stats():
    """获取统计数据API"""
    return JSONResponse(monitor_interface.get_statistics())

@app.get("/api/messages")
async def get_messages(limit: int = 50):
    """获取消息列表API"""
    messages = monitor_interface.get_recent_messages(limit)
    return JSONResponse({"messages": messages})

@app.get("/api/search")
async def search_messages(q: str, limit: int = 100):
    """搜索消息API"""
    if not q or len(q.strip()) < 2:
        return JSONResponse({"error": "搜索关键词至少需要2个字符"}, status_code=400)
    
    messages = monitor_interface.search_messages(q.strip(), limit)
    return JSONResponse({"messages": messages, "keyword": q})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点，用于实时更新数据"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        while True:
            # 定期发送更新数据
            stats = monitor_interface.get_statistics()
            await websocket.send_text(json.dumps({
                "type": "stats_update",
                "data": stats
            }))
            
            # 每5秒更新一次
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_new_message(message_data: Dict):
    """广播新消息到所有连接的客户端"""
    if not connected_clients:
        return
    
    message = {
        "type": "new_message",
        "data": message_data
    }
    
    # 要移除的客户端列表
    clients_to_remove = []
    
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(message))
        except Exception:
            clients_to_remove.append(client)
    
    # 移除断开的客户端
    for client in clients_to_remove:
        connected_clients.remove(client)

@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("WebSocket监控面板启动成功")
    logger.info("访问地址: http://localhost:8001")

if __name__ == "__main__":
    uvicorn.run(
        "web_interface:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
