import sqlite3

def check_table_exists(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    conn.close()
    return result is not None

def print_table_schema(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    result = cursor.fetchone()
    conn.close()
    if result:
        print(f"Schema for table '{table_name}':")
        print(result[0])
    else:
        print(f"Table '{table_name}' does not exist")

if __name__ == "__main__":
    db_path = "manajemen_pelanggan.db"
    tables = ["pengguna", "pelanggan", "tagihan", "akuntansi"]
    
    for table in tables:
        exists = check_table_exists(db_path, table)
        print(f"Table '{table}' exists: {exists}")
        if exists:
            print_table_schema(db_path, table)
        print()