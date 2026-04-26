import numpy as np

class VGMv5QuantEngine:
    def __init__(self):
        # adaptive weights (learning layer)
        self.w_vgm = 0.7
        self.w_nn  = 0.3

        # memory
        self.memory = {
            "wins": 0,
            "losses": 0,
            "drawdown": []
        }

    # =========================
    # MARKET RISK MODEL
    # =========================
    def vgm_score(self, W, vol, tail):
        return W * (1 - vol) * (1 - tail)

    # =========================
    # NN SCORE (placeholder hook)
    # =========================
    def nn_score(self, x):
        # later replaced with ONNX / PyTorch inference
        return np.tanh(np.mean(x))

    # =========================
    # COMBINED SIGNAL
    # =========================
    def combined(self, vgm, nn):
        return (self.w_vgm * vgm) + (self.w_nn * nn)

    # =========================
    # PORTFOLIO RISK
    # =========================
    def portfolio_risk(self, corr_matrix):
        return float(np.mean(corr_matrix))

    # =========================
    # EXECUTION DECISION
    # =========================
    def decision(self, score):
        if score < 0.35:
            return "BLOCK"
        elif score < 0.6:
            return "REDUCE"
        return "ALLOW"

    # =========================
    # EXECUTION SIMULATOR
    # =========================
    def simulate_pnl(self, decision, market_move):
        if decision == "ALLOW":
            return market_move
        elif decision == "REDUCE":
            return market_move * 0.5
        return -abs(market_move)

    # =========================
    # LEARNING UPDATE (KEY PART)
    # =========================
    def update_weights(self, pnl):
        if pnl > 0:
            self.w_vgm *= 1.01
            self.w_nn  *= 0.99
            self.memory["wins"] += 1
        else:
            self.w_vgm *= 0.99
            self.w_nn  *= 1.01
            self.memory["losses"] += 1

        # normalize
        s = self.w_vgm + self.w_nn
        self.w_vgm /= s
        self.w_nn  /= s

    # =========================
    # MAIN PIPELINE
    # =========================
    def step(self, W, vol, tail, x, market_move, corr_matrix):
        vgm = self.vgm_score(W, vol, tail)
        nn  = self.nn_score(x)

        score = self.combined(vgm, nn)
        decision = self.decision(score)

        pnl = self.simulate_pnl(decision, market_move)
        self.update_weights(pnl)

        risk = self.portfolio_risk(corr_matrix)

        return {
            "vgm": float(vgm),
            "nn": float(nn),
            "score": float(score),
            "decision": decision,
            "pnl": float(pnl),
            "portfolio_risk": risk,
            "weights": {
                "vgm": float(self.w_vgm),
                "nn": float(self.w_nn)
            }
        }