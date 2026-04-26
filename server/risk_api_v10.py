from flask import Flask, request, jsonify
from core.vgm_v10_fund import VGMv10FundInfra

app = Flask(__name__)
engine = VGMv10FundInfra()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM HEDGE FUND INFRASTRUCTURE V10",
        "status": "event-driven quant trading stack",
        "features": [
            "streaming architecture",
            "ensemble decision engine",
            "risk engine (VaR + DD)",
            "online learning loop",
            "execution abstraction layer"
        ],
        "endpoints": ["/risk", "/update", "/feedback"]
    })


@app.route("/update", methods=["POST"])
def update():

    d = request.get_json()
    price = float(d.get("price", 0.0))

    result = engine.step(price)

    global state
    state = result

    return jsonify(result)


@app.route("/risk")
def risk():
    return jsonify(engine.risk())


@app.route("/feedback", methods=["POST"])
def feedback():
    d = request.get_json()
    pnl = float(d.get("pnl", 0.0))

    engine.learn(pnl)

    return jsonify({"status": "updated", "pnl": pnl})


if __name__ == "__main__":
    print("🔥 VGM HEDGE FUND INFRA V10 STARTED")
    app.run(port=8000)