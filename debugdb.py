import sqlite3
import os

db_path = r"C:\Users\HI\Desktop\asap project\instance\database.db."
print("Checking database:", db_path)
print("Exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables found:", tables)

# Preview first table content if any
if tables:
    table_name = tables[0][0]
    print(f"\nPreviewing data from table: {table_name}")
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 50;")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
else:
    print("No tables found in the database.")

conn.close()
