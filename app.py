
from flask import Flask, render_template, jsonify
from datetime import datetime  
import time
import board
import adafruit_dht
import threading
import sqlite3

app = Flask(__name__)

# Sensor data pin is connected to GPIO 4
sensor = adafruit_dht.DHT22(board.D17)
# Uncomment for DHT11
#sensor = adafruit_dht.DHT11(board.D4)


def save_to_db(temperature, humidity):
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (temperature, humidity)
        VALUES (?, ?)
    ''', (temperature, humidity))
    conn.commit()
    conn.close()


def background_task():
    while True:
        try:
            # Print the values to the serial port
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            temperature_c = sensor.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = sensor.humidity
            print("Background Cek : Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))

            if temperature_c >= 25:
                print(f"🚨🚨🚨🚨🚨\n\Warning\n\nSuhu saat ini : {temperature_c}c\n\n{current_time}")
                save_to_db(temperature_c, humidity)
            else:
                pass

        except Exception as error:
            print(error)

        time.sleep(5.0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensor')
def sensor_data():
    try:
        # Ambil waktu saat ini
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature_c = sensor.temperature
        humidity = sensor.humidity

        data = {
        'temperature': temperature_c,
        'humidity': humidity,
        'current_time': current_time
        }
        
        return jsonify(data)

    except Exception as error:
        response = jsonify({'error': 'Something Wrong'})
        response.status_code = 404
        return response
    
@app.route('/history')
def get_sensor_history():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100')
    rows = cursor.fetchall()
    conn.close()

    history = [
        {"id": row[0], "temperature": row[1], "humidity": row[2], "timestamp": row[3]}
        for row in rows
    ]
    return jsonify(history)


if __name__ == '__main__':
    # Jalankan tugas latar belakang
    threading.Thread(target=background_task).start()
    app.run(host='0.0.0.0', port=5001)
