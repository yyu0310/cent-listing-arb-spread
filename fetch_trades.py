"""Fetch every $CENT spot trade on MEXC and Gate for the listing-day window.

Writes cent_mexc_trades.csv and cent_gate_trades.csv, then checks that the summed
trade value matches each exchange's own 1-minute kline volume.

Usage: python3 fetch_trades.py [output_dir]
"""
import csv, json, sys, urllib.request, datetime as dt
from pathlib import Path

TZ = dt.timezone(dt.timedelta(hours=8))  # listing was announced in UTC+8
START = int(dt.datetime(2026, 10, 12, 17, 0, tzinfo=TZ).timestamp())
END = int(dt.datetime(2026, 10, 12, 23, 0, tzinfo=TZ).timestamp())
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def get(url):
    print("GET", url)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req))


def mexc():
    # aggTrades returns the NEWEST 1000 trades in the window, unordered, with
    # second-resolution timestamps, so walk backwards from END.
    rows, e = [], END * 1000
    while e > START * 1000:
        s = max(START * 1000, e - 3600_000)
        r = get(f"https://api.mexc.com/api/v3/aggTrades?symbol=CENTUSDT&startTime={s}&endTime={e}&limit=1000")
        ts = [t["T"] for t in r]
        if len(r) < 1000:
            keep, e = r, s - 1  # whole window fetched
        elif min(ts) == max(ts):
            keep, e = r, min(ts) - 1  # >1000 trades in one second: some are lost, the kline check below will flag it
        else:
            # the oldest second may be cut off; drop it and refetch it whole on the next page
            keep, e = [t for t in r if t["T"] > min(ts)], min(ts) + 999
        rows += [(t["T"] / 1000, t["p"], t["q"], "sell" if t["m"] else "buy") for t in keep]
        print(f"  got {len(r)}, kept {len(keep)}, total {len(rows)}")
    return sorted(rows)  # MEXC has no trade id; order within the same second is unknown


def gate():
    rows, page = {}, 1
    while True:
        r = get(f"https://api.gateio.ws/api/v4/spot/trades?currency_pair=CENT_USDT&from={START}&to={END}&limit=1000&page={page}")
        for t in r:
            rows[t["id"]] = (float(t["create_time_ms"]) / 1000, t["price"], t["amount"], t["side"])
        print(f"  got {len(r)}, total {len(rows)}")
        if len(r) < 1000:
            break
        page += 1
    # Gate trade ids are sequential, so they give the true order even within one millisecond
    return [rows[i] for i in sorted(rows, key=int)]


def kline_usdt(name):
    # 1000 one-minute bars cover ~16 hours; the window here is 6 hours
    if name == "mexc":
        r = get(f"https://api.mexc.com/api/v3/klines?symbol=CENTUSDT&interval=1m&startTime={START * 1000}&endTime={END * 1000}&limit=1000")
        return sum(float(k[7]) for k in r)
    r = get(f"https://api.gateio.ws/api/v4/spot/candlesticks?currency_pair=CENT_USDT&interval=1m&from={START}&to={END}")
    return sum(float(k[1]) for k in r)


for name, fn in (("mexc", mexc), ("gate", gate)):
    rows = fn()
    with open(OUT / f"cent_{name}_trades.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts", "time_utc8", "price", "qty", "side", "usdt"])
        for ts, p, q, side in rows:
            w.writerow([ts, dt.datetime.fromtimestamp(ts, TZ).strftime("%H:%M:%S.%f")[:-3], p, q, side, round(float(p) * float(q), 4)])
    prices = [float(r[1]) for r in rows]
    usdt = sum(float(r[1]) * float(r[2]) for r in rows)
    buy = sum(float(r[1]) * float(r[2]) for r in rows if r[3] == "buy")
    print(f"[{name}] {len(rows)} trades | first {rows[0][1]} | last {rows[-1][1]} | high {max(prices)} low {min(prices)} | {usdt:,.0f} USDT | taker buy {buy / usdt:.0%}")
    k = kline_usdt(name)  # the last kline can include trades after END; under 1% is normal
    ok = abs(usdt - k) / k < 0.01
    print(f"[{name}] check: trades {usdt:,.0f} vs klines {k:,.0f} USDT, diff {(usdt - k) / k:+.2%} {'OK' if ok else 'MISMATCH, trades may be missing'}")
