"""
WebSocket 监控系统 - 主启动文件
==============================

这个文件提供了启动监控系统的主入口，可以同时启动监控客户端和Web界面。

使用方法：
1. 监控模式：python main.py monitor
2. Web界面模式：python main.py web  
3. 同时启动：python main.py all

作者：AI助手
"""

import asyncio
import argparse
import sys
import os
import logging
from multiprocessing import Process
import time

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from monitor_client import WebSocketMonitor, MonitorConfig
from web_interface import app
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    'websocket_url': 'ws://localhost:8000/ws/chat',
    'web_port': 8001,
    'reconnect_interval': 5,
    'max_reconnect_attempts': 10
}

def start_monitor(config: dict):
    """启动监控客户端"""
    async def run_monitor():
        monitor_config = MonitorConfig(
            server_url=config['websocket_url'],
            reconnect_interval=config['reconnect_interval'],
            max_reconnect_attempts=config['max_reconnect_attempts']
        )
        
        monitor = WebSocketMonitor(monitor_config)
        await monitor.start_monitoring()
    
    try:
        asyncio.run(run_monitor())
    except KeyboardInterrupt:
        logger.info("监控客户端被用户中断")
    except Exception as e:
        logger.error(f"监控客户端运行错误: {e}")

def start_web_interface(config: dict):
    """启动Web界面"""
    try:
        logger.info(f"启动Web界面，端口: {config['web_port']}")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=config['web_port'],
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Web界面被用户中断")
    except Exception as e:
        logger.error(f"Web界面运行错误: {e}")

def start_all(config: dict):
    """同时启动监控客户端和Web界面"""
    logger.info("启动完整监控系统...")
    
    # 创建进程
    monitor_process = Process(target=start_monitor, args=(config,))
    web_process = Process(target=start_web_interface, args=(config,))
    
    try:
        # 启动监控客户端
        monitor_process.start()
        logger.info("监控客户端进程已启动")
        
        # 等待一秒确保监控客户端先启动
        time.sleep(1)
        
        # 启动Web界面
        web_process.start()
        logger.info("Web界面进程已启动")
        
        logger.info("=" * 60)
        logger.info("🚀 WebSocket监控系统已完全启动！")
        logger.info(f"📊 监控面板: http://localhost:{config['web_port']}")
        logger.info(f"🔍 监控目标: {config['websocket_url']}")
        logger.info("按 Ctrl+C 停止系统")
        logger.info("=" * 60)
        
        # 等待进程完成
        monitor_process.join()
        web_process.join()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭系统...")
        
        # 终止进程
        if monitor_process.is_alive():
            monitor_process.terminate()
            monitor_process.join()
            logger.info("监控客户端进程已关闭")
            
        if web_process.is_alive():
            web_process.terminate()
            web_process.join()
            logger.info("Web界面进程已关闭")
            
    except Exception as e:
        logger.error(f"系统运行错误: {e}")
        
        # 确保进程清理
        for process in [monitor_process, web_process]:
            if process.is_alive():
                process.terminate()
                process.join()

def load_config_from_file(config_file: str) -> dict:
    """从配置文件加载配置"""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_file):
        try:
            import json
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
            logger.info(f"已加载配置文件: {config_file}")
        except Exception as e:
            logger.warning(f"加载配置文件失败，使用默认配置: {e}")
    else:
        logger.info("配置文件不存在，使用默认配置")
    
    return config

def create_default_config_file():
    """创建默认配置文件"""
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        
        logger.info(f"已创建默认配置文件: {config_file}")
        logger.info("您可以编辑此文件来修改监控配置")

def main():
    """主函数"""
    # 这段代码的作用是让程序在启动时可以通过命令行参数指定运行模式
    # argparse 模块来解析命令行参数
    parser = argparse.ArgumentParser(description='WebSocket 监控系统')
    parser.add_argument(
        'mode', 
        choices=['monitor', 'web', 'all'], 
        help='运行模式: monitor(仅监控) / web(仅Web界面) / all(全部)'
    )
    parser.add_argument(
        '--url', 
        default=None,
        help=f'WebSocket服务器地址 (默认: {DEFAULT_CONFIG["websocket_url"]})'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=None,
        help=f'Web界面端口 (默认: {DEFAULT_CONFIG["web_port"]})'
    )
    parser.add_argument(
        '--config', 
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    args = parser.parse_args()
    
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # 创建默认配置文件
    create_default_config_file()
    
    # 加载配置
    config = load_config_from_file(args.config)
    
    # 命令行参数覆盖配置文件
    if args.url:
        config['websocket_url'] = args.url
    if args.port:
        config['web_port'] = args.port
    
    # 显示配置信息
    logger.info("=" * 60)
    logger.info("WebSocket 监控系统")
    logger.info("=" * 60)
    logger.info(f"运行模式: {args.mode}")
    logger.info(f"监控目标: {config['websocket_url']}")
    logger.info(f"Web端口: {config['web_port']}")
    logger.info(f"重连间隔: {config['reconnect_interval']}秒")
    logger.info(f"最大重连: {config['max_reconnect_attempts']}次")
    logger.info("=" * 60)
    
    # 启动对应模式
    try:
        if args.mode == 'monitor':
            start_monitor(config)
        elif args.mode == 'web':
            start_web_interface(config)
        elif args.mode == 'all':
            start_all(config)
            
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
