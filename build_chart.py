"""Build index.html: MEXC vs Gate candlesticks computed from raw trades.

Candles come from the trade CSVs, not from the exchange kline API, because
MEXC's first kline shows an opening price that never traded.

Usage: python3 build_chart.py [data_dir]   (data_dir holds the CSVs from fetch_trades.py)
"""
import csv, json, sys
from pathlib import Path

DATA = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
HERE = Path(__file__).parent
UTC8 = 8 * 3600  # the chart library renders UTC; shift so the axis reads UTC+8


def candles(name):
    bars = {}
    with open(DATA / f"cent_{name}_trades.csv") as f:
        for r in csv.DictReader(f):
            m = int(float(r["ts"])) // 60 * 60 + UTC8
            p, u = float(r["price"]), float(r["usdt"])
            b = bars.get(m)
            if b is None:
                bars[m] = {"time": m, "open": p, "high": p, "low": p, "close": p, "usdt": u}
            else:
                b["high"], b["low"], b["close"] = max(b["high"], p), min(b["low"], p), p
                b["usdt"] += u
    out = [bars[k] for k in sorted(bars)]
    print(f"[{name}] {len(out)} one-minute candles, {out[0]['open']} -> {out[-1]['close']}")
    return out


data = {n: candles(n) for n in ("mexc", "gate")}

# self-check: candle volume must equal trade volume
for n, bars in data.items():
    with open(DATA / f"cent_{n}_trades.csv") as f:
        total = sum(float(r["usdt"]) for r in csv.DictReader(f))
    assert abs(sum(b["usdt"] for b in bars) - total) < 1, n
print("check OK: candle volume = trade volume")

html = (HERE / "chart_template.html").read_text().replace("__DATA__", json.dumps(data, separators=(",", ":")))
(HERE / "index.html").write_text(html)
print("wrote", HERE / "index.html")
