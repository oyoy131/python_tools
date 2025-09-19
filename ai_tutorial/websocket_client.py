"""
WebSocket 客户端基础教程
========================

这个文件演示了如何使用 Python 创建一个简单的 WebSocket 客户端。
客户端可以连接到 WebSocket 服务器并进行双向通信。

作者：AI助手
适合人群：Python初学者
"""

import asyncio
import websockets
import json
import threading
import time
from typing import Optional
import sys

class WebSocketClient:
    """
    WebSocket 客户端类
    封装了 WebSocket 连接的基本操作
    """

    def __init__(self, server_url: str = "ws://localhost:8000/ws/chat"):
        """
        初始化 WebSocket 客户端

        Args:
            server_url: WebSocket 服务器地址
        """
        self.server_url = server_url
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.client_id = f"Python客户端_{int(time.time())}"

    async def connect(self):
        """
        连接到 WebSocket 服务器
        """
        try:
            print(f"正在连接到服务器: {self.server_url}")
            # 创建 WebSocket 连接
            self.websocket = await websockets.connect(self.server_url)
            self.is_connected = True
            print("✅ 连接成功！")
            print(f"客户端ID: {self.client_id}")

            # 启动消息监听任务
            asyncio.create_task(self.listen_for_messages())

        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.is_connected = False

    async def disconnect(self):
        """
        断开 WebSocket 连接
        """
        if self.websocket and self.is_connected:
            try:
                await self.websocket.close()
                self.is_connected = False
                print("🔌 连接已断开")
            except Exception as e:
                print(f"断开连接时出错: {e}")

    async def send_message(self, message: str):
        """
        发送消息到服务器

        Args:
            message: 要发送的消息内容
        """
        if not self.is_connected or not self.websocket:
            print("❌ 未连接到服务器，无法发送消息")
            return

        try:
            # 发送消息
            await self.websocket.send(message)
            print(f"📤 发送: {message}")
        except Exception as e:
            print(f"❌ 发送消息失败: {e}")

    async def listen_for_messages(self):
        """
        监听服务器发送的消息
        这是一个持续运行的任务，会在后台监听消息
        """
        try:
            while self.is_connected and self.websocket:
                # 等待接收消息
                message = await self.websocket.recv()

                # 解析 JSON 消息
                try:
                    data = json.loads(message)
                    self.handle_message(data)
                except json.JSONDecodeError:
                    # 如果不是 JSON 格式，直接打印
                    print(f"📥 收到: {message}")

        except websockets.exceptions.ConnectionClosed:
            print("🔌 连接被服务器关闭")
            self.is_connected = False
        except Exception as e:
            print(f"监听消息时出错: {e}")
            self.is_connected = False

    def handle_message(self, data: dict):
        """
        处理接收到的消息

        Args:
            data: 解析后的消息数据
        """
        message_type = data.get('type', 'unknown')
        username = data.get('username', '未知用户')
        message = data.get('message', '')
        timestamp = data.get('timestamp', '')

        # 根据消息类型进行不同处理
        if message_type == 'chat':
            print(f"💬 [{username}] {message}")
        elif message_type == 'system':
            print(f"ℹ️  {message}")
        else:
            print(f"📥 收到未知类型消息: {data}")

async def interactive_chat():
    """
    交互式聊天函数
    提供命令行界面让用户输入消息
    """
    print("=== WebSocket 客户端聊天室 ===")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'help' 查看帮助")
    print()

    # 创建客户端实例
    client = WebSocketClient()

    try:
        # 连接到服务器
        await client.connect()

        if not client.is_connected:
            print("无法连接到服务器，请检查服务器是否运行")
            return

        print("\n=== 开始聊天 ===")

        while client.is_connected:
            # 获取用户输入
            user_input = input("你: ").strip()

            # 处理特殊命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("正在退出...")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'status':
                print(f"连接状态: {'已连接' if client.is_connected else '未连接'}")
                continue
            elif not user_input:
                continue  # 跳过空消息

            # 发送消息
            await client.send_message(user_input)

            # 等待一小段时间，避免消息发送过快
            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
    except Exception as e:
        print(f"聊天过程中出错: {e}")
    finally:
        # 断开连接
        await client.disconnect()

def print_help():
    """显示帮助信息"""
    print("\n=== 帮助信息 ===")
    print("quit/exit/q - 退出聊天")
    print("help - 显示此帮助信息")
    print("status - 查看连接状态")
    print("其他输入 - 发送消息")
    print()

async def auto_chat_example():
    """
    自动聊天示例
    演示如何自动发送一系列消息
    """
    print("=== 自动聊天示例 ===")

    client = WebSocketClient()

    try:
        await client.connect()

        if not client.is_connected:
            return

        # 等待连接稳定
        await asyncio.sleep(1)

        # 发送一系列自动消息
        messages = [
            "你好！这是自动发送的第一条消息",
            "这是第二条消息",
            "WebSocket 客户端工作正常！",
            "最后一条测试消息"
        ]

        for i, message in enumerate(messages, 1):
            await client.send_message(message)
            print(f"已发送第 {i} 条消息")

            # 每条消息间隔1秒
            await asyncio.sleep(1)

        print("自动消息发送完成！")

        # 等待接收服务器的响应
        await asyncio.sleep(3)

    except Exception as e:
        print(f"自动聊天出错: {e}")
    finally:
        await client.disconnect()

async def multiple_clients_example():
    """
    多客户端示例
    演示如何同时运行多个 WebSocket 客户端
    """
    print("=== 多客户端示例 ===")

    async def create_and_chat(client_id: int):
        """创建客户端并发送消息"""
        client = WebSocketClient()

        try:
            await client.connect()
            if client.is_connected:
                await client.send_message(f"我是客户端 {client_id}")
                await asyncio.sleep(2)  # 等待消息处理
        except Exception as e:
            print(f"客户端 {client_id} 出错: {e}")
        finally:
            await client.disconnect()

    # 创建3个并发客户端
    tasks = []
    for i in range(1, 4):
        task = asyncio.create_task(create_and_chat(i))
        tasks.append(task)

    # 等待所有客户端完成
    await asyncio.gather(*tasks)
    print("所有客户端任务完成！")

def main():
    """
    主函数
    提供菜单让用户选择不同的演示模式
    """
    print("=== WebSocket 客户端教程 ===")
    print("请选择演示模式：")
    print("1. 交互式聊天")
    print("2. 自动聊天示例")
    print("3. 多客户端示例")
    print("4. 退出")

    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()

            if choice == "1":
                # 运行交互式聊天
                asyncio.run(interactive_chat())
                break
            elif choice == "2":
                # 运行自动聊天示例
                asyncio.run(auto_chat_example())
                break
            elif choice == "3":
                # 运行多客户端示例
                asyncio.run(multiple_clients_example())
                break
            elif choice == "4":
                print("再见！")
                break
            else:
                print("无效选择，请重新输入")

        except KeyboardInterrupt:
            print("\n程序被用户中断")
            break
        except Exception as e:
            print(f"程序运行出错: {e}")
            break

if __name__ == "__main__":
    # 检查是否安装了 websockets 库
    try:
        import websockets
        main()
    except ImportError:
        print("❌ 未安装 websockets 库")
        print("请运行以下命令安装：")
        print("pip install websockets")
        print("\n或者如果使用的是较老版本的 Python：")
        print("pip install websockets==8.1")
