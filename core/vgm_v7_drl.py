import numpy as np

class VGMv7DeepRL:

    def __init__(self):
        # policy network weights (simple proxy NN)
        self.Wp = np.random.randn(10) * 0.1
        self.Wv = np.random.randn(10) * 0.1

        self.lr = 0.01
        self.gamma = 0.95

        self.memory = []

    # =========================
    # STATE ENCODING
    # =========================
    def encode(self, state):
        # state: vector of market features
        return np.array(state[:10])

    # =========================
    # POLICY (Actor)
    # =========================
    def policy(self, s):
        z = np.dot(self.Wp, s)
        prob = 1 / (1 + np.exp(-z))  # sigmoid

        if prob < 0.4:
            return 0   # SELL / BLOCK
        elif prob < 0.6:
            return 1   # HOLD / REDUCE
        return 2       # BUY / ALLOW

    # =========================
    # VALUE (Critic)
    # =========================
    def value(self, s):
        return np.dot(self.Wv, s)

    # =========================
    # REWARD FUNCTION
    # =========================
    def reward(self, action, market_return):
        if action == 2:
            return market_return
        elif action == 1:
            return market_return * 0.3
        else:
            return -abs(market_return)

    # =========================
    # UPDATE (DEEP RL STEP)
    # =========================
    def update(self, s, action, r, next_s):
        v = self.value(s)
        v_next = self.value(next_s)

        td_error = r + self.gamma * v_next - v

        # policy update
        self.Wp += self.lr * td_error * s

        # value update
        self.Wv += self.lr * td_error * s

    # =========================
    # STEP FUNCTION
    # =========================
    def step(self, state, next_state, market_return):

        s = self.encode(state)
        ns = self.encode(next_state)

        action = self.policy(s)
        r = self.reward(action, market_return)

        self.update(s, action, r, ns)

        self.memory.append(r)

        return {
            "action": int(action),
            "reward": float(r),
            "td_error": float(r),
            "weights_norm": float(np.linalg.norm(self.Wp))
        }