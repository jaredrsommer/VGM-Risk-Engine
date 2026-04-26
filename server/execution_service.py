from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="VGM Execution Service", version="1.0")


# =========================
# INPUT VALIDATION
# =========================
class Order(BaseModel):
    symbol: str
    side: str   # BUY / SELL
    size: float


# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {
        "service": "VGM EXECUTION SERVICE",
        "status": "LIVE",
        "endpoints": ["/execute"],
        "version": "1.0"
    }


@app.get("/health")
def health():
    return {"ok": True}


# =========================
# EXECUTION LOGIC
# =========================
@app.post("/execute")
def execute(order: Order):

    # basic safety checks
    if order.size <= 0:
        raise HTTPException(status_code=400, detail="size must be > 0")

    if order.side not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="side must be BUY or SELL")

    return {
        "status": "sent",
        "symbol": order.symbol,
        "side": order.side,
        "size": order.size,
        "execution": "simulated_fill"
    }