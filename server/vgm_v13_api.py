from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="VGM v13 Institutional Engine", version="13.0")


# =========================
# INPUT SCHEMA
# =========================
class Input(BaseModel):
    features: list[float]
    returns: list[float]


# =========================
# VGM CORE (physics risk model)
# =========================
def vgm(x):
    x = np.array(x, dtype=float)
    vol = np.std(x)
    trend = x[-1] - x[0]

    risk = vol - 0.5 * trend
    return float(np.tanh(-risk))


# =========================
# NN (statistical heuristic learner)
# =========================
def nn(x):
    x = np.array(x, dtype=float)

    mean = np.mean(x)
    std = np.std(x) + 1e-9

    signal = mean / std
    return float(np.tanh(signal))


# =========================
# REGIME DETECTOR
# =========================
def regime(x):
    v = np.std(x)

    if v > 1.5:
        return "CRASH"
    elif v > 0.8:
        return "HIGH_VOL"
    elif v > 0.3:
        return "NORMAL"
    return "LOW_VOL"


# =========================
# OPTIMIZER SWITCH (dynamic)
# =========================
def optimizer_selector(risk, regime_type):
    if regime_type == "CRASH":
        return "RISK_PARITY"
    if risk > 0.6:
        return "MIN_VARIANCE"
    return "MEAN_VARIANCE"


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "status": "VGM v13 ACTIVE",
        "modules": [
            "VGM physics engine",
            "NN signal layer",
            "dynamic optimizer",
            "regime detector",
            "crash shield"
        ]
    }


@app.get("/health")
def health():
    return {"ok": True}


# =========================
# MAIN ENGINE
# =========================
@app.post("/predict")
def predict(data: Input):

    x = np.array(data.features, dtype=float)
    r = np.array(data.returns, dtype=float)

    if len(x) < 3 or len(r) < 3:
        raise HTTPException(400, "insufficient data")

    # -------------------------
    # CORE SIGNALS
    # -------------------------
    v = vgm(x)
    n = nn(x)

    # synergy confidence
    confidence = 0.7 * v + 0.3 * n

    # risk estimate
    risk = float(np.std(r))

    # regime
    reg = regime(r)

    # optimizer choice
    opt = optimizer_selector(risk, reg)

    # -------------------------
    # DECISION ENGINE
    # -------------------------
    score = confidence - risk

    if reg == "CRASH":
        action = "BLOCK"
    elif score > 0.25:
        action = "BUY"
    elif score < -0.25:
        action = "SELL"
    else:
        action = "HOLD"

    # -------------------------
    # OUTPUT
    # -------------------------
    return {
        "action": action,
        "score": float(score),
        "confidence": float(confidence),
        "risk": float(risk),
        "regime": reg,
        "optimizer": opt
    }