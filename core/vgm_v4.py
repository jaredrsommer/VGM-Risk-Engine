import numpy as np

class VGMv4:
    def __init__(self):
        self.memory = {
            "wins": 0,
            "losses": 0,
            "crashes": 0
        }

    # ------------------------
    # CORE RISK SCORE
    # ------------------------
    def score(self, W, vol, corr, confidence):
        risk_pressure = vol * (1 + corr)
        adjusted = W * confidence - risk_pressure

        return 1 / (1 + np.exp(-adjusted))

    # ------------------------
    # PORTFOLIO ALLOCATION
    # ------------------------
    def position_size(self, risk, confidence):
        base = confidence * (1 - risk)
        return float(np.clip(base, 0, 1))

    # ------------------------
    # RISK GOVERNOR
    # ------------------------
    def governor(self, portfolio_risk):
        if portfolio_risk > 0.75:
            return "HARD_BLOCK"
        if portfolio_risk > 0.55:
            return "REDUCE_ALL"
        return "OK"

    # ------------------------
    # MEMORY UPDATE
    # ------------------------
    def update_memory(self, pnl):
        if pnl < 0:
            self.memory["losses"] += 1
        else:
            self.memory["wins"] += 1