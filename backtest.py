import pandas as pd
import numpy as np

def simple_backtest(df, signals, start_capital=1.0):
    """
    df: OHLCV DataFrame indexed by date with columns ['open','high','low','close','volume']
    signals: DataFrame with boolean columns 'entry' and 'exit' matched to df.index
    Returns summary dict and trade log DataFrame
    """
    in_pos = False
    entry_price = None
    entry_date = None
    trades = []
    equity_series = pd.Series(index=df.index, dtype=float)
    capital = float(start_capital)
    equity_series[:] = capital

    for i, idx in enumerate(df.index):
        row = df.loc[idx]
        e = signals.loc[idx, 'entry']
        x = signals.loc[idx, 'exit']
        if not in_pos:
            if e:
                in_pos = True
                entry_date = idx
                entry_price = row['close']
        else:
            if x:
                exit_date = idx
                exit_price = row['close']
                ret = exit_price / entry_price - 1.0
                capital = capital * (1.0 + ret)
                trades.append({
                    'entry_date': entry_date,
                    'exit_date': exit_date,
                    'entry_price': float(entry_price),
                    'exit_price': float(exit_price),
                    'pnl': float(exit_price - entry_price),
                    'return_pct': float(ret * 100)
                })
                in_pos = False
                entry_price = None
                entry_date = None
        equity_series.loc[idx] = capital if not in_pos else capital 
    if in_pos:
        last = df.iloc[-1]
        exit_price = last['close']
        exit_date = df.index[-1]
        ret = exit_price / entry_price - 1.0
        capital = capital * (1.0 + ret)
        trades.append({
            'entry_date': entry_date,
            'exit_date': exit_date,
            'entry_price': float(entry_price),
            'exit_price': float(exit_price),
            'pnl': float(exit_price - entry_price),
            'return_pct': float(ret * 100)
        })
        in_pos = False

    total_return = (capital / start_capital - 1.0) * 100
    num_trades = len(trades)
    equity_df = pd.DataFrame({'equity': equity_series})
    equity_df['cummax'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = equity_df['equity'] / equity_df['cummax'] - 1.0
    max_drawdown = equity_df['drawdown'].min() * 100 

    summary = {
        'total_return_pct': float(total_return),
        'max_drawdown_pct': float(max_drawdown),
        'num_trades': num_trades,
        'ending_capital': float(capital)
    }
    trades_df = pd.DataFrame(trades)
    return summary, trades_df, equity_df

if __name__ == "__main__":
    import pandas as pd
    dates = pd.date_range("2023-01-01", periods=10)
    df = pd.DataFrame({
        'open': [100,101,102,103,104,105,106,107,108,109],
        'high': [101,102,103,104,105,106,107,108,109,110],
        'low': [99,100,101,102,103,104,105,106,107,108],
        'close': [100,102,101,103,105,104,106,108,107,109],
        'volume':[900000,1200000,1300000,900000,1500000,1000000,1200000,800000,1000000,1400000]
    }, index=dates)
    signals = pd.DataFrame(index=df.index)
    signals['entry'] = [False, True, False, False, False, False, True, False, False, False]
    signals['exit']  = [False, False, False, False, True, False, False, False, True, False]
    print(simple_backtest(df, signals))
