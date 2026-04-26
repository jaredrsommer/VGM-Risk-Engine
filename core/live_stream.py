import websocket
import json
import numpy as np
from collections import deque

class LiveStream:
    def __init__(self, symbol="btcusdt"):
        self.symbol = symbol
        self.buffer = deque(maxlen=200)
        self.callbacks = []

    def on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['p']) if 'p' in data else None

        if price:
            self.buffer.append(price)

            for cb in self.callbacks:
                cb(list(self.buffer))

    def on_open(self, ws):
        print("📡 Live stream started")

    def start(self):
        url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

        ws = websocket.WebSocketApp(
            url,
            on_message=self.on_message,
            on_open=self.on_open
        )

        ws.run_forever()

    def register(self, callback):
        self.callbacks.append(callback)