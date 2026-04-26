from flask import Flask, request, jsonify
from core.vgm_v6_rl import VGMv6RL

app = Flask(__name__)
engine = VGMv6RL()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM REINFORCEMENT QUANT ENGINE V6",
        "type": "RL trading system",
        "features": [
            "policy learning",
            "reward-based adaptation",
            "VGM + NN synergy",
            "self-adjusting weights"
        ]
    })


@app.route("/step", methods=["POST"])
def step():
    d = request.get_json()

    state_input = {
        "vgm": (
            float(d.get("W", 0.5)),
            float(d.get("vol", 0.2)),
            float(d.get("tail", 0.2))
        ),
        "x": d.get("x", [0.1, 0.2, 0.3]),
        "market_return": float(d.get("market_return", 0.01))
    }

    result = engine.step(state_input)

    global state
    state = result

    return jsonify(result)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM RL SYSTEM V6 STARTED")
    app.run(port=8000)