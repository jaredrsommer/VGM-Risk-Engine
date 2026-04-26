from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

app = FastAPI(title="VGM Portfolio Optimizer", version="1.0")


# =========================
# INPUT VALIDATION
# =========================
class OptimizeRequest(BaseModel):
    returns: list[float]


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "service": "VGM OPTIMIZER",
        "status": "LIVE",
        "endpoints": ["/optimize"],
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {"ok": True}


# =========================
# OPTIMIZER
# =========================
@app.post("/optimize")
def optimize(data: OptimizeRequest):

    returns = np.array(data.returns, dtype=float)

    if len(returns) < 2:
        raise HTTPException(
            status_code=400,
            detail="returns must contain at least 2 values"
        )

    # remove NaN / inf safety
    returns = np.nan_to_num(returns)

    # =========================
    # VGM-style weighting logic
    # =========================
    abs_sum = np.sum(np.abs(returns)) + 1e-9

    weights = returns / abs_sum

    # normalize weights to sum = 1 (institutional standard)
    weights = weights / (np.sum(np.abs(weights)) + 1e-9)

    # =========================
    # Sharpe proxy (risk-adjusted return)
    # =========================
    mean_r = np.mean(returns)
    std_r = np.std(returns) + 1e-9

    sharpe_proxy = mean_r / std_r

    # =========================
    # stability clamp (avoid extreme outputs)
    # =========================
    sharpe_proxy = float(np.clip(sharpe_proxy, -5, 5))

    return {
        "weights": weights.tolist(),
        "sharpe_proxy": sharpe_proxy,
        "risk": float(std_r),
        "mean_return": float(mean_r)
    }