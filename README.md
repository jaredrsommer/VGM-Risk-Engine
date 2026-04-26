# VGM Risk Engine

**A real-time market risk scoring API for algorithmic trading bots.**

VGM is not a prediction system. It is a **Risk Firewall** — a safety layer that evaluates market conditions before any trade is executed.

---

## What It Does

Submit market features → receive a structured risk assessment:

```json
{
  "action":     "BUY",
  "score":      0.6397,
  "confidence": 0.6603,
  "risk":       0.0205,
  "regime":     "LOW_VOL",
  "optimizer":  "MEAN_VARIANCE"
}
```

**Fields:**
- `action` — BUY / SELL / HOLD
- `score` — signal strength (0–1)
- `confidence` — model certainty (0–1)
- `risk` — estimated position risk (0–1)
- `regime` — market regime classification (LOW_VOL, HIGH_VOL, TRENDING, etc.)
- `optimizer` — active portfolio optimization mode

---

## Quickstart

### Start the server

```bash
python server/vgm_v13_api.py
# Listens on http://127.0.0.1:8010
```

### Test with curl

```bash
curl -X POST http://127.0.0.1:8010/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[1,2,3,4,5],"returns":[0.01,-0.02,0.03]}'
```

### Test with PowerShell

```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8010/predict" `
  -ContentType "application/json" `
  -Body '{"features":[1,2,3,4,5],"returns":[0.01,-0.02,0.03]}'
```

---

## Request Schema

```json
{
  "features": [float, ...],   // OHLCV-derived feature vector
  "returns":  [float, ...]    // recent return series
}
```

---

## Freqtrade Integration

See `freqtrade/vgm_strategy.py` for a ready-to-use strategy that calls the VGM API before placing any order.

```python
from freqtrade.strategy import IStrategy
import requests

class VGMStrategy(IStrategy):
    def confirm_trade_entry(self, pair, order_type, amount, rate, ...):
        payload = {
            "features": self.get_features(pair),
            "returns":  self.get_returns(pair)
        }
        r = requests.post("http://127.0.0.1:8010/predict", json=payload, timeout=1)
        result = r.json()

        if result["action"] == "BUY" and result["risk"] < 0.05:
            return True
        return False
```

---

## Architecture

```
Market Data
    │
    ▼
Feature Engine  ──►  VGM Neural Net  ──►  Risk Firewall
                                               │
                          ┌────────────────────┤
                          ▼                    ▼
                     Action Signal        Risk Score
                    (BUY/SELL/HOLD)     + Regime + Confidence
```

---

## Stack

- Python 3.10 / FastAPI
- PyTorch neural network (ONNX exportable)
- Freqtrade compatible strategy module
- MT5 bridge (`mt5/mt5_risk_bridge.py`)
- Docker support (`docker-compose.yml`)

---

## Beta Testing

Looking for Freqtrade / crypto bot users to test the live risk scoring API.

Contact: kretski1@gmail.com
GitHub: https://github.com/Kretski/VGM-Risk-Engine
