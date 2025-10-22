"""
Pandas 核心功能学习项目
这个项目涵盖了 Pandas 的主要功能，通过实际案例帮助你掌握数据分析技能

学习方法：慢下来！
1. 先将所有的代码看懂，不明白的问ai。只需要了解给出的运用场景，不用去扩展，不然容易陷入迷惘。
2. 对要点进行针对性的扩展学习，筛选出要点，不用广泛性的都去扩展学习，不然难点太大容易放弃。
3. 运用到实践当中，先对扩展学习后的要点进行实践学习，再根据实践进行不同程度的扩展学习。
4. 从学习到实践，再从实践中学习，循环往复，周而复始，源源不断。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("Pandas 学习项目 - 数据分析完整流程")
print("=" * 60)

# ============================================================
# 第一部分：创建 DataFrame 和 Series
# ============================================================
print("\n【第一部分：数据结构基础】")
print("-" * 60)

# 1.1 创建 Series
print("\n1. 创建 Series（一维数据）：")
series_data = pd.Series([10, 20, 30, 40, 50],
                        index=['a', 'b', 'c', 'd', 'e'],
                        name='销售额')
print(series_data)

# 1.2 创建 DataFrame - 从字典
print("\n2. 创建 DataFrame（二维表格）：")
data = {
    '姓名': ['张三', '李四', '王五', '赵六', '钱七'],
    '年龄': [25, 30, 35, 28, 32],
    '部门': ['技术', '销售', '技术', '市场', '销售'],
    '工资': [8000, 7000, 9500, 6500, 7500],
    '入职日期': pd.date_range('2020-01-01', periods=5, freq='M')
}
df = pd.DataFrame(data)
print(df)

# ============================================================
# 第二部分：数据查看和基本信息
# ============================================================
print("\n\n【第二部分：数据查看】")
print("-" * 60)

print("\n1. 查看前几行：")
print(df.head(3))

print("\n2. 查看基本信息：")
print(df.info())

print("\n3. 统计描述：")
print(df.describe())

print("\n4. 数据形状：", df.shape)
print("5. 列名：", df.columns.tolist())
print("6. 数据类型：\n", df.dtypes)

# ============================================================
# 第三部分：数据选择和索引
# ============================================================
print("\n\n【第三部分：数据选择】")
print("-" * 60)

print("\n1. 选择单列：")
print(df['姓名'])

print("\n2. 选择多列：")
print(df[['姓名', '工资']])

print("\n3. 使用 loc 按标签选择（行和列）：")
print(df.loc[0:2, ['姓名', '部门']])

print("\n4. 使用 iloc 按位置选择：")
print(df.iloc[0:3, [0, 3]])

print("\n5. 条件筛选（工资大于7000）：")
print(df[df['工资'] > 7000])

print("\n6. 多条件筛选（技术部门且年龄小于33）：")
print(df[(df['部门'] == '技术') & (df['年龄'] < 33)])

# ============================================================
# 第四部分：数据添加和修改
# ============================================================
print("\n\n【第四部分：数据修改】")
print("-" * 60)

# 复制数据以避免修改原始数据
df_modified = df.copy()

print("\n1. 添加新列（计算年终奖）：")
df_modified['年终奖'] = df_modified['工资'] * 2
print(df_modified[['姓名', '工资', '年终奖']])

print("\n2. 修改特定值：")
df_modified.loc[0, '工资'] = 8500
print(f"张三的新工资：{df_modified.loc[0, '工资']}")

print("\n3. 使用函数修改列（工资增长10%）：")
df_modified['工资'] = df_modified['工资'].apply(lambda x: x * 1.1)
print(df_modified[['姓名', '工资']])

# ============================================================
# 第五部分：数据清洗
# ============================================================
print("\n\n【第五部分：数据清洗】")
print("-" * 60)

# 创建包含缺失值的数据
data_dirty = {
    '产品': ['A', 'B', 'C', 'D', 'E', 'A'],
    '销量': [100, np.nan, 150, 200, np.nan, 120],
    '价格': [10, 20, np.nan, 30, 25, 10],
    '评分': [4.5, 3.8, 4.2, np.nan, 4.0, 4.7]
}
df_dirty = pd.DataFrame(data_dirty)

print("\n1. 原始数据（含缺失值）：")
print(df_dirty)

print("\n2. 检查缺失值：")
print(df_dirty.isnull().sum())

print("\n3. 删除含缺失值的行：")
print(df_dirty.dropna())

print("\n4. 填充缺失值（用平均值）：")
df_filled = df_dirty.copy()
df_filled['销量'].fillna(df_filled['销量'].mean(), inplace=True)
print(df_filled)

print("\n5. 删除重复行：")
print(f"重复行数：{df_dirty.duplicated().sum()}")
df_unique = df_dirty.drop_duplicates(subset=['产品'])
print(df_unique)

# ============================================================
# 第六部分：数据分组和聚合
# ============================================================
print("\n\n【第六部分：分组聚合】")
print("-" * 60)

print("\n1. 按部门分组计算平均工资：")
dept_avg = df.groupby('部门')['工资'].mean()
print(dept_avg)

print("\n2. 多列聚合：")
dept_stats = df.groupby('部门').agg({
    '工资': ['mean', 'max', 'min'],
    '年龄': 'mean'
})
print(dept_stats)

print("\n3. 统计每个部门的人数：")
print(df['部门'].value_counts())

# ============================================================
# 第七部分：数据排序
# ============================================================
print("\n\n【第七部分：数据排序】")
print("-" * 60)

print("\n1. 按工资降序排列：")
print(df.sort_values('工资', ascending=False))

print("\n2. 多列排序（先按部门，再按工资）：")
print(df.sort_values(['部门', '工资'], ascending=[True, False]))

# ============================================================
# 第八部分：数据合并
# ============================================================
print("\n\n【第八部分：数据合并】")
print("-" * 60)

# 创建两个相关的 DataFrame
df1 = pd.DataFrame({
    '员工ID': [1, 2, 3, 4],
    '姓名': ['张三', '李四', '王五', '赵六'],
    '部门ID': [101, 102, 101, 103]
})

df2 = pd.DataFrame({
    '部门ID': [101, 102, 103],
    '部门名称': ['技术部', '销售部', '市场部']
})

print("\n1. 员工表：")
print(df1)
print("\n2. 部门表：")
print(df2)

print("\n3. 合并两个表（JOIN）：")
merged_df = pd.merge(df1, df2, on='部门ID', how='left')
print(merged_df)

print("\n4. 纵向连接（concat）：")
df3 = pd.DataFrame({
    '员工ID': [5, 6],
    '姓名': ['钱七', '孙八'],
    '部门ID': [102, 101]
})
concatenated = pd.concat([df1, df3], ignore_index=True)
print(concatenated)

# ============================================================
# 第九部分：数据透视表
# ============================================================
print("\n\n【第九部分：数据透视表】")
print("-" * 60)

# 创建销售数据
sales_data = pd.DataFrame({
    '日期': pd.date_range('2024-01-01', periods=12, freq='M'),
    '地区': ['北京', '上海', '北京', '上海', '北京', '上海'] * 2,
    '产品': ['A', 'A', 'B', 'B', 'A', 'A', 'B', 'B', 'A', 'A', 'B', 'B'],
    '销售额': [100, 150, 200, 180, 120, 160, 210, 190, 130, 170, 220, 200]
})

print("\n1. 销售数据：")
print(sales_data.head(8))

print("\n2. 创建透视表（地区 vs 产品）：")
pivot = sales_data.pivot_table(
    values='销售额',
    index='地区',
    columns='产品',
    aggfunc='sum'
)
print(pivot)

# ============================================================
# 第十部分：时间序列处理
# ============================================================
print("\n\n【第十部分：时间序列】")
print("-" * 60)

# 创建时间序列数据
dates = pd.date_range('2024-01-01', periods=10, freq='D')
ts_data = pd.DataFrame({
    '日期': dates,
    '温度': [15, 16, 14, 17, 18, 19, 20, 18, 17, 16]
})
ts_data.set_index('日期', inplace=True)

print("\n1. 时间序列数据：")
print(ts_data)

print("\n2. 提取日期组件：")
ts_data['月份'] = ts_data.index.month
ts_data['星期'] = ts_data.index.dayofweek
print(ts_data)

print("\n3. 重采样（按周求平均）：")
weekly_avg = ts_data['温度'].resample('W').mean()
print(weekly_avg)

# ============================================================
# 第十一部分：字符串操作
# ============================================================
print("\n\n【第十一部分：字符串操作】")
print("-" * 60)

text_data = pd.DataFrame({
    '姓名': ['  张三  ', 'LI Si', 'WANG Wu'],
    '邮箱': ['zhangsan@example.com', 'lisi@example.com', 'wangwu@example.com']
})

print("\n1. 原始数据：")
print(text_data)

print("\n2. 字符串处理：")
text_data['姓名_清洗'] = text_data['姓名'].str.strip().str.upper()
text_data['邮箱域名'] = text_data['邮箱'].str.split('@').str[1]
print(text_data)

# ============================================================
# 第十二部分：导出数据
# ============================================================
print("\n\n【第十二部分：数据导出】")
print("-" * 60)

print("\n你可以使用以下方法导出数据：")
print("1. df.to_csv('data.csv', index=False)  # 导出为CSV")
print("2. df.to_excel('data.xlsx', index=False)  # 导出为Excel")
print("3. df.to_json('data.json')  # 导出为JSON")
print("4. df.to_sql('table_name', connection)  # 导出到数据库")

# ============================================================
# 第十三部分：进阶练习 - 复杂数据分析
# ============================================================
print("\n\n" + "=" * 60)
print("【第十三部分：进阶挑战练习】")
print("=" * 60)

# 创建复杂的电商数据集
np.random.seed(42)
n_orders = 1000

ecommerce_data = pd.DataFrame({
    '订单ID': range(1001, 1001 + n_orders),
    '用户ID': np.random.randint(1, 201, n_orders),
    '产品类别': np.random.choice(['电子产品', '服装', '食品', '家居', '图书'], n_orders),
    '订单金额': np.random.uniform(50, 5000, n_orders).round(2),
    '订单日期': pd.date_range('2023-01-01', periods=n_orders, freq='8H'),
    '支付方式': np.random.choice(['支付宝', '微信', '信用卡', '现金'], n_orders),
    '配送状态': np.random.choice(['已送达', '配送中', '已取消', '退货'], n_orders, p=[0.7, 0.15, 0.1, 0.05]),
    '用户评分': np.random.choice([1, 2, 3, 4, 5, np.nan], n_orders, p=[0.02, 0.03, 0.1, 0.3, 0.5, 0.05])
})

print("\n📊 电商数据集（前10行）：")
print(ecommerce_data.head(10))

# ============================================================
# 练习1：客户价值分析（RFM模型）
# ============================================================
print("\n\n【练习1：客户价值分析 - RFM模型】")
print("-" * 60)

# 只分析已送达的订单
delivered_orders = ecommerce_data[ecommerce_data['配送状态'] == '已送达'].copy()

# 计算RFM指标
reference_date = delivered_orders['订单日期'].max() + timedelta(days=1)

rfm = delivered_orders.groupby('用户ID').agg({
    '订单日期': lambda x: (reference_date - x.max()).days,  # Recency
    '订单ID': 'count',  # Frequency
    '订单金额': 'sum'  # Monetary
}).rename(columns={
    '订单日期': 'Recency',
    '订单ID': 'Frequency',
    '订单金额': 'Monetary'
})

# RFM分数计算（五分位数）
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

# 综合RFM分数
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

# 客户分层
def segment_customer(row):
    if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
        return '重要价值客户'
    elif row['R_Score'] >= 4 and row['F_Score'] >= 4:
        return '重要发展客户'
    elif row['R_Score'] >= 4:
        return '重要保持客户'
    elif row['F_Score'] >= 4 and row['M_Score'] >= 4:
        return '一般价值客户'
    else:
        return '潜在客户'

rfm['客户分层'] = rfm.apply(segment_customer, axis=1)

print("\n1. RFM分析结果（前10个客户）：")
print(rfm.head(10))

print("\n2. 客户分层统计：")
print(rfm['客户分层'].value_counts())

print("\n3. 各层级客户平均价值：")
segment_stats = rfm.groupby('客户分层').agg({
    'Monetary': 'mean',
    'Frequency': 'mean',
    'Recency': 'mean'
}).round(2)
print(segment_stats)

# ============================================================
# 练习2：滑动窗口分析和同比环比
# ============================================================
print("\n\n【练习2：时间序列滑动窗口分析】")
print("-" * 60)

# 按日期聚合销售数据
daily_sales = ecommerce_data[ecommerce_data['配送状态'] == '已送达'].groupby(
    ecommerce_data['订单日期'].dt.date
).agg({
    '订单金额': 'sum',
    '订单ID': 'count'
}).rename(columns={'订单金额': '销售额', '订单ID': '订单量'})

# 7日移动平均
daily_sales['销售额_7日均值'] = daily_sales['销售额'].rolling(window=7).mean()
daily_sales['订单量_7日均值'] = daily_sales['订单量'].rolling(window=7).mean()

# 环比增长率
daily_sales['销售额_环比'] = daily_sales['销售额'].pct_change() * 100

# 7日前同比
daily_sales['销售额_7日同比'] = daily_sales['销售额'].pct_change(periods=7) * 100

print("\n1. 时间序列分析（最近10天）：")
print(daily_sales.tail(10).round(2))

print("\n2. 销售趋势统计：")
print(f"平均日销售额: {daily_sales['销售额'].mean():.2f}")
print(f"最高日销售额: {daily_sales['销售额'].max():.2f}")
print(f"销售额标准差: {daily_sales['销售额'].std():.2f}")
print(f"平均环比增长率: {daily_sales['销售额_环比'].mean():.2f}%")

# ============================================================
# 练习3：多维透视和交叉分析
# ============================================================
print("\n\n【练习3：多维数据透视分析】")
print("-" * 60)

# 添加时间维度
ecommerce_data['月份'] = ecommerce_data['订单日期'].dt.to_period('M')
ecommerce_data['季度'] = ecommerce_data['订单日期'].dt.to_period('Q')

# 复杂透视表：类别 × 支付方式 × 配送状态
pivot_complex = pd.pivot_table(
    ecommerce_data,
    values='订单金额',
    index=['产品类别', '支付方式'],
    columns='配送状态',
    aggfunc=['sum', 'count', 'mean'],
    fill_value=0
)

print("\n1. 多维透视表（部分结果）：")
print(pivot_complex.head(10))

# 交叉表分析
print("\n2. 产品类别 vs 配送状态交叉分析：")
cross_tab = pd.crosstab(
    ecommerce_data['产品类别'],
    ecommerce_data['配送状态'],
    values=ecommerce_data['订单金额'],
    aggfunc='sum',
    margins=True,
    margins_name='总计'
)
print(cross_tab)

# ============================================================
# 练习4：复杂的条件筛选和数据转换
# ============================================================
print("\n\n【练习4：复杂条件筛选和特征工程】")
print("-" * 60)

# 创建复杂的条件列
def classify_order(row):
    if row['订单金额'] > 2000 and row['用户评分'] >= 4:
        return '优质大单'
    elif row['订单金额'] > 2000:
        return '大单待提升'
    elif row['用户评分'] >= 4:
        return '优质小单'
    elif pd.isna(row['用户评分']):
        return '未评价'
    else:
        return '一般订单'

ecommerce_data['订单分类'] = ecommerce_data.apply(classify_order, axis=1)

print("\n1. 订单分类统计：")
print(ecommerce_data['订单分类'].value_counts())

# 多条件复合筛选
high_value_orders = ecommerce_data[
    (ecommerce_data['订单金额'] > ecommerce_data['订单金额'].quantile(0.75)) &
    (ecommerce_data['配送状态'] == '已送达') &
    (ecommerce_data['用户评分'] >= 4) &
    (ecommerce_data['订单日期'] >= '2023-06-01')
]

print(f"\n2. 高价值订单数量: {len(high_value_orders)}")
print(f"   占总订单比例: {len(high_value_orders) / len(ecommerce_data) * 100:.2f}%")

# 使用 transform 进行组内标准化
ecommerce_data['金额_类别标准化'] = ecommerce_data.groupby('产品类别')['订单金额'].transform(
    lambda x: (x - x.mean()) / x.std()
)

print("\n3. 标准化后的数据示例：")
print(ecommerce_data[['产品类别', '订单金额', '金额_类别标准化']].head(10))

# ============================================================
# 练习5：窗口函数和排名分析
# ============================================================
print("\n\n【练习5：窗口函数和排名分析】")
print("-" * 60)

# 每个类别中的订单金额排名
ecommerce_data['类别内排名'] = ecommerce_data.groupby('产品类别')['订单金额'].rank(
    method='dense', ascending=False
)

# 累计求和
ecommerce_data_sorted = ecommerce_data.sort_values('订单日期')
ecommerce_data_sorted['累计销售额'] = ecommerce_data_sorted['订单金额'].cumsum()

# 找出每个类别的Top 3订单
top3_by_category = ecommerce_data[
    ecommerce_data['类别内排名'] <= 3
].sort_values(['产品类别', '类别内排名'])

print("\n1. 各类别Top 3订单：")
print(top3_by_category[['产品类别', '订单金额', '类别内排名']].head(15))

# 计算移动中位数
category_rolling = ecommerce_data.sort_values('订单日期').groupby('产品类别')['订单金额'].rolling(
    window=10, min_periods=1
).median().reset_index(drop=True)

print("\n2. 移动中位数计算完成（前10条）：")
print(category_rolling.head(10))

# ============================================================
# 练习6：数据质量分析和异常检测
# ============================================================
print("\n\n【练习6：数据质量和异常检测】")
print("-" * 60)

# 使用 IQR 方法检测异常值
Q1 = ecommerce_data['订单金额'].quantile(0.25)
Q3 = ecommerce_data['订单金额'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = ecommerce_data[
    (ecommerce_data['订单金额'] < lower_bound) |
    (ecommerce_data['订单金额'] > upper_bound)
]

print(f"\n1. 异常值检测（IQR方法）：")
print(f"   下界: {lower_bound:.2f}, 上界: {upper_bound:.2f}")
print(f"   检测到 {len(outliers)} 个异常订单")
print(f"   异常订单占比: {len(outliers) / len(ecommerce_data) * 100:.2f}%")

# 数据完整性检查
print("\n2. 数据完整性分析：")
missing_summary = pd.DataFrame({
    '缺失数量': ecommerce_data.isnull().sum(),
    '缺失比例': (ecommerce_data.isnull().sum() / len(ecommerce_data) * 100).round(2)
})
print(missing_summary[missing_summary['缺失数量'] > 0])

# 重复值检查
duplicates = ecommerce_data.duplicated(subset=['用户ID', '订单日期', '订单金额']).sum()
print(f"\n3. 可能的重复订单: {duplicates}")

# ============================================================
# 练习7：高级分组和聚合
# ============================================================
print("\n\n【练习7：高级分组聚合操作】")
print("-" * 60)

# 自定义聚合函数
def sales_range(x):
    return x.max() - x.min()

def top3_avg(x):
    return x.nlargest(3).mean()

# 多层次聚合
advanced_agg = ecommerce_data.groupby(['产品类别', '支付方式']).agg({
    '订单金额': [
        'sum',
        'mean',
        'count',
        ('range', sales_range),
        ('top3_avg', top3_avg)
    ],
    '用户评分': lambda x: x.dropna().mean()
}).round(2)

print("\n1. 高级聚合分析结果：")
print(advanced_agg.head(10))

# 使用 agg 结合 lambda
user_behavior = ecommerce_data.groupby('用户ID').agg(
    总消费=('订单金额', 'sum'),
    订单数=('订单ID', 'count'),
    平均客单价=('订单金额', 'mean'),
    消费标准差=('订单金额', 'std'),
    最近购买=('订单日期', 'max'),
    首次购买=('订单日期', 'min'),
    购买天数=('订单日期', lambda x: (x.max() - x.min()).days)
).round(2)

print("\n2. 用户行为深度分析（前10个用户）：")
print(user_behavior.head(10))

# ============================================================
# 挑战任务提示
# ============================================================
print("\n\n" + "=" * 60)
print("🎯 进阶挑战任务完成！")
print("=" * 60)
print("\n💪 你已经掌握了：")
print("✓ RFM客户价值分析")
print("✓ 时间序列滑动窗口和同环比分析")
print("✓ 多维数据透视和交叉表")
print("✓ 复杂条件筛选和特征工程")
print("✓ 窗口函数和排名计算")
print("✓ 异常检测和数据质量分析")
print("✓ 高级分组聚合技巧")

print("\n\n🚀 进阶练习建议：")
print("-" * 60)
print("1. 尝试使用真实数据集（Kaggle、UCI等）")
print("2. 实现完整的数据分析报告（EDA）")
print("3. 结合 matplotlib/seaborn 进行可视化")
print("4. 学习 Pandas 性能优化技巧")
print("5. 探索 Pandas 与 SQL 的结合使用")
print("6. 挑战处理百万级以上的大数据集")
print("=" * 60)