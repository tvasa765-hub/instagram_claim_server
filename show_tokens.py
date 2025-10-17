import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

print("Доступные токены:\n")

try:
    cur.execute("SELECT token, used, quantity FROM tokens")
    rows = cur.fetchall()

    if not rows:
        print("⚠️ Нет токенов в базе.")
    else:
        for token, used, quantity in rows:
            status = "✅ свободен" if used == 0 else "❌ использован"
            print(f"{token} | {status} | {quantity} подписчиков")

except Exception as e:
    print("Ошибка при чтении базы:", e)

conn.close()

