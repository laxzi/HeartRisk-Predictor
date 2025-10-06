import sqlite3

# Connect to your database
conn = sqlite3.connect(r"C:\Users\Sooryakant\Downloads\heart_disease_site\database.db")  # Replace with your DB filename
cur = conn.cursor()

# Get all table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()

for table_name_tuple in tables:
    table_name = table_name_tuple[0]

    # Skip internal SQLite table
    if table_name == "sqlite_sequence":
        continue

    print(f"\n=== Table: {table_name} ===")

    # Get column names
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cur.fetchall()]
    print(" | ".join(columns))
    print("-" * (len(" | ".join(columns))))

    # Fetch and print all rows
    cur.execute(f"SELECT * FROM {table_name}")
    for row in cur.fetchall():
        print(" | ".join(str(item) for item in row))

conn.close()

