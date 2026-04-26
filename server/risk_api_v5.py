from flask import Flask, request, jsonify
from core.vgm_v5_quant import VGMv5QuantEngine
import numpy as np

app = Flask(__name__)
engine = VGMv5QuantEngine()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM QUANT ENGINE V5",
        "type": "research + execution simulator",
        "features": [
            "adaptive weights",
            "portfolio risk",
            "PnL learning loop",
            "NN + VGM synergy"
        ]
    })


@app.route("/step", methods=["POST"])
def step():
    d = request.get_json()

    W = float(d.get("W", 0.5))
    vol = float(d.get("vol", 0.2))
    tail = float(d.get("tail", 0.2))
    x = d.get("x", [0.1, 0.2, 0.3])
    market_move = float(d.get("market_move", 0.01))
    corr = d.get("corr_matrix", [[0.1]])

    result = engine.step(W, vol, tail, x, market_move, corr)

    global state
    state = result

    return jsonify(result)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM QUANT ENGINE V5 STARTED")
    app.run(port=8000)