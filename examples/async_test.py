import asyncio
import time
import datetime

async def count(xxx:str):
    """
    体现出事件循环和事件循环是以一个异步任务为单元，而不是一行代码
    事件循环：
    将多个异步任务包装成一个新的异步任务，运行后输出结果为（a b c a1 b1 c1）
    """
    print(f"{xxx}")
    await asyncio.sleep(1)
    print(f"{xxx}1")

async def task():
    await count("a")
    await count("b")
    await count("c")


async def main():
    # 协程将被包装成期程并被调度到事件循环中执行
    await asyncio.gather(count("a"),count("b"),count("c"))



if __name__ == "__main__":
    x = input(f"请输入x的值：\n")
    if x == "1":
        # 运行包装后的异步任务
        asyncio.run(main())
    elif x == "2":
        """
        RuntimeWarning: coroutine 'count' was never awaited count("a")
        RuntimeWarning: Enable tracemalloc to get the object allocation traceback
        
        这个错误信息表示你正在尝试调用一个协程(coroutine)函数count，但是没有使用await关键字来等待它的执行结果。
        在Python的异步编程中，当你定义一个使用async def关键字的函数时，这个函数就变成了一个协程函数。
        调用协程函数并不会直接执行它，而是返回一个协程对象，你必须使用await关键字来实际执行这个协程。
        """
        count("a")
        count("b")
        count("c")

    elif x == "3":
        """
        没有使用 gather() 函数
        多异步任务串行执行,未将它们安排到事件循环中并发执行
        """
        asyncio.run(task())

