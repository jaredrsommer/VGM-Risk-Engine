# Elliott Wave 2.0 — ALT Dashboard

A standalone dashboard that tracks **6 core market relationships** to gauge whether
capital is rotating into the altcoin market. Built on TradingView's free embedded
charts — no API key, no backend required.

This module is **independent of the VGM Risk Engine** in the rest of this repo.

## The 6 relationships

**Want pushing higher (alt expansion confirming):**
- BTC / GOLD
- ETH / BTC
- TOTAL3 / BTC
- TOTAL3

**Want pushing lower (alt expansion confirming):**
- BTC Dominance (`BTC.D`)
- USDT Dominance (`USDT.D`)

## Run it

Just open `index.html` in any modern browser:

```bash
# from the repo root
xdg-open alt_dashboard/index.html        # Linux
open      alt_dashboard/index.html        # macOS
start     alt_dashboard\index.html        # Windows
```

Or serve it locally:

```bash
python -m http.server 8765 --directory alt_dashboard
# then visit http://localhost:8765
```

## Symbols used (TradingView)

| Panel          | Symbol                              |
| -------------- | ----------------------------------- |
| BTC / GOLD     | `BITSTAMP:BTCUSD/TVC:GOLD`          |
| ETH / BTC      | `BINANCE:ETHBTC`                    |
| TOTAL3 / BTC   | `CRYPTOCAP:TOTAL3/CRYPTOCAP:BTC`    |
| TOTAL3         | `CRYPTOCAP:TOTAL3`                  |
| BTC Dominance  | `CRYPTOCAP:BTC.D`                   |
| USDT Dominance | `CRYPTOCAP:USDT.D`                  |

Each chart ships with RSI and an exponential MA pre-loaded so you can apply the
Elliott Wave 2.0 framework (cycle positioning, EW counts, Fibonacci, RSI regime,
S/R, MTF context) directly inside the widget.
