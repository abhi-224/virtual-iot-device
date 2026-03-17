# main.py
import time
from cnf import LATITUDE, LONGITUDE, PUBLISH_INTERVAL, TOPIC
from mqtt_client import init_mqtt
from db import buffer_data, close_db
import random
import datetime

# shared userdata between main and callbacks
userdata = {"connected": False, "shutdown": False}
client = init_mqtt(userdata)


def generate_sensor_data():

    current_ts = datetime.datetime.now()

    month = current_ts.month
    hour = current_ts.hour

    if 6 <= month <= 9:
        pm25_base = (10, 40)
        pm10_base = (20, 60)
    elif 10 <= month <= 11:
        pm25_base = (30, 80)
        pm10_base = (50, 120)
    elif 12 <= month <= 2:
        pm25_base = (70, 200)
        pm10_base = (100, 300)
    else:
        pm25_base = (20, 60)
        pm10_base = (30, 90)

    pm25_value = random.uniform(*pm25_base)
    pm10_value = random.uniform(*pm10_base)

    if hour in range(7, 10) or hour in range(17, 20):
        pm25_value *= random.uniform(1.1, 1.5)
        pm10_value *= random.uniform(1.1, 1.5)

    if random.random() < 0.02:  # 2% chance
        pm25_value *= random.uniform(1.5, 3.0)
        pm10_value *= random.uniform(1.5, 3.0)

    pm25_value = round(pm25_value)
    pm10_value = round(pm10_value)

    aqi_value, aqi_category = calculate_aqi(pm25_value, pm10_value)

    temperature = round(20 + 5 * (0.5 - random.random()), 1)
    humidity = round(50 + 10 * (0.5 - random.random()), 1)

    return {
        "ts": int(time.mktime(current_ts.timetuple()) * 1000),
        "temperature": temperature,
        "humidity": humidity,
        "pm25": pm25_value,
        "pm10": pm10_value,
        "aqi_value": aqi_value,
        "aqi_category": aqi_category,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
    }


def calculate_aqi(pm25, pm10):
    pm25_breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]

    pm10_breakpoints = [
        (0, 54, 0, 50),
        (55, 154, 51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ]

    def calc_individual_aqi(value, breakpoints):
        for c_low, c_high, i_low, i_high in breakpoints:
            if c_low <= value <= c_high:
                aqi = ((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low
                return round(aqi)
        return None

    aqi_pm25 = calc_individual_aqi(pm25, pm25_breakpoints)
    aqi_pm10 = calc_individual_aqi(pm10, pm10_breakpoints)

    aqi = max(aqi_pm25, aqi_pm10)

    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Moderate"
    elif aqi <= 150:
        category = "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        category = "Unhealthy"
    elif aqi <= 300:
        category = "Very Unhealthy"
    else:
        category = "Hazardous"

    return aqi, category


try:
    while True:
        data = generate_sensor_data()
        if userdata["connected"]:
            try:
                import json

                client.publish(
                    TOPIC,
                    json.dumps({"ts": data["ts"], "values": data}),
                )
                print(
                    f"[DATA SENT] PM2.5: {data['pm25']}, PM10: {data['pm10']}, AQI: {data['aqi_value']}, Category: {data['aqi_category']}"
                )
            except Exception as e:
                print(f"[WARN] Publish failed, buffering data: {e}")
                buffer_data(data)
        else:
            buffer_data(data)
        time.sleep(PUBLISH_INTERVAL)
except KeyboardInterrupt:
    print("\n[INFO] Exiting...")
    userdata["shutdown"] = True
finally:
    client.loop_stop()
    client.disconnect()
    close_db()
