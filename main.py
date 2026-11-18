"""Dip-and-breakout cbBTC bot for make.fun btc-race-24h-20261118-1444.

Long-only, one position at a time, full-size entries. Two entry triggers,
both read only from closes already delivered in batches (no lookahead):

  1. Sharp dip: the close fell at least 140 bps over the last 10 minutes.
     Buys the capitulation, expecting the bounce.
  2. Breakout: the close is at least 20 bps above the highest close of the
     previous 15 minutes. Buys a fresh leg up.

Exits (whole position): +120 bps take-profit, -100 bps stop-loss, or a
time exit after 240 bars when the trade is in profit. No new entries in
the first 60 bars (indicators need history) or in the last 30 minutes of
the window (no time left for a trade to pay its round-trip cost).

All arithmetic is integer, no randomness, no clock, no environment reads:
the bot is fully deterministic and runs twice byte-for-byte identical.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# --- tuned parameters (grid-searched on the frozen dev window) ---
DIP_LOOKBACK = 10        # bars for the sharp-dip trigger
DIP_BPS = 140            # min 10-minute fall to buy the dip, in bps
BREAKOUT_LOOKBACK = 15   # bars for the breakout trigger
BREAKOUT_BPS = 20        # min excess over the 15-bar high, in bps
TAKE_PROFIT_BPS = 120
STOP_LOSS_BPS = 100
MAX_HOLD_BARS = 240
MIN_HISTORY_BARS = 60
NO_ENTRY_AFTER_MS = 84_600_000  # 23.5 h after the first close: last 30 min
MAX_SLIPPAGE_BPS = 150

# price_scale 5, qty_scale 8, quote_scale 6: value(qty, price) =
# qty * price * 10**6 // 10**13, so avg entry price from cost/qty is
# cost * 10**13 // (qty * 10**6).
AVG_PRICE_NUM = 10 ** (8 + 5)
AVG_PRICE_DEN = 10 ** 6


class Bot:
    def __init__(self):
        self.closes = []          # closes seen so far, ints at price_scale 5
        self.entry_seq = None     # seq of the batch where the position appeared
        self.first_close_ms = None

    def on_hello(self, state):
        self.first_close_ms = state.hello.get("first_close_ms")

    def on_batch(self, state, batch):
        if state.warming_up:
            return []
        bars = [b for b in batch.get("bars", []) if b.get("symbol") == SYMBOL]
        if not bars:
            return []  # gap minute: no bar, no decision
        close = int(bars[0]["c"])
        self.closes.append(close)

        holding = state.positions.get(SYMBOL)
        if holding is None or holding.qty <= 0:
            self.entry_seq = None
            return self._maybe_buy(state, batch)
        if self.entry_seq is None:
            self.entry_seq = state.seq
        return self._maybe_sell(state, holding, close)

    def _late_window(self, state, batch):
        if self.first_close_ms is not None:
            return int(batch.get("t", 0)) - int(self.first_close_ms) >= NO_ENTRY_AFTER_MS
        return state.seq - state.warmup_bars >= 1410

    def _maybe_buy(self, state, batch):
        if len(self.closes) < MIN_HISTORY_BARS + 1:
            return []
        if self._late_window(state, batch):
            return []
        closes = self.closes
        now = closes[-1]
        # Trigger 1: sharp 10-minute dip.
        ref = closes[-1 - DIP_LOOKBACK]
        dip = now * 10_000 < ref * (10_000 - DIP_BPS)
        # Trigger 2: breakout over the previous 15 closes.
        hi = max(closes[-1 - BREAKOUT_LOOKBACK:-1])
        breakout = now * 10_000 > hi * (10_000 + BREAKOUT_BPS)
        if not (dip or breakout):
            return []
        notional = state.cash
        if notional < 1_000_000:  # min notional: 1 USDC
            return []
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": notional,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]

    def _maybe_sell(self, state, holding, close):
        # Average entry price (price-scale ints) from the position's cost.
        avg_px = holding.cost * AVG_PRICE_NUM // (holding.qty * AVG_PRICE_DEN)
        if avg_px <= 0:
            return []
        pnl_bps = (close - avg_px) * 10_000 // avg_px
        hold = state.seq - self.entry_seq if self.entry_seq is not None else 0
        sell = (
            pnl_bps >= TAKE_PROFIT_BPS
            or pnl_bps <= -STOP_LOSS_BPS
            or (hold >= MAX_HOLD_BARS and pnl_bps > 0)
        )
        if not sell:
            return []
        return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]


def main():
    bot = Bot()
    makefun_bars.run(bot.on_batch, on_hello=bot.on_hello)


if __name__ == "__main__":
    main()
