import sqlite3
from pathlib import Path


DB_PATH = Path("shop.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            product_price INTEGER DEFAULT 0,
            buyer_telegram_id INTEGER NOT NULL,
            buyer_username TEXT,
            buyer_full_name TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_product(name: str, category: str, price: int, description: str = ""):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, category, description, price)
        VALUES (?, ?, ?, ?)
        """,
        (name, category, description, price),
    )

    connection.commit()
    connection.close()


def get_all_products():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, category, description, price
        FROM products
        WHERE is_active = 1
        ORDER BY id DESC
        """
    )

    products = cursor.fetchall()

    connection.close()

    return products


def get_product_by_id(product_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, category, description, price
        FROM products
        WHERE id = ? AND is_active = 1
        """,
        (product_id,),
    )

    product = cursor.fetchone()
    connection.close()

    return product


def delete_product(product_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE products
        SET is_active = 0
        WHERE id = ?
        """,
        (product_id,),
    )

    connection.commit()
    connection.close()


def create_order(
    product_id: int,
    buyer_telegram_id: int,
    buyer_username: str = "",
    buyer_full_name: str = "",
):
    product = get_product_by_id(product_id)

    if not product:
        return None

    _, name, _, _, price = product

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO orders (
            product_id,
            product_name,
            product_price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            product_id,
            name,
            price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name,
        ),
    )

    order_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return order_id


def get_all_orders(limit: int = 20):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            product_name,
            product_price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name,
            status,
            created_at
        FROM orders
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    orders = cursor.fetchall()
    connection.close()

    return orders
