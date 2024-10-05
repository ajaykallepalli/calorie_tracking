import sqlite3
from pprint import pprint

def print_database_contents(db_path='app.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        print("-" * 20)

        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print("Schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")

        # Get table contents
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print("\nContents:")
        for row in rows:
            pprint(dict(zip([column[1] for column in columns], row)))

    conn.close()

# Usage
print_database_contents('app.db')