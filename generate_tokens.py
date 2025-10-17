import sqlite3, uuid

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

# Генерация 10 токенов
for _ in range(10):
    token = uuid.uuid4().hex
    cur.execute("INSERT INTO tokens (token) VALUES (?)", (token,))
conn.commit()
conn.close()
print("Токены созданы")
