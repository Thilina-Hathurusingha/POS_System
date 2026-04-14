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
    CREATE TABLE IF NOT EXISTS category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT,
    )
    """)
    conn.commit()

    '''cursor.execute("""
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
    conn.commit()'''


def migrate_data(old_conn, new_conn):
    print("🔄 Migrating data from stationery.db to POS_Data.db...")
    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    old_cursor.execute("SELECT * FROM category")
    rows = old_cursor.fetchall()

    for row in rows:
        (
            category_id,
            name,
            item_code,
            category_code
        ) = row


        new_cursor.execute("""
        INSERT INTO category (
            category_name
        )
        VALUES (?)
        """, (
            name
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