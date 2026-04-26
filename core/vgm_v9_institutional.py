import numpy as np

class VGMv9Institutional:

    def __init__(self):
        # ensemble policies
        self.w_rl = 0.6
        self.w_vgm = 0.3
        self.w_nn = 0.1

        # risk state
        self.max_leverage = 1.0
        self.drawdown_limit = 0.25

        # memory
        self.pnl_history = []

    # =========================
    # VGM FEATURE MODEL
    # =========================
    def vgm(self, W, vol, tail):
        return W * (1 - vol) * (1 - tail)

    # =========================
    # NN SIGNAL (placeholder)
    # =========================
    def nn(self, x):
        return np.tanh(np.mean(x))

    # =========================
    # RL POLICY (simulated PPO output)
    # =========================
    def rl_policy(self, state):
        return np.tanh(np.dot(state[:10], np.random.randn(10) * 0.05))

    # =========================
    # ENSEMBLE DECISION
    # =========================
    def decision_score(self, state):
        vgm_score = self.vgm(*state["vgm"])
        nn_score = self.nn(state["x"])
        rl_score = self.rl_policy(state["x"])

        return (
            self.w_vgm * vgm_score +
            self.w_nn * nn_score +
            self.w_rl * rl_score
        )

    # =========================
    # RISK ENGINE (INSTITUTIONAL)
    # =========================
    def risk_engine(self, score, vol, drawdown):
        leverage = self.max_leverage

        if drawdown > self.drawdown_limit:
            leverage = 0.0
        elif vol > 0.6:
            leverage *= 0.5

        if score < 0.35:
            return "BLOCK", leverage
        elif score < 0.6:
            return "REDUCE", leverage * 0.5
        return "ALLOW", leverage

    # =========================
    # PORTFOLIO OPTIMIZER
    # =========================
    def position_size(self, confidence, leverage):
        return float(np.clip(confidence * leverage, 0, 1))

    # =========================
    # EXECUTION LAYER (SIMULATED)
    # =========================
    def execute(self, action, position_size, market_return):
        if action == "ALLOW":
            return market_return * position_size
        elif action == "REDUCE":
            return market_return * position_size * 0.4
        return -abs(market_return)

    # =========================
    # LEARNING / MEMORY LOOP
    # =========================
    def learn(self, pnl):
        self.pnl_history.append(pnl)

        if len(self.pnl_history) > 50:
            avg = np.mean(self.pnl_history[-50:])

            # adaptive weights
            if avg < 0:
                self.w_rl *= 1.01
                self.w_vgm *= 0.99
            else:
                self.w_vgm *= 1.01
                self.w_rl *= 0.99

            # normalize
            s = self.w_rl + self.w_vgm + self.w_nn
            self.w_rl /= s
            self.w_vgm /= s
            self.w_nn /= s

    # =========================
    # MAIN STEP
    # =========================
    def step(self, state, vol, drawdown, market_return):

        score = self.decision_score(state)
        action, leverage = self.risk_engine(score, vol, drawdown)

        pos = self.position_size(score, leverage)
        pnl = self.execute(action, pos, market_return)

        self.learn(pnl)

        return {
            "score": float(score),
            "action": action,
            "leverage": float(leverage),
            "position_size": float(pos),
            "pnl": float(pnl),
            "weights": {
                "rl": float(self.w_rl),
                "vgm": float(self.w_vgm),
                "nn": float(self.w_nn)
            }
        }