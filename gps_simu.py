import requests
import random
import time
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/position"
DEVICE_ID = "camion-1"

lat, lon = 33.7897, -7.1575

while True:
    lat += random.uniform(-0.0002, 0.0002)
    lon += random.uniform(-0.0002, 0.0002)

    camion_data = \
        {
            "device_id": DEVICE_ID,
            "latitude": lat,
            "longitude": lon,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "accuracy": round(random.uniform(3, 15), 1),
            "speed": round(random.uniform(0, 20), 1),
        }

    try:
        response = requests.post(API_URL, json=camion_data)
        print(response.status_code, response.json())
    except Exception as e:
        print("Error concernant l'envoi de la position", e)
    time.sleep(5)

