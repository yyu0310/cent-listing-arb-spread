# cent-listing-arb-spread

[English](README.md) | [繁體中文](README.zh-TW.md) | 简体中文

上币当天，$CENT 在 MEXC 的价格最高到 Gate 的 3.09 倍。这个 repo 抓下两所的每一笔成交，画成并排的 K 线图。

在线图表：https://yyu0310.github.io/cent-listing-arb-spread/

给 AI Coding Agent 的提示词：

> Clone https://github.com/yyu0310/cent-listing-arb-spread ，先读 AGENTS.md，再跑 fetch_trades.py 和 build_chart.py 重建 index.html。

![$CENT 上币当天 MEXC 与 Gate 的 K 线叠图](docs/screenshot.png)

## 发生了什么

Incentiv 的代币 $CENT，在 UTC+8 时区 2026-10-12 17:00 同时在 MEXC 和 Gate 开放现货交易。以下数字涵盖 17:00 到 23:00。

| | MEXC | Gate |
|---|---|---|
| 成交笔数 | 10,133 | 32,652 |
| 成交额 | 198,343 USDT | 783,147 USDT |
| 第一笔成交 | 0.0029 | 0.0029 |
| 前 10 分钟最高 | 0.0072 | 0.0043 |
| 最低 | 0.0029 | 0.002034 |
| 22:59 价格 | 0.004105 | 0.003899 |

- **价差最大时**：17:09 MEXC 收在 Gate 的 3.09 倍。
- **价差 5% 以内**：20:27 之后两所价格都在 5% 以内。
- **MEXC 开盘第一秒**：10 笔成交时间戳相同，合计 5,555 USDT。

## 两所的充值链

- Gate 的充值页收的是以太坊上的 ERC-20 版 $CENT
- MEXC 的充值页收的是 Incentiv 主网上的原生 $CENT
- 两条链的地址都是 0x 开头，币要在两条链之间移动得经过跨链桥
- 两所的提币预计 2026-10-13 左右开放

## 为什么 K 线用逐笔成交自己算

MEXC 自己的第一根 1 分 K 开盘价写 0.000725，但成交记录里没有这个价格，成交最低是 0.0029。这张图的每一根 K 线都用成交记录算，开盘价就是第一个真的有人买到的价格。

## 图表怎么用

| 控制 | 作用 |
|---|---|
| 1 分／5 分／15 分 | 切换 K 线周期 |
| MEXC／Gate | 显示或隐藏某一所 |
| 鼠标移到图上 | 看同一时间两所的开高低收和成交额 |
| EN／繁中／简中 | 切换语言，默认跟着浏览器语言 |

每一所一个颜色。实心代表收涨，空心代表收跌。

## 自己重跑

每一步都可以交给 AI Agent 做。不需要账号或 API key，用的是两所的公开 API。

1. Python 3.9 以上，只用标准库
2. `python3 fetch_trades.py data`：约 15 秒把所有成交抓进 `data/`，并用两所的 K 线成交额核对加总
3. `python3 build_chart.py data`：生成 `index.html`
4. 用浏览器打开 `index.html`

先用 `mkdir data` 建好文件夹。要研究别的币，改 `fetch_trades.py` 开头的交易对和时间区间。

## 文件

| 文件 | 用途 |
|---|---|
| `index.html` | 图表本体，内含 17:00 到 23:00 的数据；GitHub Pages 用它当首页 |
| `fetch_trades.py` | 从 MEXC 和 Gate 抓成交，并跑成交额核对 |
| `build_chart.py` | 把成交聚合成 1 分 K，填进模板 |
| `chart_template.html` | 页面版面、三语文字和图表逻辑 |

## 限制

- MEXC 的成交时间只到秒，也没有成交编号，同一秒内的先后顺序无法确定，1 分 K 的开收盘可能有些微误差。Gate 的成交按流水编号排序。
- MEXC 同一秒超过 1,000 笔成交时，API 只会给 1,000 笔。发生时 `fetch_trades.py` 的成交额核对会报对不上。
- 公开的成交历史不一定会一直保留。交易所删掉旧数据的话，`index.html` 里的快照还在。
- 本 repo 只记录这次上币，交易请自行判断。

## 授权

MIT。市场数据来自 MEXC 与 Gate 的公开 API。
