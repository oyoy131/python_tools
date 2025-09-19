"""
WebSocket 监控系统使用示例
========================

本文件演示了如何使用 WebSocket 监控系统的各种功能。

作者：AI助手
"""

import asyncio
import json
import time
from datetime import datetime
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitor_client import WebSocketMonitor, MonitorConfig

async def example_basic_monitoring():
    """基础监控示例"""
    print("=== 基础监控示例 ===")
    
    # 创建配置
    config = MonitorConfig(
        server_url="ws://localhost:8000/ws/chat",
        reconnect_interval=3,
        max_reconnect_attempts=5
    )
    
    # 创建监控器
    monitor = WebSocketMonitor(config)
    
    try:
        # 运行监控（这里只运行30秒作为示例）
        print("开始监控，将运行30秒...")
        await asyncio.wait_for(monitor.start_monitoring(), timeout=30.0)
    except asyncio.TimeoutError:
        print("示例监控时间结束")
    except Exception as e:
        print(f"监控过程中出错: {e}")

async def example_custom_message_handler():
    """自定义消息处理示例"""
    print("=== 自定义消息处理示例 ===")
    
    class CustomWebSocketMonitor(WebSocketMonitor):
        """自定义监控器，演示如何扩展消息处理功能"""
        
        def __init__(self, config):
            super().__init__(config)
            self.alert_keywords = ["紧急", "重要", "admin", "错误"]
            self.user_stats = {}
        
        async def _handle_message(self, raw_message: str):
            """重写消息处理方法"""
            # 调用父类方法进行基础处理
            await super()._handle_message(raw_message)
            
            try:
                data = json.loads(raw_message)
                message_text = data.get('message', '').lower()
                username = data.get('username', '')
                
                # 检查告警关键词
                for keyword in self.alert_keywords:
                    if keyword in message_text:
                        await self._send_alert(username, data.get('message', ''), keyword)
                
                # 统计用户活动
                if username and username != '系统':
                    if username not in self.user_stats:
                        self.user_stats[username] = {
                            'message_count': 0,
                            'first_seen': datetime.now().isoformat(),
                            'last_seen': datetime.now().isoformat()
                        }
                    
                    self.user_stats[username]['message_count'] += 1
                    self.user_stats[username]['last_seen'] = datetime.now().isoformat()
                    
                    # 每100条消息输出一次用户统计
                    if self.message_count % 100 == 0:
                        await self._show_user_stats()
                        
            except json.JSONDecodeError:
                pass  # 非JSON消息，跳过自定义处理
        
        async def _send_alert(self, username: str, message: str, keyword: str):
            """发送告警"""
            alert_msg = f"🚨 告警检测: 用户 {username} 发送了包含关键词 '{keyword}' 的消息: {message}"
            print(alert_msg)
            
            # 这里可以扩展为发送邮件、钉钉通知等
            await self._save_alert_to_file(username, message, keyword)
        
        async def _save_alert_to_file(self, username: str, message: str, keyword: str):
            """保存告警到文件"""
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'username': username,
                'message': message,
                'keyword': keyword,
                'type': 'alert'
            }
            
            alert_file = f"logs/alerts_{datetime.now().strftime('%Y%m%d')}.json"
            os.makedirs(os.path.dirname(alert_file), exist_ok=True)
            
            try:
                with open(alert_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(alert_data, ensure_ascii=False) + '\n')
            except Exception as e:
                print(f"保存告警失败: {e}")
        
        async def _show_user_stats(self):
            """显示用户统计"""
            print("\n" + "="*50)
            print("📊 用户活动统计")
            print("="*50)
            
            # 按消息数排序
            sorted_users = sorted(
                self.user_stats.items(), 
                key=lambda x: x[1]['message_count'], 
                reverse=True
            )
            
            for username, stats in sorted_users[:10]:  # 显示前10名
                print(f"{username}: {stats['message_count']} 条消息")
            
            print("="*50 + "\n")
    
    # 使用自定义监控器
    config = MonitorConfig(
        server_url="ws://localhost:8000/ws/chat",
        reconnect_interval=3,
        max_reconnect_attempts=3
    )
    
    custom_monitor = CustomWebSocketMonitor(config)
    
    try:
        print("开始自定义监控，将运行30秒...")
        await asyncio.wait_for(custom_monitor.start_monitoring(), timeout=30.0)
    except asyncio.TimeoutError:
        print("自定义监控示例结束")
        
        # 显示最终统计
        if custom_monitor.user_stats:
            await custom_monitor._show_user_stats()
    except Exception as e:
        print(f"自定义监控出错: {e}")

def example_database_query():
    """数据库查询示例"""
    print("=== 数据库查询示例 ===")
    
    import sqlite3
    
    db_path = "data/chat_monitor.db"
    
    if not os.path.exists(db_path):
        print("数据库文件不存在，请先运行监控系统收集数据")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 查询总消息数
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            total_messages = cursor.fetchone()[0]
            print(f"总消息数: {total_messages}")
            
            # 查询最活跃的用户
            cursor.execute("""
                SELECT username, COUNT(*) as count 
                FROM chat_messages 
                WHERE message_type = 'chat' 
                GROUP BY username 
                ORDER BY count DESC 
                LIMIT 5
            """)
            active_users = cursor.fetchall()
            
            print("\n最活跃用户:")
            for username, count in active_users:
                print(f"  {username}: {count} 条消息")
            
            # 查询最近的消息
            cursor.execute("""
                SELECT timestamp, username, message 
                FROM chat_messages 
                ORDER BY id DESC 
                LIMIT 5
            """)
            recent_messages = cursor.fetchall()
            
            print("\n最近的消息:")
            for timestamp, username, message in recent_messages:
                print(f"  [{timestamp}] {username}: {message}")
            
            # 查询每小时消息分布
            cursor.execute("""
                SELECT CAST(strftime('%H', received_at) AS INTEGER) as hour, COUNT(*) as count
                FROM chat_messages 
                WHERE DATE(received_at) = DATE('now')
                GROUP BY hour
                ORDER BY hour
            """)
            hourly_stats = cursor.fetchall()
            
            if hourly_stats:
                print("\n今日每小时消息分布:")
                for hour, count in hourly_stats:
                    print(f"  {hour:02d}:00 - {count} 条消息")
            
    except Exception as e:
        print(f"数据库查询出错: {e}")

def example_config_management():
    """配置管理示例"""
    print("=== 配置管理示例 ===")
    
    # 读取当前配置
    config_file = "config.json"
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("当前配置:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("配置文件不存在")
    
    # 创建自定义配置示例
    custom_config = {
        "websocket_url": "ws://example.com/ws/chat",
        "web_port": 8002,
        "reconnect_interval": 10,
        "max_reconnect_attempts": 20,
        "database_path": "data/custom_monitor.db",
        "log_level": "DEBUG",
        "enable_notifications": True,
        "notification_keywords": ["紧急", "重要", "admin", "错误", "故障"]
    }
    
    # 保存自定义配置
    custom_config_file = "config_example.json"
    with open(custom_config_file, 'w', encoding='utf-8') as f:
        json.dump(custom_config, f, indent=4, ensure_ascii=False)
    
    print(f"\n已创建自定义配置示例: {custom_config_file}")

async def example_web_api_usage():
    """Web API 使用示例"""
    print("=== Web API 使用示例 ===")
    
    import aiohttp
    
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 获取统计数据
            async with session.get(f"{base_url}/api/stats") as response:
                if response.status == 200:
                    stats = await response.json()
                    print("统计数据:")
                    print(f"  总消息数: {stats.get('total_messages', 0)}")
                    print(f"  唯一用户数: {stats.get('unique_users', 0)}")
                    print(f"  今日消息数: {stats.get('today_messages', 0)}")
                else:
                    print(f"获取统计数据失败: {response.status}")
            
            # 获取最近消息
            async with session.get(f"{base_url}/api/messages?limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    messages = data.get('messages', [])
                    
                    print(f"\n最近 {len(messages)} 条消息:")
                    for msg in messages:
                        print(f"  [{msg.get('username')}] {msg.get('message')}")
                else:
                    print(f"获取消息失败: {response.status}")
            
            # 搜索消息
            search_keyword = "测试"
            async with session.get(f"{base_url}/api/search?q={search_keyword}") as response:
                if response.status == 200:
                    data = await response.json()
                    messages = data.get('messages', [])
                    
                    print(f"\n包含 '{search_keyword}' 的消息 ({len(messages)} 条):")
                    for msg in messages[:3]:  # 只显示前3条
                        print(f"  [{msg.get('username')}] {msg.get('message')}")
                else:
                    print(f"搜索消息失败: {response.status}")
                    
        except aiohttp.ClientError as e:
            print(f"Web API 连接失败: {e}")
            print("请确保 Web 界面已启动 (python main.py web)")
        except Exception as e:
            print(f"Web API 使用出错: {e}")

def main():
    """主函数 - 显示示例菜单"""
    print("WebSocket 监控系统使用示例")
    print("=" * 50)
    print("1. 基础监控示例")
    print("2. 自定义消息处理示例")
    print("3. 数据库查询示例")
    print("4. 配置管理示例")
    print("5. Web API 使用示例")
    print("6. 运行所有示例")
    print("0. 退出")
    print("=" * 50)
    
    while True:
        try:
            choice = input("请选择示例 (0-6): ").strip()
            
            if choice == "0":
                print("再见！")
                break
            elif choice == "1":
                asyncio.run(example_basic_monitoring())
            elif choice == "2":
                asyncio.run(example_custom_message_handler())
            elif choice == "3":
                example_database_query()
            elif choice == "4":
                example_config_management()
            elif choice == "5":
                asyncio.run(example_web_api_usage())
            elif choice == "6":
                print("运行所有示例...")
                example_config_management()
                example_database_query()
                await asyncio.run(example_web_api_usage())
                print("所有示例运行完成！")
            else:
                print("无效选择，请重新输入")
                
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"运行示例时出错: {e}")

if __name__ == "__main__":
    main()
