import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

# Добавляем колонку quantity, если её нет
try:
    cur.execute("ALTER TABLE tokens ADD COLUMN quantity INTEGER DEFAULT 0")
    print("Колонка quantity добавлена")
except sqlite3.OperationalError:
    print("Колонка quantity уже существует")

conn.commit()
conn.close()
