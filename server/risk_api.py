from flask import Flask, request, jsonify
from datetime import datetime
import numpy as np

app = Flask(__name__)

# =========================
# GLOBAL STATE (V3)
# =========================
state = {
    "W": 0.5,
    "action": "WAIT",
    "risk": 0.5,
    "crash_flag": False,
    "confidence": 0.5,
    "pnl_impact": 0.0,
    "last_update": None,
    "regime": "NEUTRAL"
}

# =========================
# ROOT
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "VGM FULL TRADING SYSTEM V3 ACTIVE",
        "version": "3.0",
        "features": [
            "VGM + NN synergy",
            "risk aggregation",
            "pnl feedback support",
            "crash detection",
            "execution ready"
        ],
        "endpoints": ["/risk", "/update", "/feedback"]
    })


# =========================
# RISK QUERY
# =========================
@app.route("/risk", methods=["GET"])
def risk():
    return jsonify(state)


# =========================
# LIVE UPDATE (from engine)
# =========================
@app.route("/update", methods=["POST"])
def update():
    global state
    data = request.get_json()

    if not data:
        return {"error": "no data"}, 400

    W = float(data.get("W", state["W"]))
    risk = float(data.get("risk", 1 - W))
    confidence = float(data.get("confidence", 0.5))

    # =========================
    # V3 LOGIC (SYNERGY DECISION)
    # =========================
    crash_flag = (W < 0.32 or risk > 0.78)

    if crash_flag:
        action = "BLOCK"
        regime = "CRASH"
    elif W < 0.55:
        action = "REDUCE"
        regime = "RISK"
    else:
        action = "ALLOW"
        regime = "SAFE"

    state.update({
        "W": W,
        "risk": risk,
        "confidence": confidence,
        "action": action,
        "crash_flag": crash_flag,
        "regime": regime,
        "last_update": datetime.utcnow().isoformat()
    })

    return jsonify({"status": "updated", "state": state})


# =========================
# FEEDBACK LOOP (IMPORTANT)
# =========================
@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Trading results come here:
    pnl > 0  → system learns success
    pnl < 0  → system learns failure
    """
    global state
    data = request.get_json()

    pnl = float(data.get("pnl", 0))

    state["pnl_impact"] = pnl

    # simple adaptive shift (placeholder learning signal)
    if pnl < 0:
        state["confidence"] *= 0.95
    else:
        state["confidence"] *= 1.02
        state["confidence"] = min(state["confidence"], 1.0)

    return jsonify({
        "status": "feedback recorded",
        "pnl": pnl,
        "confidence": state["confidence"]
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    print("🔥 VGM TRADING SYSTEM V3 STARTED")
    app.run(host="127.0.0.1", port=8000, debug=False)