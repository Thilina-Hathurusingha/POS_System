import sqlite3

# مسیر (paths)
import os
DB_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_DB = os.path.join(DB_DIR, "stationery.db")
NEW_DB = os.path.join(DB_DIR, "POS_Data.db")

def create_new_table(conn):
    print("📦 Creating new products table in POS_Data.db...")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        cost REAL,
        mrp REAL,
        discount_price REAL,
        total_in_stock INTEGER,
        in_stock INTEGER,
        batch_id INTEGER,
        category_id INTEGER,
        vendor_id INTEGER,
        label1 INTEGER,
        is_subproduct BOOLEAN,
        parent_product_id INTEGER,
        active BOOLEAN
    )
    """)
    conn.commit()


def migrate_data(old_conn, new_conn):
    print("🔄 Migrating data from stationery.db to POS_Data.db...")
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    old_cursor.execute("SELECT * FROM products")
    rows = old_cursor.fetchall()

    for row in rows:
        (
            item_code,
            name,
            description,
            wp,
            mrp,
            discount_price,
            stock,
            batch_stock,
            batch_id,
            category_id,
            vendor_id,
            image
        ) = row

        # Handle NULLs safely
        cost = wp if wp is not None else 0.0
        total_in_stock = stock if stock is not None else 0
        in_stock = batch_stock if batch_stock is not None else 0

        new_cursor.execute("""
        INSERT INTO products (
            name,
            description,
            cost,
            mrp,
            discount_price,
            total_in_stock,
            in_stock,
            batch_id,
            category_id,
            vendor_id,
            label1,
            is_subproduct,
            parent_product_id,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            description,
            cost,
            mrp,
            discount_price,
            total_in_stock,
            in_stock,
            batch_id,
            category_id,
            vendor_id,
            1,          # label1
            0,          # is_subproduct (False)
            0,          # parent_product_id
            1           # active (True)
        ))

    new_conn.commit()


def main():
    old_conn = sqlite3.connect(OLD_DB)
    new_conn = sqlite3.connect(NEW_DB)

    create_new_table(new_conn)
    migrate_data(old_conn, new_conn)

    old_conn.close()
    new_conn.close()

    print("✅ Migration completed successfully!")


if __name__ == "__main__":
    main()