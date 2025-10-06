import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
               ("testuser", "testpass"))

conn.commit()
conn.close()
print("Test user added!")
