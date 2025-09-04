#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python多线程教学案例
===================

本教程涵盖Python多线程的基础概念、实际应用和最佳实践
作者：AI Assistant
日期：2024
"""

import threading
import time
import queue
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)

# =============================================================================
# 1. 基础多线程概念演示
# =============================================================================

def basic_thread_example():
    """演示基本的线程创建和执行"""
    print("\n=== 基础多线程演示 ===")
    
    def worker(name, duration):
        """工作函数 - 模拟耗时操作"""
        print(f"线程 {name} 开始工作...")
        time.sleep(duration)
        print(f"线程 {name} 工作完成！耗时 {duration} 秒")
    
    # 方法1：直接创建Thread对象
    thread1 = threading.Thread(target=worker, args=("Worker-1", 2))
    thread2 = threading.Thread(target=worker, args=("Worker-2", 3))
    
    # 启动线程
    start_time = time.time()
    thread1.start()
    thread2.start()
    
    # 等待线程完成
    thread1.join()
    thread2.join()
    
    end_time = time.time()
    print(f"所有线程完成，总耗时: {end_time - start_time:.2f} 秒")
    print("注意：如果是顺序执行，应该需要5秒")


# =============================================================================
# 2. 线程类继承方式
# =============================================================================

class CustomThread(threading.Thread):
    """自定义线程类 - 继承Thread类"""
    
    def __init__(self, name, task_queue):
        super().__init__()
        self.name = name
        self.task_queue = task_queue
        self.daemon = True  # 设置为守护线程
    
    def run(self):
        """线程的主要执行逻辑"""
        while True:
            try:
                # 从队列获取任务，超时1秒
                task = self.task_queue.get(timeout=1)
                print(f"线程 {self.name} 处理任务: {task}")
                time.sleep(random.uniform(0.5, 2))  # 模拟处理时间
                self.task_queue.task_done()
            except queue.Empty:
                print(f"线程 {self.name} 超时退出")
                break


def thread_inheritance_example():
    """演示线程类继承方式"""
    print("\n=== 线程类继承演示 ===")
    
    # 创建任务队列
    task_queue = queue.Queue()
    
    # 添加任务
    for i in range(10):
        task_queue.put(f"任务-{i+1}")
    
    # 创建工作线程
    threads = []
    for i in range(3):
        thread = CustomThread(f"Worker-{i+1}", task_queue)
        threads.append(thread)
        thread.start()
    
    # 等待所有任务完成
    task_queue.join()
    print("所有任务处理完成！")


# =============================================================================
# 3. 线程同步 - Lock锁机制
# =============================================================================

# 共享资源
shared_counter = 0
counter_lock = threading.Lock()

def increment_counter(name, iterations):
    """增加计数器 - 演示线程安全"""
    global shared_counter
    
    for i in range(iterations):
        # 使用锁保证线程安全
        with counter_lock:
            current = shared_counter
            time.sleep(0.0001)  # 模拟处理时间，增加竞争条件概率
            shared_counter = current + 1
        
        if (i + 1) % 100 == 0:
            print(f"线程 {name} 已处理 {i + 1} 次")

def thread_synchronization_example():
    """演示线程同步机制"""
    print("\n=== 线程同步演示 ===")
    
    global shared_counter
    shared_counter = 0
    
    # 创建多个线程同时修改共享资源
    threads = []
    iterations_per_thread = 1000
    
    for i in range(5):
        thread = threading.Thread(
            target=increment_counter, 
            args=(f"Counter-{i+1}", iterations_per_thread)
        )
        threads.append(thread)
    
    start_time = time.time()
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    expected = len(threads) * iterations_per_thread
    
    print(f"期望计数器值: {expected}")
    print(f"实际计数器值: {shared_counter}")
    print(f"执行时间: {end_time - start_time:.2f} 秒")
    print("使用锁确保了线程安全！" if shared_counter == expected else "存在数据竞争！")


# =============================================================================
# 4. 生产者-消费者模式
# =============================================================================

def producer_consumer_example():
    """演示生产者-消费者模式"""
    print("\n=== 生产者-消费者模式演示 ===")
    
    # 创建有界队列
    buffer = queue.Queue(maxsize=5)
    
    def producer(name, item_count):
        """生产者函数"""
        for i in range(item_count):
            item = f"{name}-产品-{i+1}"
            buffer.put(item)
            print(f"生产者 {name} 生产了: {item}")
            time.sleep(random.uniform(0.1, 0.5))
        
        print(f"生产者 {name} 完成生产")
    
    def consumer(name):
        """消费者函数"""
        consumed_count = 0
        while True:
            try:
                item = buffer.get(timeout=2)
                print(f"消费者 {name} 消费了: {item}")
                consumed_count += 1
                time.sleep(random.uniform(0.2, 0.8))
                buffer.task_done()
            except queue.Empty:
                print(f"消费者 {name} 超时退出，共消费 {consumed_count} 个产品")
                break
    
    # 创建生产者线程
    producer_threads = []
    for i in range(2):
        thread = threading.Thread(target=producer, args=(f"P{i+1}", 5))
        producer_threads.append(thread)
        thread.start()
    
    # 创建消费者线程
    consumer_threads = []
    for i in range(3):
        thread = threading.Thread(target=consumer, args=(f"C{i+1}",))
        consumer_threads.append(thread)
        thread.start()
    
    # 等待生产者完成
    for thread in producer_threads:
        thread.join()
    
    # 等待所有产品被消费
    buffer.join()
    
    print("生产者-消费者演示完成！")


# =============================================================================
# 5. 线程池应用 - 网络请求并发处理
# =============================================================================

def fetch_url(url, timeout=5):
    """获取URL内容"""
    try:
        print(f"开始请求: {url}")
        response = requests.get(url, timeout=timeout)
        return {
            'url': url,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content)
        }
    except Exception as e:
        return {
            'url': url,
            'error': str(e)
        }

def thread_pool_example():
    """演示线程池的使用"""
    print("\n=== 线程池演示 ===")
    
    # 测试URL列表
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/2',
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://jsonplaceholder.typicode.com/posts/2',
        'https://httpbin.org/status/200',
    ]
    
    # 方法1：使用ThreadPoolExecutor
    print("使用线程池并发请求...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交所有任务
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        
        # 处理完成的任务
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if 'error' in result:
                    print(f"请求失败 {url}: {result['error']}")
                else:
                    print(f"请求成功 {url}: {result['status_code']}, "
                          f"耗时: {result['response_time']:.2f}s")
            except Exception as exc:
                print(f"请求异常 {url}: {exc}")
    
    end_time = time.time()
    print(f"线程池处理完成，总耗时: {end_time - start_time:.2f} 秒")


# =============================================================================
# 6. 线程本地存储
# =============================================================================

# 创建线程本地存储对象
thread_local_data = threading.local()

def init_thread_data(value):
    """初始化线程本地数据"""
    thread_local_data.value = value
    thread_local_data.counter = 0
    print(f"线程 {threading.current_thread().name} 初始化数据: {value}")

def process_thread_data():
    """处理线程本地数据"""
    thread_name = threading.current_thread().name
    
    for i in range(3):
        thread_local_data.counter += 1
        print(f"线程 {thread_name} - 值: {thread_local_data.value}, "
              f"计数器: {thread_local_data.counter}")
        time.sleep(0.5)

def thread_local_example():
    """演示线程本地存储"""
    print("\n=== 线程本地存储演示 ===")
    
    def worker(name, initial_value):
        init_thread_data(initial_value)
        process_thread_data()
    
    threads = []
    for i in range(3):
        thread = threading.Thread(
            target=worker, 
            args=(f"Worker-{i+1}", f"数据-{i+1}"),
            name=f"Worker-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("线程本地存储演示完成！")


# =============================================================================
# 7. 条件变量 (Condition)
# =============================================================================

def condition_example():
    """演示条件变量的使用"""
    print("\n=== 条件变量演示 ===")
    
    condition = threading.Condition()
    items = []
    
    def consumer(name):
        """消费者 - 等待条件满足"""
        with condition:
            while len(items) == 0:
                print(f"消费者 {name} 等待产品...")
                condition.wait()  # 等待条件
            
            item = items.pop(0)
            print(f"消费者 {name} 获得产品: {item}")
    
    def producer():
        """生产者 - 改变条件并通知"""
        for i in range(5):
            time.sleep(1)
            with condition:
                item = f"产品-{i+1}"
                items.append(item)
                print(f"生产者生产了: {item}")
                condition.notify()  # 通知等待的线程
    
    # 创建消费者线程
    consumers = []
    for i in range(3):
        thread = threading.Thread(target=consumer, args=(f"C{i+1}",))
        consumers.append(thread)
        thread.start()
    
    # 创建生产者线程
    producer_thread = threading.Thread(target=producer)
    producer_thread.start()
    
    # 等待完成
    producer_thread.join()
    for thread in consumers:
        thread.join()


# =============================================================================
# 8. 线程性能对比
# =============================================================================

def cpu_intensive_task(n):
    """CPU密集型任务"""
    result = 0
    for i in range(n):
        result += i * i
    return result

def io_intensive_task():
    """IO密集型任务"""
    time.sleep(0.1)  # 模拟IO等待
    return "IO任务完成"

def performance_comparison():
    """性能对比演示"""
    print("\n=== 性能对比演示 ===")
    
    # CPU密集型任务对比
    print("1. CPU密集型任务对比:")
    task_count = 4
    calculation_size = 1000000
    
    # 顺序执行
    start_time = time.time()
    for i in range(task_count):
        cpu_intensive_task(calculation_size)
    sequential_time = time.time() - start_time
    
    # 多线程执行
    start_time = time.time()
    threads = []
    for i in range(task_count):
        thread = threading.Thread(target=cpu_intensive_task, args=(calculation_size,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    threaded_time = time.time() - start_time
    
    print(f"顺序执行时间: {sequential_time:.2f} 秒")
    print(f"多线程执行时间: {threaded_time:.2f} 秒")
    print(f"线程效率: {sequential_time/threaded_time:.2f}x")
    print("注意：CPU密集型任务由于GIL限制，多线程可能不会带来性能提升")
    
    # IO密集型任务对比
    print("\n2. IO密集型任务对比:")
    io_task_count = 10
    
    # 顺序执行
    start_time = time.time()
    for i in range(io_task_count):
        io_intensive_task()
    sequential_io_time = time.time() - start_time
    
    # 多线程执行
    start_time = time.time()
    threads = []
    for i in range(io_task_count):
        thread = threading.Thread(target=io_intensive_task)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    threaded_io_time = time.time() - start_time
    
    print(f"顺序执行时间: {sequential_io_time:.2f} 秒")
    print(f"多线程执行时间: {threaded_io_time:.2f} 秒")
    print(f"线程效率: {sequential_io_time/threaded_io_time:.2f}x")
    print("注意：IO密集型任务多线程通常能带来显著性能提升")


# =============================================================================
# 9. 最佳实践和注意事项
# =============================================================================

def best_practices_demo():
    """最佳实践演示"""
    print("\n=== 最佳实践演示 ===")
    
    print("1. 使用上下文管理器确保资源释放:")
    lock = threading.Lock()
    
    def safe_operation():
        with lock:  # 推荐：使用with语句
            print("安全地访问共享资源")
            # 即使发生异常，锁也会被释放
    
    print("2. 设置守护线程避免程序挂起:")
    def daemon_worker():
        while True:
            print("守护线程工作中...")
            time.sleep(1)
    
    daemon_thread = threading.Thread(target=daemon_worker)
    daemon_thread.daemon = True  # 设置为守护线程
    # daemon_thread.start()  # 注释掉避免影响演示
    
    print("3. 使用线程池管理线程生命周期")
    print("4. 避免死锁 - 始终以相同顺序获取多个锁")
    print("5. 使用queue模块进行线程间通信")
    print("6. 适当使用线程本地存储避免锁竞争")


# =============================================================================
# 主函数 - 运行所有演示
# =============================================================================

def main():
    """主函数 - 运行所有演示案例"""
    print("Python多线程教学案例")
    print("=" * 50)
    
    try:
        # 运行各个演示
        basic_thread_example()
        thread_inheritance_example()
        thread_synchronization_example()
        producer_consumer_example()
        
        # 网络相关演示需要网络连接，可能失败
        try:
            thread_pool_example()
        except Exception as e:
            print(f"网络演示跳过 (需要网络连接): {e}")
        
        thread_local_example()
        condition_example()
        performance_comparison()
        best_practices_demo()
        
        print("\n" + "=" * 50)
        print("所有演示完成！")
        
        print("\n重要知识点总结:")
        print("1. Python的GIL(全局解释器锁)限制了CPU密集型任务的并发性能")
        print("2. 多线程适合IO密集型任务(文件读写、网络请求等)")
        print("3. 使用Lock、RLock、Condition等同步原语避免数据竞争")
        print("4. 线程池(ThreadPoolExecutor)简化线程管理")
        print("5. 生产者-消费者模式是常见的多线程设计模式")
        print("6. 线程本地存储避免共享状态的复杂性")
        print("7. 守护线程随主程序退出而退出")
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()
