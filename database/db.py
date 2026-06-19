import sqlite3
from pathlib import Path


DB_PATH = Path("shop.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(column[1] == column_name for column in columns)


def add_column_if_missing(cursor, table_name: str, column_name: str, column_sql: str):
    if not column_exists(cursor, table_name, column_name):
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}")


def split_digital_items(digital_content: str) -> list[str]:
    return [line.strip() for line in digital_content.splitlines() if line.strip()]


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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS digital_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            used_order_id INTEGER,
            used_at TIMESTAMP
        )
    """)

    add_column_if_missing(cursor, "products", "digital_content", "digital_content TEXT")
    add_column_if_missing(cursor, "orders", "digital_content", "digital_content TEXT")
    add_column_if_missing(cursor, "orders", "delivered_content", "delivered_content TEXT")

    connection.commit()
    connection.close()


def add_product(
    name: str,
    category: str,
    price: int,
    description: str = "",
    digital_content: str = "",
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, category, description, price, digital_content)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, category, description, price, digital_content),
    )

    product_id = cursor.lastrowid

    for item in split_digital_items(digital_content):
        cursor.execute(
            """
            INSERT INTO digital_items (product_id, content)
            VALUES (?, ?)
            """,
            (product_id, item),
        )

    connection.commit()
    connection.close()

    return product_id


def get_all_products():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, category, description, price, digital_content
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
        SELECT id, name, category, description, price, digital_content
        FROM products
        WHERE id = ? AND is_active = 1
        """,
        (product_id,),
    )

    product = cursor.fetchone()
    connection.close()

    return product


def get_available_digital_count(product_id: int) -> int:
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM digital_items
        WHERE product_id = ? AND is_used = 0
        """,
        (product_id,),
    )

    count = cursor.fetchone()[0]
    connection.close()

    return count


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

    _, name, _, _, price, digital_content = product

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
            buyer_full_name,
            digital_content
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            product_id,
            name,
            price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name,
            digital_content,
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
            product_id,
            product_name,
            product_price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name,
            status,
            created_at,
            delivered_content
        FROM orders
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )

    orders = cursor.fetchall()
    connection.close()

    return orders


def get_order_by_id(order_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            product_id,
            product_name,
            product_price,
            buyer_telegram_id,
            buyer_username,
            buyer_full_name,
            status,
            created_at,
            delivered_content
        FROM orders
        WHERE id = ?
        """,
        (order_id,),
    )

    order = cursor.fetchone()
    connection.close()

    return order


def take_next_digital_item(product_id: int, order_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("BEGIN IMMEDIATE")

    cursor.execute(
        """
        SELECT id, content
        FROM digital_items
        WHERE product_id = ? AND is_used = 0
        ORDER BY id ASC
        LIMIT 1
        """,
        (product_id,),
    )

    item = cursor.fetchone()

    if not item:
        connection.rollback()
        connection.close()
        return None

    item_id, content = item

    cursor.execute(
        """
        UPDATE digital_items
        SET is_used = 1,
            used_order_id = ?,
            used_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (order_id, item_id),
    )

    cursor.execute(
        """
        UPDATE orders
        SET delivered_content = ?,
            status = 'done'
        WHERE id = ?
        """,
        (content, order_id),
    )

    connection.commit()
    connection.close()

    return content


def mark_order_done(order_id: int, delivered_content: str = ""):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE orders
        SET status = 'done',
            delivered_content = COALESCE(NULLIF(?, ''), delivered_content)
        WHERE id = ?
        """,
        (delivered_content, order_id),
    )

    connection.commit()
    connection.close()
