import numpy as np

class VGMv6RL:
    def __init__(self):
        # policy weights (learnable)
        self.w_vgm = 0.6
        self.w_nn  = 0.4

        # learning rate
        self.lr = 0.02

        # memory
        self.memory = []

    # =========================
    # VGM physics/rules model
    # =========================
    def vgm(self, W, vol, tail):
        return W * (1 - vol) * (1 - tail)

    # =========================
    # NN proxy (placeholder)
    # =========================
    def nn(self, x):
        return np.tanh(np.mean(x))

    # =========================
    # POLICY
    # =========================
    def policy(self, state):
        vgm_score = self.vgm(*state["vgm"])
        nn_score  = self.nn(state["x"])

        return (self.w_vgm * vgm_score) + (self.w_nn * nn_score)

    # =========================
    # ACTION SPACE
    # =========================
    def action(self, score):
        if score < 0.35:
            return 0   # BLOCK
        elif score < 0.6:
            return 1   # REDUCE
        return 2       # ALLOW

    # =========================
    # REWARD FUNCTION
    # =========================
    def reward(self, action, market_return):
        if action == 2:
            return market_return
        elif action == 1:
            return market_return * 0.5
        else:
            return -abs(market_return)

    # =========================
    # POLICY UPDATE (RL CORE)
    # =========================
    def update(self, score, action, r):
        # simple policy gradient approximation
        error = r

        self.w_vgm += self.lr * error * score
        self.w_nn  += self.lr * error * (1 - score)

        # normalize
        s = self.w_vgm + self.w_nn
        self.w_vgm /= s
        self.w_nn  /= s

    # =========================
    # ONE STEP
    # =========================
    def step(self, state):
        score = self.policy(state)
        action = self.action(score)

        r = self.reward(action, state["market_return"])
        self.update(score, action, r)

        self.memory.append(r)

        return {
            "score": float(score),
            "action": int(action),
            "reward": float(r),
            "weights": {
                "vgm": float(self.w_vgm),
                "nn": float(self.w_nn)
            }
        }