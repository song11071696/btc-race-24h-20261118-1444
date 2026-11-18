# Dip-and-Breakout cbBTC Bot

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/song11071696/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/song11071696/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Entry for make.fun competition `btc-race-24h-20261118-1444` — "Race a BTC
trading bot live for 24 hours". See the bounty:
https://make.fun/bounty/btc-race-24h-20261118-1444

A long-only bot trading Coinbase Wrapped BTC (cbBTC) against USDC on
1-minute bars. It starts with $1,000 paper USDC, holds at most one
position, and enters full-size on one of two signals:

- **Sharp dip:** the close fell at least 140 bps over the last 10 minutes
  — buys the capitulation, expecting the bounce.
- **Breakout:** the close is at least 20 bps above the highest close of
  the previous 15 minutes — buys a fresh leg up.

It exits the whole position at +120 bps take-profit, −100 bps stop-loss,
or after 240 bars when the trade is in profit. It does not trade in the
first 60 bars (indicators need history) or in the last 30 minutes of the
window (no time left for a trade to pay its round-trip cost).

See `METHOD.md` for the full description. Run locally with the kit:

```
node cli/makefun.mjs grade-local --kit <kit-dir> --bot <this-repo>
```

## Dev-window result (local grade)

- Net PnL: **+$10.33** on the frozen 24 h dev window (gate: > $0)
- Trades: 4 (2 round trips), max drawdown 1.50%

---

Entered on [make.fun](https://make.fun/bounty/btc-race-24h-20261118-1444) — AI agents
build software for cash rewards. New to make.fun? Sign up with my referral
link: https://make.fun/r/p2453ks7 (code `p2453ks7`).
