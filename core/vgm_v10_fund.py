import numpy as np
from collections import deque

class VGMv10FundInfra:

    def __init__(self):
        # buffers (event-driven system)
        self.price_buffer = deque(maxlen=500)
        self.pnl_buffer = deque(maxlen=200)

        # model weights (ensemble)
        self.w_vgm = 0.4
        self.w_nn  = 0.3
        self.w_rl  = 0.3

        # risk state
        self.max_dd = 0.20
        self.var_limit = 0.05

    # =========================
    # FEATURE ENGINE
    # =========================
    def features(self):
        x = np.array(self.price_buffer)

        if len(x) < 20:
            return np.zeros(10)

        returns = np.diff(x)

        return np.array([
            np.mean(returns),
            np.std(returns),
            np.min(returns),
            np.max(returns),
            np.percentile(returns, 5),
            np.percentile(returns, 95),
            np.sum(returns > 0),
            np.sum(returns < 0),
            np.mean(x[-10:]),
            np.mean(x[-50:])
        ])

    # =========================
    # VGM SIGNAL ENGINE
    # =========================
    def vgm_signal(self, f):
        return np.tanh(np.mean(f[:3]))

    # =========================
    # NN SIGNAL (proxy)
    # =========================
    def nn_signal(self, f):
        return np.tanh(np.dot(f, np.random.randn(len(f)) * 0.05))

    # =========================
    # RL SIGNAL (simulated policy)
    # =========================
    def rl_signal(self, f):
        return np.tanh(np.mean(f) * 1.2)

    # =========================
    # ENSEMBLE DECISION
    # =========================
    def decision(self, f):

        score = (
            self.w_vgm * self.vgm_signal(f) +
            self.w_nn  * self.nn_signal(f) +
            self.w_rl  * self.rl_signal(f)
        )

        if score < -0.3:
            return "BLOCK", score
        elif score < 0.2:
            return "REDUCE", score
        return "ALLOW", score

    # =========================
    # RISK ENGINE (INSTITUTIONAL)
    # =========================
    def risk(self):

        if len(self.pnl_buffer) < 20:
            return 0.0

        pnl = np.array(self.pnl_buffer)

        var = np.percentile(pnl, 5)
        dd = np.min(np.cumsum(pnl))

        return {
            "VaR": float(var),
            "Drawdown": float(dd)
        }

    # =========================
    # EXECUTION ENGINE
    # =========================
    def execute(self, action, score, price_change):

        if action == "BLOCK":
            return 0.0

        if action == "REDUCE":
            return price_change * 0.3 * score

        return price_change * score

    # =========================
    # FEEDBACK LOOP (ONLINE LEARNING)
    # =========================
    def learn(self, pnl):

        self.pnl_buffer.append(pnl)

        avg = np.mean(self.pnl_buffer)

        # adaptive weights (self-correction)
        if avg < 0:
            self.w_rl += 0.01
            self.w_vgm -= 0.005
        else:
            self.w_vgm += 0.01
            self.w_rl -= 0.005

        s = self.w_rl + self.w_vgm + self.w_nn
        self.w_rl /= s
        self.w_vgm /= s
        self.w_nn /= s

    # =========================
    # MAIN TICK
    # =========================
    def step(self, price):

        self.price_buffer.append(price)

        f = self.features()

        action, score = self.decision(f)

        price_change = 0.0
        if len(self.price_buffer) > 2:
            price_change = self.price_buffer[-1] - self.price_buffer[-2]

        pnl = self.execute(action, score, price_change)

        self.learn(pnl)

        risk = self.risk()

        return {
            "action": action,
            "score": float(score),
            "pnl": float(pnl),
            "risk": risk,
            "weights": {
                "vgm": float(self.w_vgm),
                "nn": float(self.w_nn),
                "rl": float(self.w_rl)
            }
        }