import numpy as np

class VGMLive:
    def __init__(self, vgm_engine):
        self.vgm = vgm_engine

    def compute(self, prices):
        if len(prices) < 30:
            return {"action": "WAIT", "W": 0.5}

        x = np.array(prices[-30:])
        r = np.diff(x)

        vol = np.std(r)
        tail = abs(np.percentile(r, 5))
        mom = x[-1] - x[0]
        grad = r[-1]
        ent = np.std(r) / (np.mean(np.abs(r)) + 1e-8)

        W = self.vgm.score(vol, tail, mom, grad, ent)

        if W < 0.40:
            action = "BLOCK"
        elif W < 0.60:
            action = "REDUCE"
        else:
            action = "ALLOW"

        return {
            "W": float(W),
            "action": action,
            "risk": 1 - W
        }