import numpy as np
from collections import deque

class VGMv11QuantFund:

    def __init__(self):

        # STREAM STATE (like Redis stream buffer)
        self.stream = deque(maxlen=1000)

        # model workers (distributed concept)
        self.vgm_worker = self.VGMWorker()
        self.rl_worker  = self.RLWorker()
        self.nn_worker  = self.NNWorker()

        # risk engine
        self.max_dd = 0.25

        # portfolio state
        self.pnl = []

    # =========================
    # WORKER MODELS (SIMULATED DISTRIBUTED)
    # =========================
    class VGMWorker:
        def predict(self, x):
            return np.tanh(np.mean(x))

    class RLWorker:
        def predict(self, x):
            return np.tanh(np.dot(x, np.random.randn(len(x)) * 0.02))

    class NNWorker:
        def predict(self, x):
            return np.tanh(np.sum(x) / (len(x)+1))

    # =========================
    # FEATURE ENGINE
    # =========================
    def features(self):
        x = np.array(self.stream)

        if len(x) < 20:
            return np.zeros(10)

        r = np.diff(x)

        return np.array([
            np.mean(r),
            np.std(r),
            np.min(r),
            np.max(r),
            np.mean(x[-10:]),
            np.mean(x[-50:]),
            np.percentile(r, 5),
            np.percentile(r, 95),
            np.sum(r > 0),
            np.sum(r < 0)
        ])

    # =========================
    # ENSEMBLE DECISION LAYER
    # =========================
    def decision(self, f):

        vgm = self.vgm_worker.predict(f)
        rl  = self.rl_worker.predict(f)
        nn  = self.nn_worker.predict(f)

        score = 0.4*vgm + 0.4*rl + 0.2*nn

        if score < -0.3:
            return "BLOCK", score
        if score < 0.2:
            return "REDUCE", score
        return "ALLOW", score

    # =========================
    # RISK ENGINE (INSTITUTIONAL)
    # =========================
    def risk(self):

        if len(self.pnl) < 30:
            return {"dd": 0.0, "var": 0.0}

        pnl = np.array(self.pnl)

        dd = np.min(np.cumsum(pnl))
        var = np.percentile(pnl, 5)

        return {
            "drawdown": float(dd),
            "VaR": float(var)
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
    # ONLINE LEARNING LOOP
    # =========================
    def learn(self, pnl):
        self.pnl.append(pnl)

    # =========================
    # MAIN PIPELINE STEP
    # =========================
    def step(self, price):

        self.stream.append(price)

        f = self.features()

        action, score = self.decision(f)

        price_change = 0.0
        if len(self.stream) > 2:
            price_change = self.stream[-1] - self.stream[-2]

        pnl = self.execute(action, score, price_change)

        self.learn(pnl)

        return {
            "action": action,
            "score": float(score),
            "pnl": float(pnl),
            "risk": self.risk()
        }