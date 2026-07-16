import sqlite3

conn = sqlite3.connect("medicare.db")
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE chats
ADD COLUMN conversation_id INTEGER
""")

conn.commit()
conn.close()

print("Column added successfully!")