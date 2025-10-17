import copy

print("=" * 60)
print("Python 浅拷贝(Shallow Copy) vs 深拷贝(Deep Copy) 教学案例")
print("=" * 60)

# ==================== 案例1: 简单列表(一维) ====================
print("\n【案例1】简单列表的拷贝")
print("-" * 60)

original_list = [1, 2, 3, 4, 5]
shallow_copy = original_list.copy()  # 或者 list(original_list) 或 original_list[:]
deep_copy = copy.deepcopy(original_list)

print(f"原始列表: {original_list}")
print(f"浅拷贝: {shallow_copy}")
print(f"深拷贝: {deep_copy}")

# 修改浅拷贝
shallow_copy[0] = 999
print(f"\n修改浅拷贝后:")
print(f"原始列表: {original_list}  ← 不受影响")
print(f"浅拷贝: {shallow_copy}  ← 已修改")

print("\n💡 结论: 对于简单数据类型,浅拷贝和深拷贝效果相同")

# ==================== 案例2: 嵌套列表(多维) ====================
print("\n\n【案例2】嵌套列表的拷贝 - 关键区别!")
print("-" * 60)

original_nested = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
shallow_copy_nested = original_nested.copy()
deep_copy_nested = copy.deepcopy(original_nested)

print(f"原始列表: {original_nested}")
print(f"浅拷贝: {shallow_copy_nested}")
print(f"深拷贝: {deep_copy_nested}")

# 修改浅拷贝中的嵌套对象
print("\n--- 修改浅拷贝中的嵌套列表 ---")
shallow_copy_nested[0][0] = 999
print(f"原始列表: {original_nested}  ← 被影响了!")
print(f"浅拷贝: {shallow_copy_nested}  ← 已修改")
print(f"深拷贝: {deep_copy_nested}  ← 不受影响")

print("\n⚠️  关键区别: 浅拷贝只复制外层容器,内层对象仍是引用!")

# 修改深拷贝
print("\n--- 修改深拷贝中的嵌套列表 ---")
deep_copy_nested[1][1] = 888
print(f"原始列表: {original_nested}  ← 不受影响")
print(f"深拷贝: {deep_copy_nested}  ← 已修改")

# ==================== 案例3: 包含对象的列表 ====================
print("\n\n【案例3】包含对象的列表")
print("-" * 60)


class Student:
    def __init__(self, name, scores):
        self.name = name
        self.scores = scores

    def __repr__(self):
        return f"Student('{self.name}', {self.scores})"


students = [
    Student("张三", [85, 90, 88]),
    Student("李四", [92, 87, 95])
]

shallow_students = students.copy()
deep_students = copy.deepcopy(students)

print(f"原始学生列表:\n{students}")

# 修改浅拷贝中的对象属性
print("\n--- 修改浅拷贝中学生的成绩 ---")
shallow_students[0].scores[0] = 100
print(f"原始列表: {students[0]}  ← 被影响了!")
print(f"浅拷贝: {shallow_students[0]}  ← 已修改")
print(f"深拷贝: {deep_students[0]}  ← 不受影响")

# 修改深拷贝
print("\n--- 修改深拷贝中学生的成绩 ---")
deep_students[1].scores[0] = 100
print(f"原始列表: {students[1]}  ← 不受影响")
print(f"深拷贝: {deep_students[1]}  ← 已修改")

# ==================== 案例4: 字典的拷贝 ====================
print("\n\n【案例4】字典的拷贝")
print("-" * 60)

original_dict = {
    'name': '小明',
    'age': 20,
    'courses': ['Python', 'Java', 'C++'],
    'address': {'city': '北京', 'district': '海淀'}
}

shallow_dict = original_dict.copy()
deep_dict = copy.deepcopy(original_dict)

print(f"原始字典: {original_dict}")

# 修改浅拷贝中的嵌套对象
print("\n--- 修改浅拷贝中的嵌套列表和字典 ---")
shallow_dict['courses'].append('Go')
shallow_dict['address']['district'] = '朝阳'

print(f"原始字典: {original_dict}")
print(f"  ↑ courses和address都被修改了!")
print(f"浅拷贝: {shallow_dict}")

# 修改深拷贝
print("\n--- 修改深拷贝 ---")
deep_dict['courses'].append('Rust')
deep_dict['address']['city'] = '上海'

print(f"原始字典: {original_dict}  ← 不受影响")
print(f"深拷贝: {deep_dict}  ← 已修改")

# ==================== 总结 ====================
print("\n\n" + "=" * 60)
print("📚 核心总结")
print("=" * 60)
print("""
1. 浅拷贝 (Shallow Copy):
   - 创建新容器,但内部元素仍是原对象的引用
   - 方法: list.copy(), dict.copy(), copy.copy()
   - 适用场景: 简单数据类型的列表/字典

2. 深拷贝 (Deep Copy):
   - 递归复制所有层级的对象,完全独立
   - 方法: copy.deepcopy()
   - 适用场景: 嵌套结构、包含可变对象

3. 记忆口诀:
   浅拷贝 = 复制容器,共享内容
   深拷贝 = 完全克隆,互不影响

4. 内存视角:
   浅拷贝: 新容器指向同一内存地址的对象
   深拷贝: 新容器指向全新内存地址的对象副本
""")

# ==================== 可视化辅助理解 ====================
print("\n" + "=" * 60)
print("🎨 可视化理解")
print("=" * 60)
print("""
原始列表: original = [[1, 2], [3, 4]]
                       ↓
        ┌──────────────┴──────────────┐
        │  外层列表容器               │
        │  [指向列表A, 指向列表B]     │
        └──────┬───────────┬──────────┘
               ↓           ↓
           列表A: [1,2]  列表B: [3,4]

浅拷贝: shallow = original.copy()
        ┌──────────────────────────────┐
        │  新的外层列表容器             │
        │  [指向列表A, 指向列表B]  ← 还是指向同一个列表!
        └──────┬───────────┬──────────┘
               ↓           ↓
           列表A: [1,2]  列表B: [3,4]  ← 共享!

深拷贝: deep = copy.deepcopy(original)
        ┌──────────────────────────────┐
        │  新的外层列表容器             │
        │  [指向列表A', 指向列表B']     │
        └──────┬───────────┬──────────┘
               ↓           ↓
         列表A': [1,2]  列表B': [3,4]  ← 全新副本!
""")

print("\n运行完成! 建议多次运行并修改代码来加深理解 🎓")