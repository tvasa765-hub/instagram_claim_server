from flask import Flask, request, render_template_string
import sqlite3

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

# --- Функция уведомлений (пока пустая, Telegram нет) ---
def send_telegram(text):
    pass  # уведомлений нет

# --- Главный роут ---
@app.route("/claim", methods=["GET", "POST"])
def claim():
    token = request.values.get("token")
    if not token:
        return "Токен не передан", 400

    # подключение к базе
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
        # показать форму
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

    # уведомление (пока пустое)
    send_telegram(f"Новый заказ!\nТокен: {token}\nНик: {username}\nКоличество: {quantity}")

    return f"Заказ принят! Ник: {username}, Количество: {quantity}"

@app.route("/")
def home():
    return "Server is running! Используй маршрут /claim для формы."

# --- Запуск локально ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
