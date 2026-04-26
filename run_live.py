from core.live_stream import LiveStream
from core.vgm_engine import VGMCore
from core.vgm_live import VGMLive
import threading
import requests

engine = VGMCore()
vgm = VGMLive(engine)

def send_to_api(result):
    try:
        requests.post("http://localhost:8000/update", json=result)
    except:
        pass

def on_data(prices):
    result = vgm.compute(prices)
    print(result)
    send_to_api(result)

stream = LiveStream("btcusdt")
stream.register(on_data)

t = threading.Thread(target=stream.start)
t.start()