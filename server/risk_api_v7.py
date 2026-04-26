from flask import Flask, request, jsonify
from core.vgm_v7_drl import VGMv7DeepRL

app = Flask(__name__)
agent = VGMv7DeepRL()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM DEEP RL TRADING SYSTEM V7",
        "type": "Actor-Critic RL prototype",
        "features": [
            "policy network",
            "value function",
            "TD learning",
            "market feedback loop"
        ]
    })


@app.route("/step", methods=["POST"])
def step():
    d = request.get_json()

    state_input = d.get("state", [0.1]*10)
    next_state = d.get("next_state", [0.1]*10)
    market_return = float(d.get("market_return", 0.0))

    result = agent.step(state_input, next_state, market_return)

    global state
    state = result

    return jsonify(result)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM DEEP RL V7 STARTED")
    app.run(port=8000)