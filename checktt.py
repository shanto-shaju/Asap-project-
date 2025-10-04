import os
import sqlite3

db_path = "database.db"  # update this if needed

print("Checking:", os.path.abspath(db_path))

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)

    # Check if wifi_data table has records
    cursor.execute("SELECT * FROM database;")
    rows = cursor.fetchall()
    print(f"Data in wifi_data table ({len(rows)} rows):")
    for row in rows:
        print(row)

except sqlite3.Error as e:
    print("SQLite error:", e)

finally:
    conn.close()
