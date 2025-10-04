import sqlite3

# Connect to the database
conn = sqlite3.connect("wifi_data.db")
cursor = conn.cursor()

# Fetch all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in wifi_data.db:")
for table in tables:
    print(table[0])

conn.close()