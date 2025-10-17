from flask import Flask, request, render_template_string
import sqlite3
import requests

app = Flask(__name__)

# --- HTML форма ---
FORM_HTML = """
<h2>Укажите ник и количество</h2>
<form method="post">
  <input type="hidden" name="token" value="{{token}}">
  Ник: <input name="username" required><br>
  Количество: <input type="number" name="quantity" min="1" required><br>
  <button type="submit">Отправить</button>
</form>
"""

# --- Telegram уведомления ---
BOT_TOKEN = "8266250354:AAHp6fCgA7Q3TnyuUZ2_6ueZAucO4kWVpdQ"
CHAT_ID = "5737355586"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Ошибка при отправке Telegram:", e)

# --- Главный роут /claim ---
@app.route("/claim", methods=["GET", "POST"])
def claim():
    token = request.values.get("token")
    if not token:
        return "Токен не передан", 400

    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()

    # проверка токена
    cur.execute("SELECT used FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return "Неверный токен", 400
    if row[0]:
        conn.close()
        return "Этот токен уже использован", 400

    if request.method == "GET":
        return render_template_string(FORM_HTML, token=token)

    # POST — обработка формы
    username = request.form.get("username").strip()
    quantity = request.form.get("quantity").strip()
    if not username or not quantity:
        conn.close()
        return "Неверные данные", 400

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError
    except:
        conn.close()
        return "Неверное количество", 400

    # сохранить заказ
    cur.execute("INSERT INTO orders (token, username, quantity) VALUES (?,?,?)",
                (token, username, quantity))
    # пометить токен как использованный
    cur.execute("UPDATE tokens SET used=1 WHERE token=?", (token,))
    conn.commit()
    conn.close()

    # уведомление в Telegram
    send_telegram(f"Новый заказ!\nТокен: {token}\nНик: {username}\nКоличество: {quantity}")

    return f"Заказ принят! Ник: {username}, Количество: {quantity}"

# --- Маршрут / для проверки ---
@app.route("/")
def home():
    return "Server is running! Используй маршрут /claim для формы."

# --- Маршрут /orders для просмотра всех заказов ---
@app.route("/orders")
def orders():
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT id, token, username, quantity FROM orders ORDER BY id DESC")
    all_orders = cur.fetchall()
    conn.close()

    html = "<h2>Все заказы</h2><table border='1'><tr><th>ID</th><th>Токен</th><th>Ник</th><th>Количество</th></tr>"
    for order in all_orders:
        html += f"<tr><td>{order[0]}</td><td>{order[1]}</td><td>{order[2]}</td><td>{order[3]}</td></tr>"
    html += "</table>"
    return html

# --- Запуск ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
