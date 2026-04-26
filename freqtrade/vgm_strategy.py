"""
VGM Risk Strategy for Freqtrade
================================
Uses the VGM Risk Engine API as a pre-trade safety filter.

Setup:
  1. Start VGM server: python server/vgm_v13_api.py
  2. Copy this file to your Freqtrade user_data/strategies/ folder
  3. Run: freqtrade trade --strategy VGMStrategy

API must be running at VGM_API_URL before bot starts.
"""

import requests
import numpy as np
import pandas as pd
from functools import reduce
from freqtrade.strategy import IStrategy, DecimalParameter
from pandas import DataFrame


VGM_API_URL = "http://127.0.0.1:8010/predict"
VGM_TIMEOUT = 1.0      # seconds — fail fast, don't block
VGM_MAX_RISK = 0.05    # reject trades with risk score above this
VGM_MIN_CONF = 0.55    # reject trades below this confidence


class VGMStrategy(IStrategy):
    """
    Freqtrade strategy with VGM Risk Firewall integration.

    The VGM API acts as a gate: standard Freqtrade signals generate
    candidates, but every trade must pass the VGM risk check before
    execution. High-risk market regimes are automatically blocked.
    """

    INTERFACE_VERSION = 3
    timeframe = "5m"

    # Minimal ROI — let VGM risk filter handle exits
    minimal_roi = {"0": 0.02}
    stoploss = -0.03
    trailing_stop = False

    # --- Feature extraction ---

    def _get_features(self, dataframe: DataFrame, length: int = 5) -> list:
        """
        Build a simple feature vector from recent OHLCV data.
        Replace with your own feature engineering as needed.
        """
        recent = dataframe.tail(length)
        features = [
            float(recent["close"].pct_change().mean()),
            float(recent["volume"].pct_change().mean()),
            float(recent["high"].mean() - recent["low"].mean()),  # avg range
            float(recent["close"].std()),                          # volatility
            float(recent["close"].iloc[-1] / recent["close"].iloc[0] - 1),  # momentum
        ]
        return features

    def _get_returns(self, dataframe: DataFrame, length: int = 10) -> list:
        """Recent log returns for the VGM model."""
        returns = dataframe["close"].pct_change().tail(length).dropna().tolist()
        return [float(r) for r in returns]

    # --- VGM API call ---

    def _vgm_check(self, dataframe: DataFrame) -> dict | None:
        """
        Call VGM Risk API. Returns parsed response or None on failure.
        Failures are silent — strategy falls back to blocking the trade.
        """
        try:
            payload = {
                "features": self._get_features(dataframe),
                "returns":  self._get_returns(dataframe),
            }
            resp = requests.post(VGM_API_URL, json=payload, timeout=VGM_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    # --- Signal generation (standard Freqtrade) ---

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Simple EMA crossover — replace with your own indicators
        dataframe["ema_fast"] = dataframe["close"].ewm(span=9).mean()
        dataframe["ema_slow"] = dataframe["close"].ewm(span=21).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            dataframe["ema_fast"] > dataframe["ema_slow"],
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            dataframe["ema_fast"] < dataframe["ema_slow"],
            "exit_long"
        ] = 1
        return dataframe

    # --- VGM gate on trade entry ---

    def confirm_trade_entry(
        self, pair: str, order_type: str, amount: float,
        rate: float, time_in_force: str, current_time,
        entry_tag: str | None, side: str, **kwargs
    ) -> bool:
        """
        VGM Risk Firewall runs here — last gate before order placement.
        Trade is blocked if:
          - API is unreachable
          - risk score > VGM_MAX_RISK
          - confidence < VGM_MIN_CONF
          - action != BUY (for long entries)
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        result = self._vgm_check(dataframe)

        if result is None:
            # API down — block trade (fail safe)
            return False

        action     = result.get("action", "HOLD")
        risk       = result.get("risk", 1.0)
        confidence = result.get("confidence", 0.0)
        regime     = result.get("regime", "UNKNOWN")

        # Log for Freqtrade journal
        self.log(
            f"VGM [{pair}] action={action} risk={risk:.4f} "
            f"conf={confidence:.4f} regime={regime}"
        )

        if action != "BUY":
            return False
        if risk > VGM_MAX_RISK:
            return False
        if confidence < VGM_MIN_CONF:
            return False

        return True
