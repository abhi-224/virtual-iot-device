# main.py
import time
from cnf import LATITUDE, LONGITUDE, PUBLISH_INTERVAL, TOPIC
from mqtt_client import init_mqtt
from db import buffer_data, close_db

import random

# shared userdata between main and callbacks
userdata = {"connected": False, "shutdown": False}
client = init_mqtt(userdata)


def generate_sensor_data():
    return {
        "ts": int(time.time() * 1000),
        "temperature": round(20 + 5 * (0.5 - random.random()), 1),
        "humidity": round(50 + 10 * (0.5 - random.random()), 1),
        "pm25": int(100 + 50 * (0.5 - random.random())),
        "pm10": int(180 + 30 * (0.5 - random.random())),
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
    }


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
                print(f"[DATA SENT] PM2.5: {data['pm25']}, PM10: {data['pm10']}")
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
