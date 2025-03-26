
import time
import board
import adafruit_dht
from datetime import datetime  
import requests

# Sensor data pin is connected to GPIO 
sensor = adafruit_dht.DHT22(board.D17)
# Uncomment for DHT11
#sensor = adafruit_dht.DHT11(board.D4)


def report_to_telegram(message):    
    apiToken = '6502295888:AAH5Kfc4MuLk09rCLfxvcbZzTQ-M8aZaQOU'
    chatID = '399708611'
    # chatID = '-4501020289'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)


def background_task():
    print('Starttt')
    while True:
        try:
            # Print the values to the serial port
            temperature_c = sensor.temperature
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = sensor.humidity
            print("Background Check : Temp={0:0.1f}ºC, Temp={1:0.1f}ºF, Humidity={2:0.1f}%".format(temperature_c, temperature_f, humidity))
            if temperature_c >= 25:
                print(f"🚨🚨🚨🚨🚨\n\nAstagfirullah\n\nSuhu saat ini : {temperature_c}c\n\n{current_time}")
                report_to_telegram(
                    message = f"🚨🚨🚨🚨🚨\n\nWarning !!!\n\nSuhu Server UPA TIK Lt2 saat ini : {temperature_c}c\n\n{current_time}"
                )
            else:
                pass
        
        except RuntimeError as error:
            print(f"⚠️ Runtime Error: {error}")
            time.sleep(2.0)
            continue

        except Exception as error:
            print(f"❌ ERROR: {error}")
        
        time.sleep(10.0)  # Jangan terlalu cepat baca sensor, minimal 2 detik


if __name__ == "__main__":
    print('Start Background Task Monitoring Suhu')
    background_task()