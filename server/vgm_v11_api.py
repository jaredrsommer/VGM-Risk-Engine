from flask import Flask, request, jsonify
from core.vgm_v11_fund import VGMv11QuantFund

app = Flask(__name__)
engine = VGMv11QuantFund()

state = {}

@app.route("/")
def home():
    return jsonify({
        "system": "VGM QUANT FUND PLATFORM V11",
        "type": "distributed multi-worker quant system",
        "features": [
            "streaming ingestion layer",
            "distributed model workers",
            "ensemble decision engine",
            "risk engine (VaR + DD)",
            "execution abstraction",
            "online learning loop"
        ],
        "endpoints": ["/trade", "/risk", "/state"]
    })


@app.route("/trade", methods=["POST"])
def trade():
    d = request.get_json()
    price = float(d.get("price", 0.0))

    result = engine.step(price)

    global state
    state = result

    return jsonify(result)


@app.route("/risk")
def risk():
    return jsonify(engine.risk())


@app.route("/state")
def get_state():
    return jsonify(state)


if __name__ == "__main__":
    print("🔥 VGM QUANT FUND V11 DISTRIBUTED STARTED")
    app.run(port=8000)