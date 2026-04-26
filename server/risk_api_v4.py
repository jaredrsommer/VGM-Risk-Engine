from flask import Flask, request, jsonify
from core.vgm_v4 import VGMv4

app = Flask(__name__)
engine = VGMv4()

state = {
    "portfolio_risk": 0.5,
    "action": "WAIT",
    "allocation": 0.0
}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM HEDGE FUND V4",
        "capabilities": [
            "portfolio risk control",
            "memory learning",
            "execution ready",
            "governor system"
        ]
    })


@app.route("/risk", methods=["GET"])
def risk():
    return jsonify(state)


@app.route("/update", methods=["POST"])
def update():
    global state
    d = request.get_json()

    W = float(d.get("W", 0.5))
    vol = float(d.get("vol", 0.2))
    corr = float(d.get("corr", 0.1))
    confidence = float(d.get("confidence", 0.5))

    risk = engine.score(W, vol, corr, confidence)
    allocation = engine.position_size(risk, confidence)
    action = engine.governor(risk)

    state.update({
        "portfolio_risk": risk,
        "allocation": allocation,
        "action": action
    })

    return jsonify(state)


@app.route("/feedback", methods=["POST"])
def feedback():
    pnl = float(request.json.get("pnl", 0))
    engine.update_memory(pnl)

    return jsonify({
        "status": "learning updated",
        "pnl": pnl,
        "memory": engine.memory
    })


if __name__ == "__main__":
    print("🔥 VGM HEDGE FUND V4 STARTED")
    app.run(port=8000)