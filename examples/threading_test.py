import threading
import time
from datetime import datetime

# 看懂这些代码的执行顺序
def callback():
    print("开始运行 callback")
    for i in range(3):
        time.sleep(1)
        print(i)

def print_numbers(param=callback()):
    print("开始运行 print_numbers")
    # for i in range(3):
    #     time.sleep(1)
    #     print(i)
    return param


if __name__ == "__main__":
    choice = input("test_number:")
    if choice == '1':
        # 创建线程
        thread = threading.Thread(target=print_numbers)
        thread1 = threading.Thread(target=print_numbers(callback()))

        # 启动线程
        print(datetime.now())
        thread.start()
        thread1.start()
        print("主线程同步运行中")
        # 等待线程结束
        thread.join()
        thread1.join()
        print("线程结束再执行以下代码")

    elif choice == '2':
        pass
    else:print("error")