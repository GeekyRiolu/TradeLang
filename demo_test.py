import pandas as pd
import numpy as np
from nl_to_dsl import nl_to_dsl
from dsl_parser import parse_dsl
from ast_to_python import generate_signal_function
from backtest import simple_backtest

dates = pd.date_range("2023-01-01", periods=60)
df = pd.DataFrame({
    "close": np.linspace(100, 130, 60),
    "high": np.linspace(101, 131, 60),
    "low": np.linspace(99, 129, 60),
    "volume": np.random.randint(800000, 1500000, 60)
}, index=dates)

nl = "Buy when the close price is above the 20-day moving average and volume is above 1M. Exit when RSI(14) is below 30."

dsl = nl_to_dsl(nl)
ast = parse_dsl(dsl)
signal_fn = generate_signal_function(ast)
signals = signal_fn(df)

result = simple_backtest(df, signals)
print(dsl)
print(result)
