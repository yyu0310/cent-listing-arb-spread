# AGENTS.md

Two standard-library Python scripts and one HTML template. They download every $CENT spot trade on MEXC and Gate for the 2026-10-12 listing window and render both exchanges as overlaid candlesticks in `index.html`.

## Pipeline

1. `fetch_trades.py <dir>` writes `cent_mexc_trades.csv` and `cent_gate_trades.csv` (columns: `ts` epoch seconds, `time_utc8`, `price`, `qty`, `side`, `usdt`), then compares summed trade value with each exchange's 1-minute kline volume and prints OK or MISMATCH.
2. `build_chart.py <dir>` aggregates trades into 1-minute candles keyed by `ts`, asserts candle volume equals trade volume, and replaces `__DATA__` in `chart_template.html` to write `index.html` next to the script.

## Constants

| Where | Name | Meaning |
|---|---|---|
| fetch_trades.py | `TZ`, `START`, `END` | Window in UTC+8, 2026-10-12 17:00 to 23:00 |
| fetch_trades.py | `CENTUSDT`, `CENT_USDT` in URLs | MEXC and Gate symbols |
| build_chart.py | `UTC8` | Shift applied so the chart axis reads UTC+8 |

## Exchange API quirks

- MEXC `aggTrades`: when a window has more than 1000 trades it returns the newest 1000, unordered, with second-resolution timestamps. `mexc()` walks backwards from `END` and drops the oldest second of a full page so it is refetched whole.
- MEXC first 1-minute kline has an open price that never traded; never use exchange klines for the open.
- Gate `spot/trades`: page through with `from`, `to`, `page`; trade ids are sequential and give the true order.

## Rules

- No API keys, no order placement; public endpoints only.
- Keep `index.html` regenerated from the template; do not edit it by hand.
- Do not commit the CSVs; they are rebuilt by `fetch_trades.py`.
