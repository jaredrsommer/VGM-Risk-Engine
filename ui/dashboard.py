import requests
import time

while True:
    try:
        r = requests.get("http://localhost:8000/risk").json()
        print(f"VGM LIVE → W:{r['W']:.3f} | {r['action']}")
    except:
        pass
    time.sleep(1)