from flask import Flask, request, render_template_string
import sqlite3
import requests
from flask import Flask, request, render_template_string, render_template

app = Flask(__name__)

# --- Telegram настройки ---
BOT_TOKEN = "8266250354:AAHp6fCgA7Q3TnyuUZ2_6ueZAucO4kWVpdQ"
CHAT_ID = "5737355586"

# --- HTML форма с красивым дизайном ---
FORM_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Получение услуги</title>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #6C63FF, #48C6EF);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #333;
        }
        .card {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            width: 320px;
            text-align: center;
            animation: fadeIn 0.8s ease-in-out;
        }
        h2 {
            margin-bottom: 25px;
        }
        input {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 16px;
            transition: 0.3s;
        }
        input:focus {
            border-color: #6C63FF;
            box-shadow: 0 0 6px rgba(108,99,255,0.4);
        }
        button {
            margin-top: 20px;
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: #6C63FF;
            color: white;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }
        button:hover {
            background: #5548F8;
            transform: scale(1.03);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Введите ник</h2>
        <form method="post">
            <input type="hidden" name="token" value="{{token}}">
            <input name="username" placeholder="Ваш ник..." required>
            <button type="submit">Отправить</button>
        </form>
    </div>
</body>
</html>
"""

# --- HTML после успешной отправки ---
SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Спасибо!</title>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #6C63FF, #48C6EF);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            color: white;
            text-align: center;
        }
        .msg {
            font-size: 24px;
            background: rgba(255,255,255,0.15);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(8px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: scale(0.9);}
            to {opacity: 1; transform: scale(1);}
        }
    </style>
</head>
<body>
    <div class="msg">
        <h1>Спасибо, {{username}} 🎉</h1>
        <p>Ваш заказ принят! Количество: {{quantity}}</p>
    </div>
</body>
</html>
"""

def send_telegram(text):
    """Отправка уведомления в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("Ошибка при отправке Telegram:", e)

# --- Основной маршрут ---
@app.route("/claim", methods=["GET", "POST"])
def claim():
    token = request.values.get("token")
    if not token:
        return "❌ Токен не передан", 400

    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT used, quantity FROM tokens WHERE token=?", (token,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return "❌ Неверный токен", 400

    used, quantity = row
    if used:
        conn.close()
        return render_template("used_token.html")

    if request.method == "GET":
        conn.close()
        return render_template_string(FORM_HTML, token=token)

    # POST-запрос (пользователь отправил форму)
    username = request.form.get("username", "").strip()
    if not username:
        conn.close()
        return "❌ Укажите ник", 400

    # Сохраняем заказ и отмечаем токен как использованный
    cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, username TEXT, quantity INTEGER)")
    cur.execute("INSERT INTO orders (token, username, quantity) VALUES (?, ?, ?)", (token, username, quantity))
    cur.execute("UPDATE tokens SET used = 1 WHERE token=?", (token,))
    conn.commit()
    conn.close()

    send_telegram(f"📦 Новый заказ!\nНик: {username}\nТокен: {token}\nКоличество: {quantity}")

    return render_template_string(SUCCESS_HTML, username=username, quantity=quantity)

@app.route("/")
def home():
    return "✅ Сервер работает! Используй /claim?token=..."

@app.route("/orders")
def orders():
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute("SELECT id, token, username, quantity FROM orders ORDER BY id DESC")
    all_orders = cur.fetchall()
    conn.close()

    html = "<h2>Все заказы</h2><table border='1' cellpadding='6'><tr><th>ID</th><th>Токен</th><th>Ник</th><th>Количество</th></tr>"
    for o in all_orders:
        html += f"<tr><td>{o[0]}</td><td>{o[1]}</td><td>{o[2]}</td><td>{o[3]}</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
