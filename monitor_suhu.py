
from flask import Flask, render_template, jsonify
import time
import board
import adafruit_dht
from datetime import datetime  
import requests
import threading

app = Flask(__name__)

# Sensor data pin is connected to GPIO 4
sensor = adafruit_dht.DHT22(board.D17)
# Uncomment for DHT11
#sensor = adafruit_dht.DHT11(board.D4)


def report_to_telegram(message):    
    apiToken = '6502295888:AAH5Kfc4MuLk09rCLfxvcbZzTQ-M8aZaQOU'
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
            print("Notif : Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))

            if temperature_c >= 25:
                report_to_telegram(
                    message = f"🚨🚨🚨🚨🚨\n\nAstagfirullah\n\nSuhu saat ini : {temperature_c}c\n\n{current_time}"
                )
            else:
                pass

        except Exception as error:
            report_to_telegram(
                message = error
            )

        time.sleep(5.0)


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
        # Dapatkan waktu saat ini
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Print the values to the serial port
        temperature_c = sensor.temperature
        humidity = sensor.humidity

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
                'current_time': current_time
            }
        
        return jsonify(data)

    except Exception as error:
        response = jsonify({'error': 'Something Wrong'})
        response.status_code = 404
        return response


if __name__ == '__main__':
    # Jalankan tugas latar belakang
    threading.Thread(target=background_task).start()
    app.run(host='0.0.0.0', port=5000)
