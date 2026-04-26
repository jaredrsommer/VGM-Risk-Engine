from fastapi import FastAPI
import numpy as np

app = FastAPI()

@app.post("/risk")
def risk(data: dict):

    pnl = np.array(data["pnl"])

    var = np.percentile(pnl, 5)
    cvar = np.mean(pnl[pnl <= var])

    drawdown = np.min(np.cumsum(pnl))

    return {
        "VaR": float(var),
        "CVaR": float(cvar),
        "drawdown": float(drawdown),
        "risk_level": "HIGH" if drawdown < -10 else "OK"
    }