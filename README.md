# cent-listing-arb-spread

English | [繁體中文](README.zh-TW.md) | [简体中文](README.zh-CN.md)

On its listing day, $CENT traded on MEXC at up to 3.09 times Gate's price. This repo rebuilds every trade on both exchanges and charts them side by side.

Live chart: https://yyu0310.github.io/cent-listing-arb-spread/

Prompt for an AI coding agent:

> Clone https://github.com/yyu0310/cent-listing-arb-spread and read AGENTS.md, then run fetch_trades.py and build_chart.py to rebuild index.html.

![MEXC vs Gate candlesticks on the $CENT listing day](docs/screenshot.png)

## What happened

Incentiv's token $CENT opened for spot trading on MEXC and Gate at the same time, 2026-10-12 17:00 UTC+8. Numbers below cover 17:00 to 23:00.

| | MEXC | Gate |
|---|---|---|
| Trades | 10,133 | 32,652 |
| Volume | 198,343 USDT | 783,147 USDT |
| First trade | 0.0029 | 0.0029 |
| High in the first 10 minutes | 0.0072 | 0.0043 |
| Low | 0.0029 | 0.002034 |
| Price at 22:59 | 0.004105 | 0.003899 |

- **Peak gap**: at 17:09 MEXC closed at 3.09 times Gate's price.
- **Gap under 5%**: from 20:27 onward the two prices stayed within 5% of each other.
- **First second on MEXC**: 10 trades with the same timestamp, 5,555 USDT in total.

## Deposit chains

- Gate's deposit page took $CENT as an ERC-20 token on Ethereum
- MEXC's deposit page took $CENT on the native Incentiv chain
- Both chains use 0x addresses; moving coins between them needs a bridge
- Withdrawals on both exchanges were scheduled to open around 2026-10-13

## Why candles are built from raw trades

MEXC's own first 1-minute kline shows an open of 0.000725, a price that does not appear in the trade list: the lowest trade was 0.0029. This chart builds every candle from the trade list, so the open is the first price someone actually paid.

## Using the chart

| Control | What it does |
|---|---|
| 1m / 5m / 15m | Change the candle period |
| MEXC / Gate | Show or hide one exchange |
| Hover | Read open, high, low, close and volume for both exchanges at that time |
| EN / 繁中 / 简中 | Switch language; the default follows your browser |

Each exchange has one color. A filled body means the candle closed up, a hollow body means it closed down.

## Rebuild it yourself

Every step can be done by an AI agent. No account or API key is needed; both exchanges' public APIs are used.

1. Python 3.9 or newer, standard library only
2. `python3 fetch_trades.py data` downloads all trades into `data/` in about 15 seconds and checks the summed trade volume against each exchange's kline volume
3. `python3 build_chart.py data` writes `index.html`
4. Open `index.html` in a browser

Create the `data` folder first with `mkdir data`. To study another token, change the symbols and the time window at the top of `fetch_trades.py`.

## Files

| File | Purpose |
|---|---|
| `index.html` | The chart, with the 17:00 to 23:00 data embedded; served by GitHub Pages |
| `fetch_trades.py` | Downloads trades from MEXC and Gate and runs the volume check |
| `build_chart.py` | Turns trades into 1-minute candles and fills the template |
| `chart_template.html` | Page layout, language strings and chart logic |

## Limitations

- MEXC timestamps are rounded to the second and have no trade id, so the order of trades within one second is unknown. Open and close inside a 1-minute candle may be slightly off. Gate trades are ordered by their sequential id.
- If more than 1,000 MEXC trades fall in a single second, the API returns only 1,000. The volume check in `fetch_trades.py` reports a mismatch when that happens.
- Public trade history might not stay online forever. If the exchanges drop old data, `index.html` keeps the snapshot.
- This repo records one listing. Trade at your own risk.

## License

MIT. Market data comes from the public APIs of MEXC and Gate.
