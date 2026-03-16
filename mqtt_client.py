import json
import time
import paho.mqtt.client as mqtt
from cnf import BROKER, PORT, ACCESS_TOKEN, TOPIC
from db import fetch_buffered_data, delete_buffered_data


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("[INFO] Connected to ThingsBoard")
        userdata["connected"] = True
        flush_buffered_data(client)
    else:
        print(f"[ERROR] Connection failed with code {rc}")


def on_disconnect(client, userdata, reasonCode=None, properties=None, *args):
    if userdata.get("shutdown"):
        print("[INFO] Disconnected cleanly.")
        return
    print(f"[WARN] Disconnected (reason code {reasonCode}), attempting reconnect...")
    userdata["connected"] = False
    try:
        client.reconnect()
        print("[INFO] Reconnected successfully")
        return
    except Exception as e:
        print(f"[ERROR] Reconnect attempt failed: {e}")
        time.sleep(5)
    exit(1)


def flush_buffered_data(client):
    rows = fetch_buffered_data()
    for row in rows:
        payload = {
            "ts": row[1],
            "values": {
                "temperature": row[2],
                "humidity": row[3],
                "pm25": row[4],
                "pm10": row[5],
                "latitude": row[6],
                "longitude": row[7],
            },
        }
        try:
            client.publish(TOPIC, json.dumps(payload))
            print(f"[FLUSHED] PM2.5: {row[4]}, PM10: {row[5]}")
            delete_buffered_data(row[0])
        except Exception as e:
            print(f"[ERROR] Failed to flush buffered data: {e}")
            break


def init_mqtt(userdata):
    client = mqtt.Client(
        client_id="",
        protocol=mqtt.MQTTv5,
        userdata=userdata,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    )
    client.username_pw_set(ACCESS_TOKEN)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f"[ERROR] Could not connect to broker: {e}")
        exit(1)
    client.loop_start()
    return client
