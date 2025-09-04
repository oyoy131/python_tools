"""
Uvicorn 基础教程
================

Uvicorn 是一个基于 uvloop 和 httptools 构建的快速 ASGI 服务器实现。
它主要用于运行 Python 异步 web 应用程序，特别是 FastAPI 应用。

作者：AI助手
适合人群：Python初学者
"""

# ========================================
# 第一部分：什么是 Uvicorn？
# ========================================

"""
Uvicorn 是一个 ASGI (Asynchronous Server Gateway Interface) 服务器。
它可以运行异步 Python web 应用程序，比如：
- FastAPI 应用
- Starlette 应用
- Django 3.0+ 的异步视图

主要特点：
1. 高性能 - 基于 uvloop 事件循环
2. 简单易用 - 命令行启动
3. 支持热重载 - 开发时自动重启
4. 支持多种协议 - HTTP/1.1, WebSockets
"""

# ========================================
# 第二部分：安装 Uvicorn
# ========================================

"""
安装命令：
pip install uvicorn

如果要使用所有功能（推荐）：
pip install "uvicorn[standard]"

这将安装额外的依赖：
- uvloop: 高性能事件循环
- httptools: 快速 HTTP 解析
- python-dotenv: 环境变量支持
- PyYAML: YAML 配置支持
- watchfiles: 文件监控（热重载）
"""

# ========================================
# 第三部分：最简单的例子
# ========================================

async def simple_app(scope, receive, send):
    """
    最基础的 ASGI 应用示例
    这是一个返回 "Hello World" 的简单应用
    """
    # 检查请求类型
    assert scope['type'] == 'http'
    
    # 发送响应头
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })
    
    # 发送响应体
    await send({
        'type': 'http.response.body',
        'body': b'Hello World from Uvicorn!',
    })

# 如果直接运行这个文件，启动服务器
# if __name__ == "__main__":
#     import uvicorn
#     print("启动最简单的 Uvicorn 应用...")
#     print("访问: http://localhost:8000")
#     print("按 Ctrl+C 停止服务器")
#     uvicorn.run(simple_app, host="127.0.0.1", port=8000)

# ========================================
# 第四部分：使用 FastAPI 的实际例子
# ========================================

"""
通常我们会结合 FastAPI 使用 Uvicorn
"""

# 首先需要安装 FastAPI
# pip install fastapi

try:
    from fastapi import FastAPI
    
    # 创建 FastAPI 应用实例
    app = FastAPI(title="Uvicorn 教程", description="学习 Uvicorn 的基础用法")
    
    @app.get("/")
    async def read_root():
        """根路径 - 返回欢迎信息"""
        return {"message": "欢迎来到 Uvicorn 教程！"}
    
    @app.get("/hello/{name}")
    async def say_hello(name: str):
        """个性化问候"""
        return {"message": f"你好, {name}!"}
    
    @app.get("/items/{item_id}")
    async def read_item(item_id: int, q: str = None):
        """获取物品信息"""
        result = {"item_id": item_id}
        if q:
            result.update({"q": q})
        return result
    
    # 启动 FastAPI 应用的函数
    def run_fastapi_app():
        """启动 FastAPI 应用"""
        print("启动 FastAPI + Uvicorn 应用...")
        print("访问: http://localhost:8000")
        print("API 文档: http://localhost:8000/docs")
        print("按 Ctrl+C 停止服务器")
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

except ImportError:
    print("FastAPI 未安装，请运行: pip install fastapi")
    
    def run_fastapi_app():
        print("请先安装 FastAPI: pip install fastapi")

# ========================================
# 第五部分：常用配置选项
# ========================================

def demo_configurations():
    """演示不同的 Uvicorn 配置选项"""
    
    # 基本配置
    basic_config = {
        "host": "127.0.0.1",    # 监听地址
        "port": 8000,           # 监听端口
        "reload": True,         # 开发模式热重载
        "debug": True,          # 调试模式
    }
    
    # 生产环境配置
    production_config = {
        "host": "0.0.0.0",      # 监听所有接口
        "port": 80,             # 标准 HTTP 端口
        "workers": 4,           # 工作进程数
        "reload": False,        # 生产环境不要热重载
        "access_log": True,     # 访问日志
    }
    
    # SSL/HTTPS 配置
    ssl_config = {
        "host": "0.0.0.0",
        "port": 443,
        "ssl_keyfile": "path/to/keyfile.pem",
        "ssl_certfile": "path/to/certfile.pem",
    }
    
    print("配置选项示例：")
    print(f"基本配置: {basic_config}")
    print(f"生产环境配置: {production_config}")
    print(f"SSL配置: {ssl_config}")

# ========================================
# 第六部分：命令行使用方法
# ========================================

"""
命令行启动 Uvicorn 的不同方法：

1. 最简单的启动：
   uvicorn main:app
   
2. 指定主机和端口：
   uvicorn main:app --host 0.0.0.0 --port 8080
   
3. 开发模式（热重载）：
   uvicorn main:app --reload
   
4. 指定工作进程数：
   uvicorn main:app --workers 4
   
5. 启用调试模式：
   uvicorn main:app --debug
   
6. 指定日志级别：
   uvicorn main:app --log-level debug
   
7. 后台运行：
   nohup uvicorn main:app --host 0.0.0.0 --port 8000 &

常用参数说明：
- main:app 表示 main.py 文件中的 app 对象
- --reload: 文件修改时自动重启（仅开发环境）
- --workers: 工作进程数（生产环境）
- --host: 监听地址
- --port: 监听端口
- --debug: 调试模式
- --log-level: 日志级别 (critical, error, warning, info, debug, trace)
"""

# ========================================
# 第七部分：实际应用示例
# ========================================

def create_production_server():
    """创建生产环境服务器配置"""
    
    # 这是一个生产环境的配置示例
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 4,               # 根据 CPU 核心数调整
        "worker_class": "uvicorn.workers.UvicornWorker",
        "keepalive": 2,
        "max_requests": 1000,       # 每个工作进程处理的最大请求数
        "max_requests_jitter": 100,
        "timeout": 30,
        "access_log": True,
        "error_log": True,
    }
    
    return config

def development_server():
    """开发环境服务器配置"""
    
    config = {
        "host": "127.0.0.1",
        "port": 8000,
        "reload": True,             # 文件修改自动重启
        "debug": True,              # 调试模式
        "log_level": "debug",       # 详细日志
        "access_log": True,
    }
    
    return config

# ========================================
# 第八部分：错误处理和日志
# ========================================

import logging

def setup_logging():
    """设置日志配置"""
    
    # 创建日志器
    logger = logging.getLogger("uvicorn_tutorial")
    logger.setLevel(logging.INFO)
    
    # 创建处理器
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # 添加处理器到日志器
    logger.addHandler(handler)
    
    return logger

# ========================================
# 第九部分：性能优化建议
# ========================================

"""
Uvicorn 性能优化建议：

1. 生产环境使用多工作进程：
   uvicorn main:app --workers 4

2. 安装性能依赖：
   pip install "uvicorn[standard]"

3. 使用 Gunicorn + Uvicorn 工作器：
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

4. 配置适当的超时设置：
   --timeout-keep-alive 2

5. 启用访问日志（可选）：
   --access-log

6. 在反向代理后面运行（推荐）：
   nginx + uvicorn
"""

# ========================================
# 主程序入口
# ========================================

def main():
    """主程序"""
    print("=" * 50)
    print("Uvicorn 基础教程")
    print("=" * 50)
    print()
    
    print("选择要运行的示例：")
    print("1. 最简单的 ASGI 应用")
    print("2. FastAPI 应用")
    print("3. 查看配置示例")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ")
    
    if choice == "1":
        print("\n启动最简单的 ASGI 应用...")
        uvicorn.run(simple_app, host="127.0.0.1", port=8000)
    elif choice == "2":
        run_fastapi_app()
    elif choice == "3":
        demo_configurations()
    elif choice == "4":
        print("再见！")
    else:
        print("无效选择，请重新运行程序")

if __name__ == "__main__":
    # 检查是否安装了 uvicorn
    try:
        import uvicorn
        main()
    except ImportError:
        print("Uvicorn 未安装！")
        print("请运行以下命令安装：")
        print("pip install 'uvicorn[standard]'")
