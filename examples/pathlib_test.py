from pathlib import Path

def decorator(func):
    def wrapper():
        print("函数被调用之前执行")
        func()
        print("函数被调用之后执行")
    return wrapper # 返回一个新的函数

class MyPath:
    def __init__(self, my_path):
        self.my_path = my_path

    def path_test(self):
        print(Path(self.my_path).exists())

    @staticmethod
    def test1():
        print("staticmethod")

    @staticmethod
    @decorator
    def test2():
        print("two decorator")

my_path = MyPath(".")
my_path.path_test()

if __name__ == '__main__':
    MyPath.test2()
