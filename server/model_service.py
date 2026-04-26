from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="VGM Hybrid Predictor", version="1.0")


# =========================
# INPUT VALIDATION MODEL
# =========================
class InputData(BaseModel):
    features: list[float]


# =========================
# VGM CORE (physics-like rule)
# =========================
def vgm(x):
    x = np.array(x, dtype=float)
    if len(x) == 0:
        return 0.0
    return float(np.tanh(np.mean(x)))


# =========================
# NN APPROX (simple heuristic)
# =========================
def nn(x):
    x = np.array(x, dtype=float)
    if len(x) == 0:
        return 0.0
    return float(np.tanh(np.sum(x) / (len(x) + 1)))


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {
        "status": "VGM HYBRID MODEL ACTIVE",
        "endpoints": ["/predict"],
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {"ok": True}


# =========================
# PREDICTION ENDPOINT
# =========================
@app.post("/predict")
def predict(data: InputData):

    x = data.features

    if x is None or len(x) < 2:
        raise HTTPException(
            status_code=400,
            detail="features must contain at least 2 values"
        )

    v = vgm(x)
    n = nn(x)

    # hybrid synergy
    score = 0.6 * v + 0.4 * n

    # dynamic thresholds (slightly more realistic than fixed)
    if score < -0.25:
        action = "SELL"
        risk = "HIGH"
    elif score < 0.25:
        action = "HOLD"
        risk = "MEDIUM"
    else:
        action = "BUY"
        risk = "LOW"

    return {
        "score": round(float(score), 5),
        "vgm_component": round(v, 5),
        "nn_component": round(n, 5),
        "action": action,
        "risk_level": risk
    }