import sqlite3

conn = sqlite3.connect('logs/predictions.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Read all rows from a table (replace 'your_table_name' with actual table name)
cursor.execute("SELECT * FROM predictions;")
rows = cursor.fetchall()
for row in rows:
    # print(row)
    pass

cursor.execute("PRAGMA table_info(predictions);")
columns = cursor.fetchall()

print("Columns in 'predictions' table:")
for col in columns:
    print(f"{col[1]} ({col[2]})")

conn.close()