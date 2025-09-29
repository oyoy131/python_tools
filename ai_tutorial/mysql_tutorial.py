#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python + MySQL 完整教学案例
主题：电商店铺数据管理系统

涵盖内容：
1. 数据库连接与基础操作
2. 表设计与创建
3. 数据插入、查询、更新、删除
4. 索引设计与优化
5. 事务处理
6. 连接查询
7. 性能优化
8. 实际应用场景

环境要求：
pip install pymysql sqlalchemy pandas
"""

import pymysql
import json
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import pandas as pd


class ShopDatabase:
    def __init__(self, host='localhost', user='root', password='root', database='shop_demo'):
        """
        初始化数据库连接
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        try:
            # 首先连接到MySQL服务器（不指定数据库）
            temp_conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )

            # 创建数据库（如果不存在）
            with temp_conn.cursor() as cursor:
                # noinspection SqlNoDataSourceInspection
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database} CHARACTER SET utf8mb4")
            temp_conn.commit()
            temp_conn.close()

            # 连接到指定数据库
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                autocommit=False  # 关闭自动提交，便于事务演示
            )
            print(f"✅ 成功连接到数据库 {self.database}")

        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")

    def create_tables(self):
        """
        创建表结构
        演示：表设计、字段类型、约束条件
        """
        cursor = self.connection.cursor()

        # 1. 创建店铺表
        shop_table = """
        CREATE TABLE IF NOT EXISTS shops (
            id INT PRIMARY KEY AUTO_INCREMENT,
            shop_name VARCHAR(100) NOT NULL COMMENT '店铺名称',
            owner_name VARCHAR(50) NOT NULL COMMENT '店主姓名',
            category ENUM('餐饮', '服装', '电子', '书店', '其他') NOT NULL COMMENT '店铺类别',
            address TEXT NOT NULL COMMENT '店铺地址',
            phone VARCHAR(20) COMMENT '联系电话',
            email VARCHAR(100) COMMENT '邮箱',
            rating DECIMAL(3,2) DEFAULT 0.00 COMMENT '评分(0-5)',
            monthly_sales INT DEFAULT 0 COMMENT '月销售额',
            status ENUM('营业', '暂停', '关闭') DEFAULT '营业' COMMENT '营业状态',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='店铺信息表';
        """

        # 2. 创建商品表
        product_table = """
        CREATE TABLE IF NOT EXISTS products (
            id INT PRIMARY KEY AUTO_INCREMENT,
            shop_id INT NOT NULL COMMENT '店铺ID',
            product_name VARCHAR(200) NOT NULL COMMENT '商品名称',
            description TEXT COMMENT '商品描述',
            price DECIMAL(10,2) NOT NULL COMMENT '商品价格',
            stock INT DEFAULT 0 COMMENT '库存数量',
            category VARCHAR(50) COMMENT '商品分类',
            image_urls JSON COMMENT '商品图片URLs',
            is_active BOOLEAN DEFAULT TRUE COMMENT '是否上架',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品信息表';
        """

        # 3. 创建订单表
        order_table = """
        CREATE TABLE IF NOT EXISTS orders (
            id INT PRIMARY KEY AUTO_INCREMENT,
            shop_id INT NOT NULL COMMENT '店铺ID',
            product_id INT NOT NULL COMMENT '商品ID',
            customer_name VARCHAR(50) NOT NULL COMMENT '客户姓名',
            quantity INT NOT NULL COMMENT '购买数量',
            unit_price DECIMAL(10,2) NOT NULL COMMENT '单价',
            total_amount DECIMAL(10,2) NOT NULL COMMENT '总金额',
            order_status ENUM('待付款', '已付款', '已发货', '已完成', '已取消') DEFAULT '待付款',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';
        """

        # PyMySQL的游标清理机制
        # 连接关闭时：当 connection.close() 被调用时，所有关联的游标会被自动清理
        # 垃圾回收：Python的垃圾回收器最终也会清理游标对象
        # 但是：这不是最佳实践，可能导致临时资源浪费

        try:
            cursor.execute(shop_table)
            cursor.execute(product_table)
            cursor.execute(order_table)
            self.connection.commit()
            print("✅ 数据表创建完成")
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            self.connection.rollback()

    def create_indexes(self):
        """
        创建索引
        演示：普通索引、唯一索引、复合索引、全文索引
        """
        cursor = self.connection.cursor()

        indexes = [
            # 1. 为店铺名创建唯一索引（业务逻辑：店铺名不能重复）
            "CREATE UNIQUE INDEX idx_shop_name ON shops(shop_name)",

            # 2. 为店铺类别创建普通索引（经常按类别查询）
            "CREATE INDEX idx_shop_category ON shops(category)",

            # 3. 为评分创建索引（经常按评分排序）
            "CREATE INDEX idx_shop_rating ON shops(rating DESC)",

            # 4. 为店铺状态和创建时间创建复合索引
            "CREATE INDEX idx_shop_status_created ON shops(status, created_at)",

            # 5. 为商品表的店铺ID创建索引（外键查询优化）
            "CREATE INDEX idx_product_shop_id ON products(shop_id)",

            # 6. 为商品价格创建索引
            "CREATE INDEX idx_product_price ON products(price)",

            # 7. 为商品名创建全文索引（支持中文搜索需要配置）
            "CREATE INDEX idx_product_name_fulltext ON products(product_name)",

            # 8. 为订单日期创建索引
            "CREATE INDEX idx_order_date ON orders(order_date)",

            # 9. 为订单状态创建索引
            "CREATE INDEX idx_order_status ON orders(order_status)"
        ]

        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ 索引创建成功: {index_sql.split()[-1]}")
            except pymysql.Error as e:
                if "Duplicate key name" in str(e):
                    print(f"⚠️ 索引已存在: {index_sql.split()[-1]}")
                else:
                    print(f"❌ 索引创建失败: {e}")

        self.connection.commit()

    def insert_sample_data(self):
        """
        插入示例数据
        演示：批量插入、事务处理、JSON数据处理
        """
        cursor = self.connection.cursor()

        try:
            # 开始事务
            self.connection.begin()

            # 插入店铺数据
            shops_data = [
                ('张三的小餐馆', '张三', '餐饮', '北京市朝阳区xxx街道123号', '13800138000', 'zhangsan@email.com', 4.5, 15000),
                ('李四服装店', '李四', '服装', '上海市徐汇区xxx路456号', '13900139000', 'lisi@email.com', 4.2, 25000),
                ('王五电子城', '王五', '电子', '广州市天河区xxx大道789号', '13700137000', 'wangwu@email.com', 4.8, 50000),
                ('赵六书店', '赵六', '书店', '深圳市南山区xxx街101号', '13600136000', 'zhaoliu@email.com', 4.3, 8000),
                ('小明便利店', '小明', '其他', '成都市武侯区xxx路202号', '13500135000', 'xiaoming@email.com', 4.0, 12000)
            ]

            shop_sql = """
            INSERT INTO shops (shop_name, owner_name, category, address, phone, email, rating, monthly_sales)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(shop_sql, shops_data)

            # 获取插入的店铺ID用于商品插入
            cursor.execute("SELECT id, shop_name FROM shops")
            shop_ids = {name: id for id, name in cursor.fetchall()}

            # 插入商品数据（包含JSON字段）
            products_data = [
                (shop_ids['张三的小餐馆'], '宫保鸡丁', '经典川菜，香辣可口', 28.00, 100, '川菜',
                 json.dumps(['http://example.com/img1.jpg', 'http://example.com/img2.jpg'])),
                (shop_ids['张三的小餐馆'], '麻婆豆腐', '嫩滑豆腐配麻辣汤汁', 22.00, 50, '川菜',
                 json.dumps(['http://example.com/img3.jpg'])),
                (shop_ids['李四服装店'], '休闲T恤', '纯棉材质，舒适透气', 89.00, 200, '上衣',
                 json.dumps(['http://example.com/tshirt1.jpg', 'http://example.com/tshirt2.jpg'])),
                (shop_ids['李四服装店'], '牛仔裤', '经典款式，百搭单品', 199.00, 150, '裤装',
                 json.dumps(['http://example.com/jeans1.jpg'])),
                (shop_ids['王五电子城'], 'iPhone 15', '最新款苹果手机', 6999.00, 30, '手机',
                 json.dumps(['http://example.com/iphone1.jpg', 'http://example.com/iphone2.jpg',
                             'http://example.com/iphone3.jpg'])),
                (shop_ids['赵六书店'], 'Python编程入门', '适合初学者的编程书籍', 59.00, 80, '编程',
                 json.dumps(['http://example.com/book1.jpg'])),
                (shop_ids['小明便利店'], '矿泉水', '优质饮用水', 2.00, 1000, '饮料',
                 json.dumps(['http://example.com/water.jpg']))
            ]

            product_sql = """
            INSERT INTO products (shop_id, product_name, description, price, stock, category, image_urls)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(product_sql, products_data)

            # 插入订单数据
            cursor.execute("SELECT id FROM products")
            product_ids = [row[0] for row in cursor.fetchall()]

            orders_data = []
            for i in range(20):  # 创建20个示例订单
                shop_id = (i % 5) + 1  # 循环分配给不同店铺
                product_id = product_ids[i % len(product_ids)]
                quantity = (i % 5) + 1
                unit_price = 50.00 + (i * 10)
                total_amount = unit_price * quantity

                orders_data.append((
                    shop_id, product_id, f'客户{i + 1}', quantity, unit_price, total_amount,
                    ['待付款', '已付款', '已发货', '已完成'][i % 4]
                ))

            order_sql = """
            INSERT INTO orders (shop_id, product_id, customer_name, quantity, unit_price, total_amount, order_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(order_sql, orders_data)

            # 提交事务
            self.connection.commit()
            print("✅ 示例数据插入成功")

        except Exception as e:
            # 出错时回滚事务
            self.connection.rollback()
            print(f"❌ 数据插入失败，事务已回滚: {e}")

    def query_examples(self):
        """
        查询示例
        演示：基础查询、条件查询、排序、分组、聚合函数
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)  # 使用字典游标

        print("\n" + "=" * 50)
        print("查询示例演示")
        print("=" * 50)

        # 1. 基础查询
        print("\n1. 查询所有店铺信息：")
        cursor.execute("SELECT shop_name, category, rating, monthly_sales FROM shops")
        shops = cursor.fetchall()
        for shop in shops:
            print(
                f"  {shop['shop_name']} | {shop['category']} | 评分:{shop['rating']} | 月销售:{shop['monthly_sales']}")

        # 2. 条件查询
        print("\n2. 查询评分大于4.0的餐饮店铺：")
        cursor.execute("""
            SELECT shop_name, rating, address 
            FROM shops 
            WHERE category = '餐饮' AND rating > 4.0
        """)
        for shop in cursor.fetchall():
            print(f"  {shop['shop_name']} | 评分:{shop['rating']}")

        # 3. 排序查询
        print("\n3. 按月销售额降序排列的前3名店铺：")
        cursor.execute("""
            SELECT shop_name, monthly_sales, category 
            FROM shops 
            ORDER BY monthly_sales DESC 
            LIMIT 3
        """)
        for i, shop in enumerate(cursor.fetchall(), 1):
            print(f"  第{i}名: {shop['shop_name']} | 销售额:{shop['monthly_sales']}")

        # 4. 聚合查询
        print("\n4. 各类别店铺的统计信息：")
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) as shop_count,
                AVG(rating) as avg_rating,
                SUM(monthly_sales) as total_sales
            FROM shops
            GROUP BY category
            ORDER BY total_sales DESC
        """)
        for stat in cursor.fetchall():
            print(
                f"  {stat['category']}: 店铺数={stat['shop_count']}, 平均评分={stat['avg_rating']:.2f}, 总销售额={stat['total_sales']}")

        # 5. JSON字段查询
        print("\n5. 查询有多张图片的商品：")
        cursor.execute("""
            SELECT product_name, price, JSON_LENGTH(image_urls) as image_count
            FROM products 
            WHERE JSON_LENGTH(image_urls) > 1
        """)
        for product in cursor.fetchall():
            print(f"  {product['product_name']} | 价格:{product['price']} | 图片数:{product['image_count']}")

    def join_examples(self):
        """
        连接查询示例
        演示：INNER JOIN、LEFT JOIN、子查询
        """
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        print("\n" + "=" * 50)
        print("连接查询演示")
        print("=" * 50)

        # 1. 内连接：查询店铺及其商品信息
        print("\n1. 每个店铺的商品信息：")
        cursor.execute("""
            SELECT 
                s.shop_name,
                s.category as shop_category,
                p.product_name,
                p.price,
                p.stock
            FROM shops s
            INNER JOIN products p ON s.id = p.shop_id
            ORDER BY s.shop_name, p.price DESC
        """)

        current_shop = None
        for row in cursor.fetchall():
            if current_shop != row['shop_name']:
                current_shop = row['shop_name']
                print(f"\n  【{current_shop}】({row['shop_category']})")
            print(f"    - {row['product_name']}: ¥{row['price']} (库存:{row['stock']})")

        # 2. 左连接：查询店铺及订单统计（包括没有订单的店铺）
        print("\n2. 店铺订单统计（包括无订单店铺）：")
        cursor.execute("""
            SELECT 
                s.shop_name,
                s.rating,
                COUNT(o.id) as order_count,
                COALESCE(SUM(o.total_amount), 0) as total_revenue
            FROM shops s
            LEFT JOIN orders o ON s.id = o.shop_id
            GROUP BY s.id, s.shop_name, s.rating
            ORDER BY total_revenue DESC
        """)

        for shop in cursor.fetchall():
            print(
                f"  {shop['shop_name']} | 评分:{shop['rating']} | 订单数:{shop['order_count']} | 总收入:{shop['total_revenue']}")

        # 3. 复杂连接：查询高价值订单详情
        print("\n3. 高价值订单详情（订单金额>100）：")
        cursor.execute("""
            SELECT 
                s.shop_name,
                p.product_name,
                o.customer_name,
                o.quantity,
                o.unit_price,
                o.total_amount,
                o.order_status,
                DATE(o.order_date) as order_date
            FROM orders o
            INNER JOIN shops s ON o.shop_id = s.id
            INNER JOIN products p ON o.product_id = p.id
            WHERE o.total_amount > 100
            ORDER BY o.total_amount DESC
        """)

        for order in cursor.fetchall():
            print(
                f"  {order['shop_name']} | {order['product_name']} | 客户:{order['customer_name']} | 金额:{order['total_amount']} | {order['order_status']}")

    def transaction_example(self):
        """
        事务处理示例
        演示：事务的ACID特性、回滚、并发控制
        """
        print("\n" + "=" * 50)
        print("事务处理演示")
        print("=" * 50)

        cursor = self.connection.cursor()

        try:
            # 场景：客户购买商品，需要同时更新库存和创建订单
            print("\n模拟购买商品的事务处理...")

            # 开始事务
            self.connection.begin()

            # 1. 查询商品信息和库存
            product_id = 1
            buy_quantity = 5

            cursor.execute("SELECT product_name, price, stock FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product:
                raise Exception("商品不存在")

            product_name, price, current_stock = product
            print(f"购买商品: {product_name} | 当前库存: {current_stock} | 购买数量: {buy_quantity}")

            if current_stock < buy_quantity:
                raise Exception(f"库存不足！当前库存: {current_stock}, 需要: {buy_quantity}")

            # 2. 减少库存
            new_stock = current_stock - buy_quantity
            cursor.execute("UPDATE products SET stock = %s WHERE id = %s", (new_stock, product_id))
            print(f"✅ 库存更新: {current_stock} -> {new_stock}")

            # 3. 创建订单
            total_amount = price * buy_quantity
            cursor.execute("""
                INSERT INTO orders (shop_id, product_id, customer_name, quantity, unit_price, total_amount, order_status)
                VALUES ((SELECT shop_id FROM products WHERE id = %s), %s, %s, %s, %s, %s, %s)
            """, (product_id, product_id, "事务测试客户", buy_quantity, price, total_amount, "已付款"))

            print(f"✅ 订单创建: 数量{buy_quantity} | 总金额¥{total_amount}")

            # 4. 提交事务
            self.connection.commit()
            print("✅ 事务提交成功！")

        except Exception as e:
            # 回滚事务
            self.connection.rollback()
            print(f"❌ 事务执行失败，已回滚: {e}")

        # 演示事务回滚
        print("\n演示事务回滚...")
        try:
            self.connection.begin()

            # 故意制造一个错误（违反约束）
            cursor.execute("INSERT INTO shops (shop_name, owner_name, category, address) VALUES (%s, %s, %s, %s)",
                           ("张三的小餐馆", "张三", "餐饮", "测试地址"))  # 违反唯一索引约束

            self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            print(f"✅ 捕获异常并回滚: {e}")

    def index_performance_test(self):
        """
        索引性能测试
        演示：有索引vs无索引的查询性能差异
        """
        print("\n" + "=" * 50)
        print("索引性能测试")
        print("=" * 50)

        cursor = self.connection.cursor()

        # 1. 测试有索引的查询
        print("\n1. 测试索引查询性能...")

        # 按店铺名查询（有唯一索引）
        start_time = time.time()
        cursor.execute("SELECT * FROM shops WHERE shop_name = '张三的小餐馆'")
        result = cursor.fetchall()
        end_time = time.time()
        print(f"按店铺名查询（有索引）: {(end_time - start_time) * 1000:.2f}ms | 结果数: {len(result)}")

        # 按评分查询（有索引）
        start_time = time.time()
        cursor.execute("SELECT * FROM shops WHERE rating > 4.0")
        result = cursor.fetchall()
        end_time = time.time()
        print(f"按评分查询（有索引）: {(end_time - start_time) * 1000:.2f}ms | 结果数: {len(result)}")

        # 2. 查看查询执行计划
        print("\n2. 查询执行计划分析:")

        # 分析有索引的查询
        cursor.execute("EXPLAIN SELECT * FROM shops WHERE shop_name = '张三的小餐馆'")
        explain_result = cursor.fetchall()
        print("有索引的查询计划:")
        for row in explain_result:
            print(f"  类型: {row[1]} | 可能的键: {row[3]} | 使用的键: {row[4]} | 扫描行数: {row[8]}")

        # 分析表扫描查询
        cursor.execute("EXPLAIN SELECT * FROM shops WHERE phone LIKE '138%'")
        explain_result = cursor.fetchall()
        print("无索引的查询计划:")
        for row in explain_result:
            print(f"  类型: {row[1]} | 可能的键: {row[3]} | 使用的键: {row[4]} | 扫描行数: {row[8]}")

    def optimization_examples(self):
        """
        查询优化示例
        演示：慢查询优化、索引优化建议
        """
        print("\n" + "=" * 50)
        print("查询优化示例")
        print("=" * 50)

        cursor = self.connection.cursor()

        # 1. 优化前：低效的查询
        print("\n1. 查询优化对比:")

        # 低效查询：使用子查询
        start_time = time.time()
        cursor.execute("""
            SELECT * FROM shops 
            WHERE id IN (
                SELECT shop_id FROM products WHERE price > 100
            )
        """)
        result1 = cursor.fetchall()
        time1 = (time.time() - start_time) * 1000

        # 优化后：使用JOIN
        start_time = time.time()
        cursor.execute("""
            SELECT DISTINCT s.* FROM shops s
            INNER JOIN products p ON s.id = p.shop_id
            WHERE p.price > 100
        """)
        result2 = cursor.fetchall()
        time2 = (time.time() - start_time) * 1000

        print(f"子查询方式: {time1:.2f}ms | 结果数: {len(result1)}")
        print(f"JOIN方式: {time2:.2f}ms | 结果数: {len(result2)}")
        print(f"性能提升: {((time1 - time2) / time1 * 100):.1f}%")

        # 2. 索引使用建议
        print("\n2. 查看索引使用情况:")
        cursor.execute("SHOW INDEX FROM shops")
        indexes = cursor.fetchall()

        print("shops表的索引:")
        for idx in indexes:
            print(f"  索引名: {idx[2]} | 列名: {idx[4]} | 唯一性: {'是' if idx[1] == 0 else '否'}")

    def practical_scenarios(self):
        """
        实际应用场景
        演示：分页查询、数据统计、报表生成
        """
        print("\n" + "=" * 50)
        print("实际应用场景演示")
        print("=" * 50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        # 1. 分页查询
        print("\n1. 分页查询示例:")
        page_size = 3
        page_num = 1
        offset = (page_num - 1) * page_size

        cursor.execute("""
            SELECT shop_name, rating, monthly_sales 
            FROM shops 
            ORDER BY monthly_sales DESC 
            LIMIT %s OFFSET %s
        """, (page_size, offset))

        print(f"第{page_num}页（每页{page_size}条）:")
        for i, shop in enumerate(cursor.fetchall(), offset + 1):
            print(f"  {i}. {shop['shop_name']} | 评分:{shop['rating']} | 销售:{shop['monthly_sales']}")

        # 2. 销售统计报表
        print("\n2. 月度销售报表:")
        cursor.execute("""
            SELECT 
                s.shop_name,
                s.category,
                COUNT(o.id) as order_count,
                SUM(o.total_amount) as total_revenue,
                AVG(o.total_amount) as avg_order_value
            FROM shops s
            LEFT JOIN orders o ON s.id = o.shop_id 
                AND o.order_status IN ('已付款', '已发货', '已完成')
            GROUP BY s.id, s.shop_name, s.category
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
        """)

        print(f"{'店铺名称':<15} {'类别':<8} {'订单数':<8} {'总收入':<10} {'客单价':<8}")
        print("-" * 60)
        for report in cursor.fetchall():
            avg_value = report['avg_order_value'] if report['avg_order_value'] else 0
            print(
                f"{report['shop_name']:<15} {report['category']:<8} {report['order_count']:<8} ¥{report['total_revenue']:<9} ¥{avg_value:<7.0f}")

        # 3. 商品库存预警
        print("\n3. 库存预警报告:")
        cursor.execute("""
            SELECT 
                s.shop_name,
                p.product_name,
                p.stock,
                p.price,
                CASE 
                    WHEN p.stock = 0 THEN '缺货'
                    WHEN p.stock < 10 THEN '低库存'
                    ELSE '正常'
                END as stock_status
            FROM products p
            INNER JOIN shops s ON p.shop_id = s.id
            WHERE p.stock < 20 AND p.is_active = 1
            ORDER BY p.stock ASC
        """)

        for item in cursor.fetchall():
            status_icon = "🔴" if item['stock_status'] == '缺货' else "🟡"
            print(
                f"  {status_icon} {item['shop_name']} | {item['product_name']} | 库存:{item['stock']} | {item['stock_status']}")

    def advanced_features(self):
        """
        高级特性演示
        演示：存储过程、触发器、视图
        """
        print("\n" + "=" * 50)
        print("高级特性演示")
        print("=" * 50)

        cursor = self.connection.cursor()

        # 1. 创建视图
        print("\n1. 创建和使用视图:")
        try:
            cursor.execute("DROP VIEW IF EXISTS shop_summary")
            cursor.execute("""
                CREATE VIEW shop_summary AS
                SELECT 
                    s.id,
                    s.shop_name,
                    s.category,
                    s.rating,
                    s.monthly_sales,
                    COUNT(p.id) as product_count,
                    AVG(p.price) as avg_product_price
                FROM shops s
                LEFT JOIN products p ON s.id = p.shop_id AND p.is_active = 1
                GROUP BY s.id, s.shop_name, s.category, s.rating, s.monthly_sales
            """)
            print("✅ 创建店铺汇总视图成功")

            # 使用视图查询
            cursor.execute("SELECT shop_name, product_count, avg_product_price FROM shop_summary ORDER BY rating DESC")
            print("\n店铺汇总信息:")
            for row in cursor.fetchall():
                shop_name, product_count, avg_price = row
                avg_price = avg_price if avg_price else 0
                print(f"  {shop_name} | 商品数:{product_count} | 平均价格:¥{avg_price:.2f}")

        except Exception as e:
            print(f"❌ 视图操作失败: {e}")

        # 2. 创建存储过程
        print("\n2. 创建和调用存储过程:")
        try:
            cursor.execute("DROP PROCEDURE IF EXISTS GetShopStats")
            cursor.execute("""
                CREATE PROCEDURE GetShopStats(IN shop_id INT)
                BEGIN
                    DECLARE shop_name_var VARCHAR(100);
                    DECLARE total_products INT DEFAULT 0;
                    DECLARE total_orders INT DEFAULT 0;
                    DECLARE total_revenue DECIMAL(10,2) DEFAULT 0.00;

                    -- 获取店铺名称
                    SELECT shop_name INTO shop_name_var FROM shops WHERE id = shop_id;

                    -- 获取商品数量
                    SELECT COUNT(*) INTO total_products FROM products WHERE shop_id = shop_id;

                    -- 获取订单数量和总收入
                    SELECT COUNT(*), COALESCE(SUM(total_amount), 0) 
                    INTO total_orders, total_revenue 
                    FROM orders WHERE shop_id = shop_id;

                    -- 返回结果
                    SELECT shop_name_var as shop_name, total_products, total_orders, total_revenue;
                END
            """)
            print("✅ 创建存储过程成功")

            # 调用存储过程
            cursor.callproc('GetShopStats', [1])
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    print(f"  店铺统计 - 名称:{row[0]} | 商品数:{row[1]} | 订单数:{row[2]} | 总收入:¥{row[3]}")

        except Exception as e:
            print(f"❌ 存储过程操作失败: {e}")

        # 3. 创建触发器
        print("\n3. 创建触发器:")
        try:
            cursor.execute("DROP TRIGGER IF EXISTS update_shop_sales")
            cursor.execute("""
                CREATE TRIGGER update_shop_sales
                AFTER INSERT ON orders
                FOR EACH ROW
                BEGIN
                    UPDATE shops 
                    SET monthly_sales = monthly_sales + NEW.total_amount
                    WHERE id = NEW.shop_id;
                END
            """)
            print("✅ 创建触发器成功（新订单自动更新店铺销售额）")

        except Exception as e:
            print(f"❌ 触发器操作失败: {e}")

        self.connection.commit()

    def performance_monitoring(self):
        """
        性能监控
        演示：慢查询日志、连接状态、缓存命中率
        """
        print("\n" + "=" * 50)
        print("性能监控")
        print("=" * 50)

        cursor = self.connection.cursor()

        # 1. 查看数据库状态
        print("\n1. 数据库连接状态:")
        cursor.execute("SHOW STATUS LIKE 'Connections'")
        connections = cursor.fetchone()
        print(f"总连接数: {connections[1]}")

        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        active_connections = cursor.fetchone()
        print(f"当前活跃连接: {active_connections[1]}")

        # 2. 查看表信息
        print("\n2. 表空间使用情况:")
        cursor.execute("""
            SELECT 
                TABLE_NAME,
                TABLE_ROWS,
                ROUND(DATA_LENGTH/1024/1024, 2) as DATA_SIZE_MB,
                ROUND(INDEX_LENGTH/1024/1024, 2) as INDEX_SIZE_MB
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (self.database,))

        print(f"{'表名':<15} {'行数':<10} {'数据大小(MB)':<12} {'索引大小(MB)':<12}")
        print("-" * 55)
        for table_info in cursor.fetchall():
            table_name, rows, data_size, index_size = table_info
            print(f"{table_name:<15} {rows or 0:<10} {data_size:<12} {index_size:<12}")

        # 3. 查看进程列表
        print("\n3. 当前进程:")
        try:
            cursor.execute("SHOW PROCESSLIST")
            processes = cursor.fetchall()
            print(f"当前活跃进程数: {len(processes)}")
            for proc in processes[:3]:  # 只显示前3个
                print(f"  ID:{proc[0]} | 用户:{proc[1]} | 状态:{proc[4]} | 时间:{proc[5]}s")
        except Exception as e:
            print(f"查看进程失败: {e}")

    def backup_and_restore_demo(self):
        """
        备份恢复演示
        演示：数据导出、导入的Python实现
        """
        print("\n" + "=" * 50)
        print("备份恢复演示")
        print("=" * 50)

        cursor = self.connection.cursor()

        # 1. 数据备份（简单的INSERT语句生成）
        print("\n1. 生成备份SQL:")
        backup_sql = []

        # 备份shops表
        cursor.execute("SELECT * FROM shops")
        shops_data = cursor.fetchall()
        cursor.execute("DESCRIBE shops")
        shops_columns = [col[0] for col in cursor.fetchall()]

        backup_sql.append("-- 备份shops表")
        backup_sql.append("TRUNCATE TABLE shops;")

        for row in shops_data:
            values = []
            for val in row:
                if val is None:
                    values.append('NULL')
                elif isinstance(val, str):
                    values.append(f"'{val.replace('\'', '\\\'')}'")
                elif isinstance(val, datetime):
                    values.append(f"'{val}'")
                else:
                    values.append(str(val))

            backup_sql.append(f"INSERT INTO shops VALUES ({', '.join(values)});")

        print("✅ 生成了备份SQL语句")
        print(f"备份包含 {len(shops_data)} 条店铺记录")

        # 2. 展示部分备份内容
        print("\n2. 备份文件预览（前3行）:")
        for line in backup_sql[:5]:
            print(f"  {line}")
        if len(backup_sql) > 5:
            print(f"  ... （共{len(backup_sql)}行）")

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("✅ 数据库连接已关闭")


def main():
    """
    主函数：执行完整的教学演示
    """
    print("🎓 Python + MySQL 完整教学演示")
    print("=" * 60)

    # 初始化数据库（请根据你的环境修改连接参数）
    db = ShopDatabase(
        host='localhost',
        user='root',
        password='root',  # 请修改为你的MySQL密码
        database='shop_demo'
    )

    try:
        # 1. 连接数据库
        db.connect()

        # 2. 创建表结构
        db.create_tables()

        # 3. 创建索引
        db.create_indexes()

        # 4. 插入示例数据
        db.insert_sample_data()

        # 5. 基础查询演示
        db.query_examples()

        # 6. 连接查询演示
        db.join_examples()

        # 7. 事务处理演示
        db.transaction_example()

        # 8. 索引性能测试
        db.index_performance_test()

        # 9. 查询优化演示
        db.optimization_examples()

        # 10. 实际应用场景
        db.practical_scenarios()

        # 11. 高级特性演示
        db.advanced_features()

        # 12. 性能监控
        db.performance_monitoring()

        # 13. 备份恢复演示
        db.backup_and_restore_demo()

        print("\n🎉 教学演示完成！")
        print("\n📚 学习要点总结：")
        print("1. 数据库连接和基础操作")
        print("2. 表设计：字段类型、约束条件、外键")
        print("3. 索引：普通索引、唯一索引、复合索引、全文索引")
        print("4. 查询：基础查询、条件查询、排序、分组、聚合")
        print("5. 连接：INNER JOIN、LEFT JOIN、复杂多表查询")
        print("6. 事务：ACID特性、提交、回滚、并发控制")
        print("7. 优化：查询优化、执行计划分析、索引使用")
        print("8. 高级特性：视图、存储过程、触发器")
        print("9. 性能监控：连接状态、表空间、进程管理")
        print("10. 实际应用：分页、统计报表、库存管理")

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")

    finally:
        # 关闭数据库连接
        db.close()


# 单独功能测试函数
def quick_test():
    """
    快速测试函数：只运行基础功能，适合初学者
    """
    print("🚀 快速测试模式")

    db = ShopDatabase()
    try:
        db.connect()
        db.create_tables()
        db.insert_sample_data()
        db.query_examples()
        print("\n✅ 快速测试完成！")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 运行完整演示
    main()

    # 如果只想快速测试，可以运行：
    # quick_test()

"""
🔧 使用说明：

1. 环境准备：
   - 安装MySQL服务器
   - 安装Python依赖：pip install pymysql sqlalchemy pandas

2. 配置修改：
   - 修改数据库连接参数（host, user, password）
   - 确保MySQL服务正在运行

3. 运行方式：
   - 完整演示：python mysql_tutorial.py
   - 快速测试：取消注释最后一行的 quick_test()

4. 学习建议：
   - 先运行快速测试，理解基础概念
   - 再运行完整演示，学习高级特性
   - 尝试修改代码，实验不同的查询和操作
   - 查看控制台输出，理解每个步骤的作用

5. 扩展练习：
   - 添加新的表和字段
   - 设计更复杂的查询
   - 实现数据导入导出功能
   - 添加数据验证和错误处理
   - 实现连接池管理

📖 相关学习资源：
- MySQL官方文档：https://dev.mysql.com/doc/
- SQLAlchemy文档：https://docs.sqlalchemy.org/
- Python MySQL编程实践
"""