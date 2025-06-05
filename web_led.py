from flask import Flask, request, render_template, abort
import serial
import json

# Загрузка конфигурации
with open("config.json") as f:
    config = json.load(f)

SECRET_TOKEN = config["secret_token"]

# Подключение к Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600)

app = Flask(__name__)

# Главная страница
@app.route("/", methods=["GET"])
def index():
    return render_template("lamp_token.html", token=SECRET_TOKEN)

# POST-запрос на управление светодиодом
@app.route("/set", methods=["POST"])
def control_led():
    state = request.form.get("state")
    token = request.form.get("token")

    if token != SECRET_TOKEN:
        print("🚫 Неверный токен")
        abort(403)

    if state in ["0", "1"]:
        arduino.write(state.encode())
        return f"LED set to {state}", 200

    return "Invalid value", 400

# Запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
