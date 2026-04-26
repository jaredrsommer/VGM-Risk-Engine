from kafka import KafkaProducer
import json
import random
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def stream_market():
    price = 100.0

    while True:
        price += random.uniform(-1, 1)

        event = {
            "symbol": "BTCUSDT",
            "price": price,
            "volume": random.random(),
            "timestamp": time.time()
        }

        producer.send("market-data", event)
        print("sent:", event)

        time.sleep(0.5)

if __name__ == "__main__":
    stream_market()