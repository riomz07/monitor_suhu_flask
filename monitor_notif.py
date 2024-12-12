# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-dht11-dht22-python/
# Based on Adafruit_CircuitPython_DHT Library Example

import time
import board
import adafruit_dht
import requests
from datetime import datetime  

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

while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = sensor.humidity
        print("Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))

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
