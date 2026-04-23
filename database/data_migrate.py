import sqlite3

import os
#DB_DIR = os.path.dirname(os.path.abspath(__file__))
#OLD_DB = os.path.join(DB_DIR, "stationery.db")
#NEW_DB = os.path.join(DB_DIR, "POS_Data.db")



# File paths
OLD_DB = "stationery.db"
NEW_DB = "POS_Data.db"

OLD_TABLE = "stock_batch"
NEW_TABLE = "stock"

def migrate_data():
    # Connect to old database
    old_conn = sqlite3.connect(OLD_DB)
    old_cursor = old_conn.cursor()

    # Connect to new database (will be created if not exists)
    new_conn = sqlite3.connect(NEW_DB)
    new_cursor = new_conn.cursor()

    # Create new table
    new_cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {NEW_TABLE} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code INTEGER,
        cost REAL,
        mrp REAL,
        price REAL,
        quantity INTEGER,
        in_stock INTEGER,
        date INTEGER,
        remark TEXT
    )
    """)

    # Fetch data from old table
    old_cursor.execute(f"""
        SELECT item_code, wp, mrp, discount_price,
               quantity, in_stock, date, Remark
        FROM {OLD_TABLE}
    """)

    rows = old_cursor.fetchall()

    # Insert into new table
    for row in rows:
        new_cursor.execute(f"""
            INSERT INTO {NEW_TABLE} (
                item_code, cost, mrp, price,
                quantity, in_stock, date, remark
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, row)

    # Commit changes
    new_conn.commit()

    # Close connections
    old_conn.close()
    new_conn.close()

    print("✅ Data migration completed successfully!")

if __name__ == "__main__":
    migrate_data()