from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="FastAPI 测试(标题修改)",
    description="一个 FastAPI 应用示例（描述修改）",
    version="0.1.0（版本修改）",
)

# 数据模型定义
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] =  None
    price: float
    is_available: bool

class User(BaseModel):
    id: int
    username: str
    email: str

fake_items_db = [
    {"id": 1, "name": "物品1", "description": "str类型的商品描述", "price": 10.99, "is_available": True},
    {"id": 2, "name": "物品2", "description": "str类型的商品描述", "price": 20.99, "is_available": False},
    {"id": 3, "name": "物品3", "description": "str类型的商品描述", "price": 30.99, "is_available": True},
    {"id": 4, "name": "物品4", "description": "str类型的商品描述", "price": 40.99, "is_available": False},
]

@app.get("/")
async def root():
    """首页 - 欢迎信息"""
    return {
        "message": "欢迎来到 FastAPI + Uvicorn 教程！",
        "description": "这是一个学习示例",
        "endpoints": {
            "文档": "/docs",
            "物品列表": "/items",
            "用户列表": "/users"
        }
    }


@app.get("/items", response_model=List[Item])
async def get_items():
    """获取物品列表(这里虽然是注释，但是可以修改，且会显示到web端)"""
    return fake_items_db

@app.get("/items/{items_id}", response_model=Item)
async def get_item(item_id: int):
    """获取指"""
    for item in fake_items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="物品未找到")


@app.post("/items", response_model=Item)
async def create_item(item:Item):
    """创建新物品"""
    # 检查ID是否已存在
    for existing_item in fake_items_db:
        if existing_item["id"] == item.id:
            raise HTTPException(status_code=400, detail="物品ID已存在")
    
    # 添加到"数据库"
    item_dict = item.model_dump()
    fake_items_db.append(item_dict)
    return item_dict

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    """更新物品信息"""
    for i, existing_item in enumerate(fake_items_db):
        if existing_item["id"] == item_id:
            item_dict = item.model_dump()
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