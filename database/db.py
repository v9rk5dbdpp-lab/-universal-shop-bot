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