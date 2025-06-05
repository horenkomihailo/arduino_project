from flask import Flask, request
import serial

# Укажи правильный порт для Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def control_led():
    state = request.form.get("state")
    if state in ["0", "1"]:
        arduino.write(state.encode())
        return f"LED set to {state}", 200
    return "Invalid value", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
