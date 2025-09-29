# 导入 pymysql 主包
# 导入 pymysql 包中的 cursors 子模块
# 两者都可以使用
import pymysql.cursors
from sqlalchemy import false

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='shop_demo',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=False,
                             )

with connection:
    with connection.cursor() as cursor:

        sql = "SELECT * FROM orders"

        try:
            cursor.execute(sql)
            connection.commit()
            print(cursor.fetchall())
        except Exception as e:
            print(e)
            connection.rollback()


    # connection.commit()


