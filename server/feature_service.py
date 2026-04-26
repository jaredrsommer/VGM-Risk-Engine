from fastapi import FastAPI
from kafka import KafkaConsumer
import json
import numpy as np
import threading
from collections import deque

app = FastAPI()

# =========================
# SHARED STATE (thread-safe buffer)
# =========================
buffer = deque(maxlen=50)

# =========================
# KAFKA CONSUMER (BACKGROUND THREAD)
# =========================
def kafka_stream():
    consumer = KafkaConsumer(
        'market-data',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True
    )

    for msg in consumer:
        price = msg.value.get("price")

        if price is not None:
            buffer.append(float(price))


# Start Kafka in background
threading.Thread(target=kafka_stream, daemon=True).start()


# =========================
# FEATURE ENGINE
# =========================
def features(prices):
    p = np.array(prices)

    if len(p) < 2:
        return {
            "mean": 0.0,
            "std": 0.0,
            "trend": 0.0,
            "volatility": 0.0,
            "status": "warming_up"
        }

    r = np.diff(p)

    return {
        "mean": float(np.mean(r)),
        "std": float(np.std(r)),
        "trend": float(p[-1] - p[0]),
        "volatility": float(np.std(p)),
        "last_price": float(p[-1])
    }


# =========================
# API ENDPOINTS
# =========================

@app.get("/")
def root():
    return {
        "status": "VGM FEATURE SERVICE RUNNING",
        "mode": "kafka_streaming",
        "buffer_size": len(buffer)
    }


@app.get("/features")
def get_features():
    return features(list(buffer))


@app.get("/health")
def health():
    return {"ok": True, "buffer": len(buffer)}