from flask import Flask, request, jsonify
from core.vgm_v8_ppo import VGMv8PPO

app = Flask(__name__)
agent = VGMv8PPO()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM QUANT RL PRODUCTION V8",
        "type": "PPO-style risk-constrained trading system",
        "features": [
            "risk governor layer",
            "policy + value networks",
            "PnL-based reward",
            "drawdown protection",
            "execution-ready architecture"
        ],
        "endpoints": ["/step", "/state"]
    })


@app.route("/step", methods=["POST"])
def step():
    d = request.get_json()

    state_input = d.get("state", [0.1]*12)
    next_state = d.get("next_state", [0.1]*12)

    pnl = float(d.get("pnl", 0))
    vol = float(d.get("vol", 0.2))
    dd = float(d.get("drawdown", 0.1))

    result = agent.step(state_input, next_state, pnl, vol, dd)

    global state
    state = result

    return jsonify(result)


@app.route("/state", methods=["GET"])
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM PRODUCTION RL V8 STARTED")
    app.run(port=8000)