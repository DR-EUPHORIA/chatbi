"""Demo 电商数据库初始化脚本 — 创建表结构并填充模拟数据"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from config import settings

# 模拟数据常量
CATEGORIES = [
    ("数码", "电子产品"),
    ("手机", "电子产品"),
    ("电脑", "电子产品"),
    ("耳机", "电子产品"),
    ("服装", "服饰鞋包"),
    ("鞋靴", "服饰鞋包"),
    ("箱包", "服饰鞋包"),
    ("食品", "食品生鲜"),
    ("生鲜", "食品生鲜"),
    ("家电", "家居家电"),
    ("家具", "家居家电"),
    ("美妆", "美妆个护"),
    ("个护", "美妆个护"),
    ("图书", "图书文娱"),
]

PRODUCTS = [
    ("iPhone 15", 1, 5999.0, 4200.0),
    ("MacBook Air", 2, 8999.0, 6500.0),
    ("AirPods Pro", 3, 1799.0, 1100.0),
    ("华为 Mate 60", 1, 5499.0, 3800.0),
    ("联想小新笔记本", 2, 4999.0, 3600.0),
    ("索尼降噪耳机", 3, 2299.0, 1500.0),
    ("优衣库T恤", 4, 99.0, 40.0),
    ("Nike 运动鞋", 5, 799.0, 350.0),
    ("新秀丽行李箱", 6, 1299.0, 700.0),
    ("三只松鼠坚果", 7, 59.9, 30.0),
    ("智利车厘子", 8, 129.0, 80.0),
    ("美的空调", 9, 3299.0, 2200.0),
    ("宜家书桌", 10, 599.0, 300.0),
    ("兰蔻小黑瓶", 11, 899.0, 450.0),
    ("舒肤佳沐浴露", 12, 39.9, 15.0),
    ("三体（全集）", 13, 89.0, 35.0),
    ("小米手环", 0, 249.0, 150.0),
    ("戴森吹风机", 12, 2999.0, 1800.0),
    ("海尔冰箱", 9, 2599.0, 1700.0),
    ("阿迪达斯外套", 4, 599.0, 250.0),
]

REGIONS = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
CITIES = {
    "华东": ["上海", "杭州", "南京", "苏州", "宁波"],
    "华南": ["广州", "深圳", "东莞", "佛山", "厦门"],
    "华北": ["北京", "天津", "石家庄", "太原", "济南"],
    "华中": ["武汉", "长沙", "郑州", "合肥", "南昌"],
    "西南": ["成都", "重庆", "昆明", "贵阳", "南宁"],
    "西北": ["西安", "兰州", "乌鲁木齐", "银川", "西宁"],
    "东北": ["沈阳", "大连", "哈尔滨", "长春", "吉林"],
}
PAYMENT_METHODS = ["支付宝", "微信支付", "银行卡", "花呗", "信用卡"]
ORDER_STATUSES = ["paid", "shipped", "delivered", "refunded"]
STATUS_WEIGHTS = [0.15, 0.20, 0.55, 0.10]
GENDERS = ["男", "女"]


def _parse_db_path(db_url: str) -> str:
    """从 SQLAlchemy URL 中提取 SQLite 文件路径"""
    prefix = "sqlite:///"
    if db_url.startswith(prefix):
        return db_url[len(prefix):]
    return db_url


def init_demo_db() -> str:
    """初始化 Demo 电商数据库，返回结果描述"""

    db_path = _parse_db_path(settings.default_db_url)
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    random.seed(42)

    conn = sqlite3.connect(str(path))
    cursor = conn.cursor()

    # 创建表
    cursor.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS categories;
        DROP TABLE IF EXISTS users;

        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            parent_category TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 1000,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );

        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            city TEXT NOT NULL,
            region TEXT NOT NULL,
            register_date TEXT NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            profit REAL NOT NULL,
            status TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            region TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)

    # 插入品类
    for category_name, parent_category in CATEGORIES:
        cursor.execute(
            "INSERT INTO categories (category_name, parent_category) VALUES (?, ?)",
            (category_name, parent_category),
        )

    # 插入商品
    for product_name, cat_idx, price, cost in PRODUCTS:
        category_id = cat_idx + 1 if cat_idx < len(CATEGORIES) else 1
        stock = random.randint(100, 5000)
        cursor.execute(
            "INSERT INTO products (product_name, category_id, price, cost, stock) VALUES (?, ?, ?, ?, ?)",
            (product_name, category_id, price, cost, stock),
        )

    # 插入用户
    user_count = 5000
    base_register_date = datetime(2023, 1, 1)
    for user_idx in range(user_count):
        region = random.choice(REGIONS)
        city = random.choice(CITIES[region])
        gender = random.choice(GENDERS)
        age = random.randint(18, 65)
        register_date = base_register_date + timedelta(days=random.randint(0, 730))
        cursor.execute(
            "INSERT INTO users (username, gender, age, city, region, register_date) VALUES (?, ?, ?, ?, ?, ?)",
            (f"user_{user_idx + 1:05d}", gender, age, city, region, register_date.strftime("%Y-%m-%d")),
        )

    # 插入订单
    order_count = 100000
    product_count = len(PRODUCTS)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 2, 13)
    date_range_days = (end_date - start_date).days

    order_rows = []
    for _ in range(order_count):
        user_id = random.randint(1, user_count)
        product_id = random.randint(1, product_count)
        order_date = start_date + timedelta(days=random.randint(0, date_range_days))
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]

        product_price = PRODUCTS[product_id - 1][2]
        product_cost = PRODUCTS[product_id - 1][3]

        discount = random.uniform(0.85, 1.0)
        unit_price = round(product_price * discount, 2)
        total_amount = round(unit_price * quantity, 2)
        profit = round((unit_price - product_cost) * quantity, 2)

        status = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]
        payment_method = random.choice(PAYMENT_METHODS)
        region = random.choice(REGIONS)

        order_rows.append((
            user_id, product_id, order_date.strftime("%Y-%m-%d"),
            quantity, unit_price, total_amount, profit,
            status, payment_method, region,
        ))

    cursor.executemany(
        "INSERT INTO orders (user_id, product_id, order_date, quantity, unit_price, total_amount, profit, status, payment_method, region) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        order_rows,
    )

    conn.commit()

    # 验证
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products")
    prod_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    usr_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders")
    ord_count = cursor.fetchone()[0]

    conn.close()

    return f"Demo 数据库初始化完成：{cat_count} 个品类，{prod_count} 个商品，{usr_count} 个用户，{ord_count} 条订单"
