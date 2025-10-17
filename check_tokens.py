import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

cur.execute("SELECT token, used, quantity FROM tokens")
rows = cur.fetchall()
for r in rows:
    print(r)

conn.close()
