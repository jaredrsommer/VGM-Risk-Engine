import numpy as np

class VGMCore:
    def score(self, vol, tail, mom, grad, ent):
        W = (
            0.3 * (1 - vol) +
            0.25 * (1 - tail) +
            0.2 * np.tanh(mom) -
            0.15 * ent +
            0.1 * (1 - abs(grad))
        )
        return 1 / (1 + np.exp(-W))