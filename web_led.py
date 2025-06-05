from flask import Flask, request, render_template, abort
import serial
import json
import os

# Загрузка разрешённых IP
with open("config.json") as f:
    config = json.load(f)

ALLOWED_IPS = config["allowed_ips"]

# Подключение к Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600)

# Flask-приложение
app = Flask(__name__)

# Проверка IP
@app.before_request
def limit_remote_addr():
    ip = request.remote_addr
    if ip not in ALLOWED_IPS:
        print(f"🚫 Блокировка доступа: {ip}")
        abort(403)

# Главная страница с кнопками
@app.route("/", methods=["GET"])
def index():
    return render_template("lamp.html")

# POST-запрос от кнопок
@app.route("/set", methods=["POST"])
def control_led():
    state = request.form.get("state")
    if state in ["0", "1"]:
        arduino.write(state.encode())
        return f"LED set to {state}", 200
    return "Invalid value", 400

# Запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
