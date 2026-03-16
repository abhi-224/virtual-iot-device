import sqlite3
from cnf import DB

conn = sqlite3.connect(DB, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS buffered_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER,
    temperature REAL,
    humidity REAL,
    pm25 INTEGER,
    pm10 INTEGER,
    latitude REAL,
    longitude REAL
)
""")
conn.commit()


def buffer_data(sensor_data):
    cursor.execute(
        """
        INSERT INTO buffered_data
        (timestamp, temperature, humidity, pm25, pm10, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            int(sensor_data["ts"]),
            sensor_data["temperature"],
            sensor_data["humidity"],
            sensor_data["pm25"],
            sensor_data["pm10"],
            sensor_data["latitude"],
            sensor_data["longitude"],
        ),
    )
    conn.commit()
    print(f"[BUFFERED] PM2.5: {sensor_data['pm25']}, PM10: {sensor_data['pm10']}")


def fetch_buffered_data():
    cursor.execute("SELECT * FROM buffered_data ORDER BY id ASC")
    return cursor.fetchall()


def delete_buffered_data(record_id):
    cursor.execute("DELETE FROM buffered_data WHERE id = ?", (record_id,))
    conn.commit()


def close_db():
    conn.close()
