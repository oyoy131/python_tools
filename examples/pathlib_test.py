from pathlib import Path

LOCAL_FILE_PATH = Path(__file__).resolve()

def dir_iter():
    p = Path(".")
    return [x for x in p.iterdir() if x.is_dir()]

def path_absolute():
    x = Path("../resource/img")
    return [x.resolve(), x.absolute(), x.exists()]

def test1():
    temp_path = LOCAL_FILE_PATH.parents[1] / "resource"
    if temp_path.exists():
        print(temp_path)

def path_test():
    print([not not x.exists() for x in [x / "123.mp4" for x in LOCAL_FILE_PATH.parent.parent.iterdir()]])
    print(Path("queue_test.py").resolve())
    print(Path("../resource").exists())

def file_os_call():
    x = LOCAL_FILE_PATH.parents[1] / "storage" / "text_file" / "file1.txt"
    x.touch(exist_ok=True)
    x.write_text("Hello world!\nhow about the world", "utf-8")

# 添加批量重命名文件的函数
def rename_files_in_directory(directory_path):
    """
    将指定目录中的所有文件重命名为file_1, file_2等格式，保持原有扩展名
    
    Args:
        directory_path (str or Path): 目标文件夹路径
    """
    directory = Path(directory_path)
    
    # 检查目录是否存在
    if not directory.exists():
        raise FileNotFoundError(f"目录 {directory} 不存在")
    
    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} 不是一个有效的目录")
    
    # 获取目录中的所有文件（不包括子目录）
    files = [f for f in directory.iterdir() if f.is_file()]
    
    # 为每个文件生成新的名称并重命名
    for index, file_path in enumerate(files, start=1):
        # 获取文件的扩展名
        file_extension = file_path.suffix
        # 生成新文件名
        new_name = f"file_{index}{file_extension}"
        new_path = directory / new_name
        
        # 重命名文件
        file_path.rename(new_path)

if __name__ == "__main__":
    # file_os_call()
    # path_test()
    x = Path("../resource/img").resolve()
    rename_files_in_directory(x)
