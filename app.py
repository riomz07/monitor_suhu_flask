
from flask import Flask, render_template, jsonify
import time
import board
import adafruit_dht
from datetime import datetime  
import requests
import threading
import sqlite3

app = Flask(__name__)

def save_data_to_db(temperature, humidity):
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (temperature, humidity)
        VALUES (?, ?)
    ''', (temperature, humidity))
    conn.commit()
    conn.close()

# Sensor data pin is connected to GPIO 
sensor = adafruit_dht.DHT22(board.D17)
# Uncomment for DHT11
#sensor = adafruit_dht.DHT11(board.D4)


def report_to_telegram(message):    
    apiToken = '6502295888:AAH5Kfc4MuLk09rCLfxvcbZzTQ-M8aZaQOU'
    # chatID = '399708611'
    chatID = '-4501020289'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


def background_task():
    while True:
        try:
            # Print the values to the serial port
            temperature_c = sensor.temperature
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = sensor.humidity
            print("Background Check : Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
            save_data_to_db(temperature_c, humidity)
            if temperature_c >= 25:
                print(f"🚨🚨🚨🚨🚨\n\nAstagfirullah\n\nSuhu saat ini : {temperature_c}c\n\n{current_time}")
                report_to_telegram(
                    message = f"🚨🚨🚨🚨🚨\n\nWarning !!!\n\nSuhu Server UPA TIK Lt2 saat ini : {temperature_c}c\n\n{current_time}"
                )
            else:
                pass

        except Exception as error:
            print(f"⚠️ ERROR: {error}")  # Log error agar bisa dilihat
            # report_to_telegram(f"⚠️ ERROR: {error}")  # Bisa dikirim ke Telegram

        finally:
            time.sleep(30.0)  # Delay 5 detik agar tidak terlalu sering looping


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-notif')
def test_notif():
    try:
        report_to_telegram(message='Testing...')
        return jsonify(data='Sukses Terkirim')
    except Exception as e :
        return jsonify(data=e)


@app.route('/sensor-data')
def sensor_data():

    try:
        conn = sqlite3.connect('monitor.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1')
        rows = cursor.fetchone()
        conn.close()
        # Dapatkan waktu saat ini
        current_time = rows[3]
        # Print the values to the serial port
        temperature_c = rows[1]
        humidity = rows[2]

        # Render halaman web dengan data
        # return render_template('index.html', temperature=temperature_c, humidity=humidity, current_time=current_time)

        if humidity is not None and temperature_c is not None:
            print('Ada Data')
            data = {
            'temperature': temperature_c,
            'humidity': humidity,
            'current_time': current_time
            }
        else:
            print('No Data')
            data = {
                'temperature': 'Loading...',
                'humidity': 'Loading...',
                'current_time': '....'
            }
        
        return jsonify(data)

    except Exception as error:
        response = jsonify({'error': 'Something Wrong'})
        print(error)
        response.status_code = 404
        return response
   

@app.route('/history')
def sensor_history():
    conn = sqlite3.connect('monitor.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 5')
    rows = cursor.fetchall()
    conn.close()

    history = [
        {"id": row[0], "temperature": row[1], "humidity": row[2], "timestamp": row[3]}
        for row in rows
    ]
    return jsonify(history)


# 🛠️ **Jalankan background task sebagai daemon**
thread = threading.Thread(target=background_task, daemon=True)
thread.start()

if __name__ == '__main__':
    # Jalankan tugas latar belakang
    app.run(host='0.0.0.0', port=5000)
