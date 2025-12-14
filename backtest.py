import pandas as pd

def simple_backtest(df, signals, capital=1.0):
    in_pos = False
    entry_price = 0
    trades = []
    equity = capital

    for i in range(len(df)):
        price = df.iloc[i]["close"]
        if not in_pos and signals.iloc[i]["entry"]:
            in_pos = True
            entry_price = price
        elif in_pos and signals.iloc[i]["exit"]:
            ret = price / entry_price - 1
            equity *= (1 + ret)
            trades.append(ret)
            in_pos = False

    total_return = (equity - capital) / capital * 100
    return {
        "total_return_pct": total_return,
        "trades": len(trades)
    }
