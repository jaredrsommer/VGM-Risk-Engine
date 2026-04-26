import numpy as np

class VGMv8PPO:

    def __init__(self):
        # policy + value networks (simple linear proxy)
        self.theta = np.random.randn(12) * 0.01
        self.value_w = np.random.randn(12) * 0.01

        self.lr = 0.005
        self.gamma = 0.95
        self.clip = 0.2

        self.memory = []

    # =========================
    # FEATURE ENCODING
    # =========================
    def encode(self, state):
        return np.array(state[:12])

    # =========================
    # POLICY (soft action)
    # =========================
    def policy(self, s):
        logits = np.dot(self.theta, s)
        prob = 1 / (1 + np.exp(-logits))

        if prob < 0.4:
            return 0   # BLOCK
        elif prob < 0.6:
            return 1   # REDUCE
        return 2       # ALLOW

    # =========================
    # VALUE FUNCTION
    # =========================
    def value(self, s):
        return np.dot(self.value_w, s)

    # =========================
    # RISK GOVERNOR (CRITICAL LAYER)
    # =========================
    def risk_gate(self, vol, drawdown):
        if drawdown > 0.25:
            return "FORCE_BLOCK"
        if vol > 0.6:
            return "DELEVERAGE"
        return "OK"

    # =========================
    # REWARD (PnL + risk penalty)
    # =========================
    def reward(self, action, pnl, vol, dd):
        risk_penalty = vol * 0.5 + dd * 0.7

        if action == 2:
            return pnl - risk_penalty
        elif action == 1:
            return pnl * 0.4 - risk_penalty
        else:
            return -abs(pnl) - risk_penalty

    # =========================
    # PPO-LIKE UPDATE (SIMPLIFIED)
    # =========================
    def update(self, s, action, r, next_s):

        v = self.value(s)
        v_next = self.value(next_s)

        advantage = r + self.gamma * v_next - v

        # policy update (clipped gradient approximation)
        self.theta += self.lr * np.clip(advantage, -self.clip, self.clip) * s

        # value update
        self.value_w += self.lr * advantage * s

    # =========================
    # MAIN STEP
    # =========================
    def step(self, state, next_state, pnl, vol, dd):

        s = self.encode(state)
        ns = self.encode(next_state)

        action = self.policy(s)
        gate = self.risk_gate(vol, dd)

        if gate == "FORCE_BLOCK":
            action = 0

        r = self.reward(action, pnl, vol, dd)

        self.update(s, action, r, ns)

        self.memory.append(r)

        return {
            "action": int(action),
            "reward": float(r),
            "risk_gate": gate,
            "theta_norm": float(np.linalg.norm(self.theta)),
            "value_norm": float(np.linalg.norm(self.value_w))
        }