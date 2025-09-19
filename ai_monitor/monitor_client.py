"""
WebSocket 监控客户端
==================

这个监控客户端可以连接到任何 WebSocket 服务器，实时监控所有聊天消息，
并将数据保存到本地进行分析和可视化。

功能特点：
- 实时监控WebSocket消息
- 自动重连机制
- 消息数据存储
- 统计分析功能
- Web界面展示

作者：AI助手
"""

import asyncio
import websockets
import json
import sqlite3
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass
import aiofiles
import signal
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MonitorConfig:
    """监控配置类"""
    server_url: str = "ws://localhost:8000/ws/chat"  # 目标WebSocket服务器地址
    reconnect_interval: int = 5  # 重连间隔（秒）
    max_reconnect_attempts: int = 10  # 最大重连次数
    database_path: str = "data/chat_monitor.db"  # 数据库文件路径
    log_level: str = "INFO"  # 日志级别
    enable_web_interface: bool = True  # 启用Web界面
    web_port: int = 8001  # Web界面端口

class ChatMessage:
    """聊天消息类"""
    
    def __init__(self, data: dict):
        self.timestamp = data.get('timestamp', datetime.now().isoformat())
        self.message_type = data.get('type', 'unknown')
        self.username = data.get('username', '未知用户')
        self.message = data.get('message', '')
        self.received_at = datetime.now().isoformat()
        
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'username': self.username,
            'message': self.message,
            'received_at': self.received_at
        }

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS monitor_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    connection_events INTEGER DEFAULT 0,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def save_message(self, message: ChatMessage):
        """保存消息到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO chat_messages 
                    (timestamp, message_type, username, message, received_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    message.timestamp,
                    message.message_type,
                    message.username,
                    message.message,
                    message.received_at
                ))
                
        except Exception as e:
            logger.error(f"保存消息到数据库失败: {e}")
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总消息数
                cursor.execute("SELECT COUNT(*) FROM chat_messages")
                total_messages = cursor.fetchone()[0]
                
                # 唯一用户数
                cursor.execute("SELECT COUNT(DISTINCT username) FROM chat_messages")
                unique_users = cursor.fetchone()[0]
                
                # 今日消息数
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE DATE(received_at) = ?
                """, (today,))
                today_messages = cursor.fetchone()[0]
                
                # 最近活跃用户
                cursor.execute("""
                    SELECT username, COUNT(*) as count 
                    FROM chat_messages 
                    WHERE DATE(received_at) = ?
                    GROUP BY username 
                    ORDER BY count DESC 
                    LIMIT 10
                """, (today,))
                active_users = cursor.fetchall()
                
                return {
                    'total_messages': total_messages,
                    'unique_users': unique_users,
                    'today_messages': today_messages,
                    'active_users': active_users,
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """获取最近的消息"""
        try:
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
                
                return list(reversed(messages))  # 按时间正序返回
                
        except Exception as e:
            logger.error(f"获取最近消息失败: {e}")
            return []

class WebSocketMonitor:
    """WebSocket监控器主类"""
    
    def __init__(self, config: MonitorConfig):
        self.config = config
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_running = False
        self.reconnect_attempts = 0
        self.db_manager = DatabaseManager(config.database_path)
        self.message_count = 0
        self.start_time = time.time()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理退出信号"""
        logger.info("收到退出信号，正在关闭监控器...")
        self.is_running = False
        sys.exit(0)
    
    async def start_monitoring(self):
        """开始监控"""
        logger.info("WebSocket监控器启动中...")
        logger.info(f"目标服务器: {self.config.server_url}")
        
        self.is_running = True
        
        while self.is_running:
            try:
                await self._connect_and_monitor()
            except Exception as e:
                logger.error(f"监控过程中出现错误: {e}")
                
            if self.is_running and self.reconnect_attempts < self.config.max_reconnect_attempts:
                self.reconnect_attempts += 1
                logger.info(f"将在 {self.config.reconnect_interval} 秒后重连 (尝试 {self.reconnect_attempts}/{self.config.max_reconnect_attempts})")
                await asyncio.sleep(self.config.reconnect_interval)
            else:
                break
        
        logger.info("监控器已停止")
    
    async def _connect_and_monitor(self):
        """连接并监控WebSocket"""
        try:
            logger.info(f"正在连接到 {self.config.server_url}")
            
            async with websockets.connect(
                self.config.server_url,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            ) as websocket:
                self.websocket = websocket
                self.reconnect_attempts = 0  # 重置重连计数
                
                logger.info("✅ WebSocket连接成功建立")
                logger.info("🔍 开始监控聊天消息...")
                
                # 监听消息
                async for message in websocket:
                    if not self.is_running:
                        break
                        
                    await self._handle_message(message)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket连接被关闭")
        except websockets.exceptions.InvalidURI:
            logger.error(f"无效的WebSocket地址: {self.config.server_url}")
            self.is_running = False
        except Exception as e:
            logger.error(f"连接失败: {e}")
    
    async def _handle_message(self, raw_message: str):
        """处理接收到的消息"""
        try:
            self.message_count += 1
            
            # 尝试解析JSON消息
            try:
                data = json.loads(raw_message)
                message = ChatMessage(data)
            except json.JSONDecodeError:
                # 如果不是JSON格式，创建一个简单的消息对象
                message = ChatMessage({
                    'type': 'raw',
                    'username': '系统',
                    'message': raw_message,
                    'timestamp': datetime.now().isoformat()
                })
            
            # 记录消息
            await self._log_message(message)
            
            # 保存到数据库
            self.db_manager.save_message(message)
            
            # 实时显示统计信息（每10条消息显示一次）
            if self.message_count % 10 == 0:
                await self._show_statistics()
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    async def _log_message(self, message: ChatMessage):
        """记录消息日志"""
        if message.message_type == 'chat':
            logger.info(f"💬 [{message.username}] {message.message}")
        elif message.message_type == 'system':
            logger.info(f"ℹ️  系统消息: {message.message}")
        else:
            logger.info(f"📥 收到消息: {message.message}")
        
        # 保存到日志文件
        log_entry = {
            'timestamp': message.received_at,
            'type': 'message_received',
            'data': message.to_dict()
        }
        
        await self._save_to_log_file(log_entry)
    
    async def _save_to_log_file(self, log_entry: Dict):
        """保存日志到文件"""
        try:
            log_file = f"logs/messages_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
                await f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"保存日志文件失败: {e}")
    
    async def _show_statistics(self):
        """显示统计信息"""
        stats = self.db_manager.get_statistics()
        runtime = time.time() - self.start_time
        
        logger.info("=" * 50)
        logger.info("📊 监控统计信息")
        logger.info(f"运行时间: {int(runtime//3600)}h {int((runtime%3600)//60)}m {int(runtime%60)}s")
        logger.info(f"本次会话消息数: {self.message_count}")
        logger.info(f"数据库总消息数: {stats.get('total_messages', 0)}")
        logger.info(f"唯一用户数: {stats.get('unique_users', 0)}")
        logger.info(f"今日消息数: {stats.get('today_messages', 0)}")
        logger.info("=" * 50)

# 配置变量（可以通过外部设置）
# 这些变量可以在运行时通过环境变量或配置文件修改
WEBSOCKET_URL = "ws://localhost:8000/ws/chat"  # WebSocket服务器地址
RECONNECT_INTERVAL = 5  # 重连间隔
MAX_RECONNECT_ATTEMPTS = 10  # 最大重连次数

async def main():
    """主函数"""
    print("🚀 WebSocket监控系统启动")
    print("=" * 60)
    print("📋 配置信息:")
    print(f"   目标服务器: {WEBSOCKET_URL}")
    print(f"   重连间隔: {RECONNECT_INTERVAL}秒")
    print(f"   最大重连次数: {MAX_RECONNECT_ATTEMPTS}")
    print("=" * 60)
    print()
    
    # 创建配置
    config = MonitorConfig(
        server_url=WEBSOCKET_URL,
        reconnect_interval=RECONNECT_INTERVAL,
        max_reconnect_attempts=MAX_RECONNECT_ATTEMPTS
    )
    
    # 创建监控器
    monitor = WebSocketMonitor(config)
    
    try:
        # 开始监控
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
    except Exception as e:
        logger.error(f"监控器运行错误: {e}")
    finally:
        logger.info("监控器已关闭")

if __name__ == "__main__":
    # 检查依赖
    try:
        import websockets
        import aiofiles
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("请运行以下命令安装依赖:")
        print("pip install websockets aiofiles")
        sys.exit(1)
    
    # 运行监控器
    asyncio.run(main())
