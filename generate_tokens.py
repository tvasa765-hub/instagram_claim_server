import sqlite3
import uuid

# Подключение к базе
conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

# --- Создаём таблицу tokens с полем quantity, если ещё нет ---
cur.execute("""
CREATE TABLE IF NOT EXISTS tokens (
    token TEXT PRIMARY KEY,
    used INTEGER DEFAULT 0,
    quantity INTEGER DEFAULT 0
)
""")

# --- Ввод данных для услуги ---
quantity = int(input("Введите количество подписчиков для этой услуги: "))
count = int(input("Сколько токенов создать? "))

# --- Генерация токенов ---
tokens = []
for _ in range(count):
    token = uuid.uuid4().hex
    tokens.append(token)
    cur.execute("INSERT INTO tokens (token, quantity) VALUES (?, ?)", (token, quantity))

conn.commit()
conn.close()

# --- Вывод созданных токенов ---
print(f"\nСоздано {count} токенов для услуги {quantity} подписчиков:")
for t in tokens:
    print(t)

