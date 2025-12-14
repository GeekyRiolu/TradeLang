import pandas as pd
from nl_to_dsl import nl_to_dsl
from dsl_parser import parse_dsl
from ast_to_python import generate_signal_function
from backtest import simple_backtest

def build_sample_data():
    dates = pd.date_range("2023-01-01", periods=60)
    import numpy as np
    np.random.seed(0)
    base = np.linspace(100, 130, len(dates))
    noise = np.random.normal(0, 1.0, len(dates)).cumsum() * 0.1
    close = base + noise
    df = pd.DataFrame(index=dates)
    df['close'] = close
    df['open'] = df['close'].shift(1).fillna(df['close'])
    df['high'] = df[['open','close']].max(axis=1) + 0.5
    df['low']  = df[['open','close']].min(axis=1) - 0.5
    vols = (np.random.randint(800_000, 1_400_000, size=len(dates)))
    df['volume'] = vols
    return df

def run_demo(nl_text):
    print("Natural Language Input:")
    print(nl_text)
    dsl = nl_to_dsl(nl_text)
    print("\nGenerated DSL:")
    print(dsl)
    ast = parse_dsl(dsl)
    import json
    print("\nParsed AST:")
    print(json.dumps(ast, indent=2, default=str))
    df = build_sample_data()
    sig_fn = generate_signal_function(ast)
    signals = sig_fn(df)
    print("\nSample signals head:")
    print(signals.head(10))
    summary, trades_df, equity_df = simple_backtest(df, signals, start_capital=1.0)
    print("\nBacktest Result:")
    for k,v in summary.items():
        print(f"{k}: {v}")
    print("\nTrade Log:")
    if trades_df.empty:
        print("(no trades triggered)")
    else:
        print(trades_df.to_string(index=False))

if __name__ == "__main__":
    example_nl = "Buy when the close price is above the 20-day moving average and volume is above 1M. Exit when RSI(14) is below 30."
    run_demo(example_nl)
