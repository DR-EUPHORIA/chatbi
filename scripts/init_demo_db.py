"""初始化 Demo 数据库 — 创建电商模拟数据"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "demo")
DB_PATH = os.path.join(DB_DIR, "ecommerce.db")


def create_tables(cursor):
    """创建表结构"""

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL,
            parent_category TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            gender TEXT,
            age INTEGER,
            city TEXT,
            region TEXT,
            register_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            profit REAL NOT NULL,
            status TEXT DEFAULT 'paid',
            payment_method TEXT,
            region TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)


def seed_categories(cursor):
    """插入品类数据"""
    categories = [
        (1, "电子产品", None),
        (2, "服装鞋帽", None),
        (3, "食品饮料", None),
        (4, "家居家装", None),
        (5, "美妆个护", None),
        (6, "手机数码", "电子产品"),
        (7, "电脑办公", "电子产品"),
        (8, "男装", "服装鞋帽"),
        (9, "女装", "服装鞋帽"),
        (10, "零食", "食品饮料"),
        (11, "饮料", "食品饮料"),
        (12, "家具", "家居家装"),
        (13, "护肤", "美妆个护"),
        (14, "彩妆", "美妆个护"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO categories VALUES (?, ?, ?)", categories)


def seed_products(cursor):
    """插入商品数据"""
    product_templates = [
        ("iPhone 15 Pro", 6, 7999, 5500),
        ("MacBook Air M3", 7, 9999, 7000),
        ("华为 Mate 60", 6, 6999, 4800),
        ("小米 14", 6, 3999, 2800),
        ("联想 ThinkPad", 7, 5999, 4200),
        ("Nike 运动鞋", 8, 899, 350),
        ("Adidas T恤", 8, 299, 120),
        ("优衣库羽绒服", 9, 599, 250),
        ("ZARA 连衣裙", 9, 499, 200),
        ("三只松鼠坚果", 10, 59, 25),
        ("良品铺子零食礼盒", 10, 129, 55),
        ("农夫山泉矿泉水", 11, 2, 0.8),
        ("可口可乐", 11, 3, 1.2),
        ("宜家书桌", 12, 999, 450),
        ("全友沙发", 12, 3999, 1800),
        ("兰蔻小黑瓶", 13, 1080, 400),
        ("SK-II 神仙水", 13, 1590, 600),
        ("MAC 口红", 14, 170, 60),
        ("完美日记眼影", 14, 89, 30),
        ("iPad Air", 6, 4799, 3300),
    ]

    products = []
    for idx, (name, cat_id, price, cost) in enumerate(product_templates, 1):
        stock = random.randint(100, 5000)
        products.append((idx, name, cat_id, price, cost, stock))

    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?, ?)", products)
    return len(products)


def seed_users(cursor, count=5000):
    """插入用户数据"""
    cities = {
        "华东": ["上海", "杭州", "南京", "苏州", "宁波"],
        "华北": ["北京", "天津", "石家庄", "太原", "济南"],
        "华南": ["广州", "深圳", "东莞", "佛山", "厦门"],
        "华中": ["武汉", "长沙", "郑州", "合肥", "南昌"],
        "西南": ["成都", "重庆", "昆明", "贵阳", "西安"],
    }

    genders = ["男", "女"]
    users = []

    for user_id in range(1, count + 1):
        region = random.choice(list(cities.keys()))
        city = random.choice(cities[region])
        gender = random.choice(genders)
        age = random.randint(18, 65)
        register_days_ago = random.randint(1, 730)
        register_date = (datetime.now() - timedelta(days=register_days_ago)).strftime("%Y-%m-%d")
        username = f"user_{user_id:05d}"

        users.append((user_id, username, gender, age, city, region, register_date))

    cursor.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", users)
    return count


def seed_orders(cursor, user_count=5000, product_count=20, order_count=100000):
    """插入订单数据"""
    statuses = ["paid", "paid", "paid", "paid", "shipped", "delivered", "delivered", "delivered", "refunded"]
    payment_methods = ["支付宝", "微信支付", "银行卡", "花呗", "信用卡"]

    # 获取商品价格和成本
    cursor.execute("SELECT product_id, price, cost, category_id FROM products")
    products = {row[0]: {"price": row[1], "cost": row[2], "category_id": row[3]} for row in cursor.fetchall()}

    # 获取用户地区
    cursor.execute("SELECT user_id, region FROM users")
    user_regions = {row[0]: row[1] for row in cursor.fetchall()}

    orders = []
    for order_id in range(1, order_count + 1):
        user_id = random.randint(1, user_count)
        product_id = random.randint(1, product_count)
        product = products[product_id]

        # 订单日期：最近 180 天，越近的日期概率越高
        days_ago = int(random.expovariate(1 / 30))
        days_ago = min(days_ago, 180)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 15, 7, 3])[0]

        # 价格有一定的随机折扣
        discount = random.uniform(0.8, 1.0)
        unit_price = round(product["price"] * discount, 2)
        total_amount = round(unit_price * quantity, 2)
        profit = round((unit_price - product["cost"]) * quantity, 2)

        status = random.choice(statuses)
        payment = random.choice(payment_methods)
        region = user_regions.get(user_id, "华东")

        orders.append((
            order_id, user_id, product_id, order_date,
            quantity, unit_price, total_amount, profit,
            status, payment, region,
        ))

    cursor.executemany("INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", orders)
    return order_count


def main():
    """主函数：创建数据库并填充数据"""
    os.makedirs(DB_DIR, exist_ok=True)

    # 如果数据库已存在，先删除
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"已删除旧数据库：{DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("正在创建表结构...")
    create_tables(cursor)

    print("正在插入品类数据...")
    seed_categories(cursor)

    print("正在插入商品数据...")
    product_count = seed_products(cursor)
    print(f"  已插入 {product_count} 个商品")

    print("正在插入用户数据...")
    user_count = seed_users(cursor)
    print(f"  已插入 {user_count} 个用户")

    print("正在插入订单数据（这可能需要几秒钟）...")
    order_count = seed_orders(cursor, user_count, product_count)
    print(f"  已插入 {order_count} 条订单")

    conn.commit()
    conn.close()

    file_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n数据库初始化完成！")
    print(f"  路径：{DB_PATH}")
    print(f"  大小：{file_size:.1f} MB")
    print(f"  品类：14 个")
    print(f"  商品：{product_count} 个")
    print(f"  用户：{user_count} 个")
    print(f"  订单：{order_count} 条")


if __name__ == "__main__":
    main()
