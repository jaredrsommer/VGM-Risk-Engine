from flask import Flask, request, jsonify
from core.vgm_v9_institutional import VGMv9Institutional

app = Flask(__name__)
engine = VGMv9Institutional()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM INSTITUTIONAL QUANT SYSTEM V9",
        "type": "multi-layer ensemble RL + risk engine",
        "features": [
            "ensemble policy (RL + VGM + NN)",
            "portfolio risk control",
            "adaptive weight learning",
            "execution simulation",
            "institutional architecture"
        ],
        "endpoints": ["/step", "/state"]
    })


@app.route("/step", methods=["POST"])
def step():
    d = request.get_json()

    state_input = d.get("state", {"vgm": (0.5, 0.2, 0.2), "x": [0.1]*10})
    vol = float(d.get("vol", 0.2))
    dd = float(d.get("drawdown", 0.1))
    market_return = float(d.get("market_return", 0.01))

    result = engine.step(state_input, vol, dd, market_return)

    global state
    state = result

    return jsonify(result)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM INSTITUTIONAL V9 STARTED")
    app.run(port=8000)