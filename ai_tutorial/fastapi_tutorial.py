"""
FastAPI + Uvicorn 实践示例
=========================

这是一个简单的 FastAPI 应用示例，配合 Uvicorn 服务器运行。
运行命令：uvicorn fastapi_demo:app --reload

作者：AI助手
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI(
    title="Uvicorn 教程 API",
    description="学习 FastAPI 和 Uvicorn 的示例应用",
    version="1.0.0"
)

# 数据模型
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float

class User(BaseModel):
    id: int
    username: str
    email: str

# 模拟数据库
fake_items_db = [
    {"id": 1, "name": "苹果", "description": "新鲜的红苹果", "price": 3.5},
    {"id": 2, "name": "香蕉", "description": "黄色香蕉", "price": 2.0},
    {"id": 3, "name": "橙子", "description": "多汁的橙子", "price": 4.0},
]

fake_users_db = [
    {"id": 1, "username": "张三", "email": "zhangsan@example.com"},
    {"id": 2, "username": "李四", "email": "lisi@example.com"},
]

# ========================================
# 路由定义
# ========================================

@app.get("/")
async def root():
    """首页 - 欢迎信息"""
    return {
        "message": "欢迎来到 FastAPI + Uvicorn 教程！",
        "description": "这是一个学习示例",
        "endpoints": {
            "文档": "/docs",
            "物品列表": "/items",
            "用户列表": "/users",
            "健康检查": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "健康", "message": "服务器运行正常"}

# ========================================
# 物品相关接口
# ========================================

# @app.get("/items", response_model=List[Item])
# async def get_items():
#     """获取所有物品"""
#     return fake_items_db

@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """根据ID获取特定物品"""
    for item in fake_items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="物品未找到")

@app.post("/items", response_model=Item)
async def create_item(item: Item):
    """创建新物品"""
    # 检查ID是否已存在
    for existing_item in fake_items_db:
        if existing_item["id"] == item.id:
            raise HTTPException(status_code=400, detail="物品ID已存在")
    
    # 添加到"数据库"
    item_dict = item.dict()
    fake_items_db.append(item_dict)
    return item_dict

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """更新物品信息"""
    for i, existing_item in enumerate(fake_items_db):
        if existing_item["id"] == item_id:
            item_dict = item.dict()
            item_dict["id"] = item_id  # 确保ID一致
            fake_items_db[i] = item_dict
            return item_dict
    raise HTTPException(status_code=404, detail="物品未找到")

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """删除物品"""
    for i, item in enumerate(fake_items_db):
        if item["id"] == item_id:
            deleted_item = fake_items_db.pop(i)
            return {"message": f"物品 '{deleted_item['name']}' 已删除"}
    raise HTTPException(status_code=404, detail="物品未找到")

# ========================================
# 用户相关接口
# ========================================

@app.get("/users", response_model=List[User])
async def get_users():
    """获取所有用户"""
    return fake_users_db

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """根据ID获取特定用户"""
    for user in fake_users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="用户未找到")

# ========================================
# 查询参数示例
# ========================================

@app.get("/search/items")
async def search_items(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """搜索物品（演示查询参数）"""
    results = fake_items_db.copy()
    
    # 按名称搜索
    if q:
        results = [item for item in results if q.lower() in item["name"].lower()]
    
    # 按价格范围过滤
    if min_price is not None:
        results = [item for item in results if item["price"] >= min_price]
    
    if max_price is not None:
        results = [item for item in results if item["price"] <= max_price]
    
    return {
        "query": q,
        "price_range": {"min": min_price, "max": max_price},
        "results": results,
        "count": len(results)
    }

# ========================================
# 启动配置
# ========================================

if __name__ == "__main__":
    print("启动 FastAPI 应用...")
    print("访问地址：")
    print("- 主页: http://localhost:8000")
    print("- API 文档: http://localhost:8000/docs")
    print("- 替代文档: http://localhost:8000/redoc")
    print("\n按 Ctrl+C 停止服务器")
    
    # 开发环境配置
    uvicorn.run(
        "fastapi_demo:app",  # 应用模块:应用对象
        host="127.0.0.1",    # 主机
        port=8000,           # 端口
        reload=True,         # 热重载
        debug=True,          # 调试模式
        log_level="info"     # 日志级别
    )
