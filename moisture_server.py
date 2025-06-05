from flask import Flask, jsonify, render_template
from flask_cors import CORS
import serial
import time
import csv
from datetime import datetime
import threading

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

app = Flask(__name__)
CORS(app)

def auto_read_loop():
    while True:
        try:
            arduino.write(b"M")
            time.sleep(0.5)
            if arduino.in_waiting:
                line = arduino.readline().decode().strip()
                value = int(line)
                percent = max(0, min(100, int((value / 700) * 100)))
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                with open("moisture_log.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, value, percent])

            time.sleep(3600)  # раз в час — 3600 секунд
        except Exception as e:
            print(f"[ERROR auto read]: {e}")
            time.sleep(60)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/moisture", methods=["GET"])
def get_moisture():
    arduino.write(b"M")
    time.sleep(0.5)
    if arduino.in_waiting:
        line = arduino.readline().decode().strip()
        try:
            value = int(line)
            percent = max(0, min(100, int((value / 700) * 100)))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Сохраняем в CSV
            with open("moisture_log.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, value, percent])

            return jsonify({"value": value, "percent": percent, "time": timestamp})
        except:
            return jsonify({"error": "Invalid response"}), 500
    return jsonify({"error": "No response"}), 500


@app.route("/history", methods=["GET"])
def history():
    data = []
    try:
        with open("moisture_log.csv", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                data.append({"time": row[0], "value": int(row[1]), "percent": int(row[2])})
    except FileNotFoundError:
        pass
    return jsonify(data)


@app.route("/clear", methods=["POST"])
def clear_data():
    open("moisture_log.csv", "w").close()  # просто очищает файл
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    threading.Thread(target=auto_read_loop, daemon=True).start()
    app.run(port=5000)
