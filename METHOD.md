# Method

## Market and costs

One asset, cbBTC/USDC, 1-minute bars. Orders decided on a bar's close fill
at the next bar's open. Every fill pays 4 bps fee + 2 bps modelled slippage
+ constant-product price impact against that bar's open depth, so a
full-size round trip costs roughly 26 bps. A trade therefore has to catch a
move clearly larger than that; 1-minute noise (about 7 bps standard
deviation on the dev window) is far too small to trade.

## Why this shape

The dev window fell 2.8% over 24 hours with two tradable events: a sharp
capitulation early on (about −240 bps in 30 minutes) followed by a slow
recovery, and a 15-bar breakout into the day's second rally. Plain
mean-reversion (RSI/Bollinger dip-buying) loses on this window because dips
kept dipping, and fast EMA-cross trend following loses far more (about
−$140 in the local simulator) by whipsawing. The two triggers below are
the selective versions that survive: they fire rarely and only on moves
large relative to the 26 bps round-trip cost.

## Rules

- Entry, full size (100% of cash), when either trigger fires and no
  position is open:
  - sharp dip: close down ≥ 120 bps over the last 10 closes;
  - breakout: close ≥ 20 bps above the highest close of the previous
    15 closes.
- Exit, whole position, when any of these holds at a bar's close:
  - take-profit +120 bps over the position's average entry price
    (cost basis, fees included);
  - stop-loss −100 bps;
  - time exit: held ≥ 240 bars and in profit.
- No entries before 60 bars of history, and none in the last 30 minutes
  of the window (measured from bar time, so it holds on any 24 h window).
- `max_slippage_bps` 150 on every order: far above any 1-minute move in
  the dev data, so fills are effectively never rejected for slippage,
  while still bounding a freak gap.

## Tuning and robustness

Parameters were grid-searched with a local simulator that replicates the
harness fill math exactly (integer arithmetic, fee/slippage/impact at the
next bar's open, flatten at the last close). The chosen point is not a
sharp peak: neighbouring settings (dip 120–150 bps, breakout 20–30 bps,
hold 120–240 bars) all score about +$10 on the dev window, and the two
round trips it takes are two different events (dip trade, breakout trade),
not one lucky trade. Max drawdown on dev is 1.51%, far inside the 25%
guardrail.

## Determinism

Integer arithmetic only, no randomness, no wall clock, no environment
reads. The bot's state is the closes it has been sent and its position;
two runs on the same data produce byte-identical replies.
