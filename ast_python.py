import pandas as pd
import numpy as np

def sma(series, n):
    return series.rolling(int(n)).mean()

def rsi(series, n):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    rs = up.ewm(alpha=1/n).mean() / (down.ewm(alpha=1/n).mean() + 1e-9)
    return 100 - (100 / (1 + rs))

def cross_above(a, b):
    return (a.shift(1) <= b.shift(1)) & (a > b)

def value_to_code(node):
    t = node["type"]
    if t == "name":
        return f"df['{node['value']}']"
    if t == "number":
        return str(node["value"])
    if t == "indicator":
        args = [value_to_code(a) for a in node["args"]]
        return f"{node['name']}({', '.join(args)})"
    if t == "shift":
        return f"df['{node['base']}'].shift({node['n']})"
    if t == "cross":
        return f"cross_above({value_to_code(node['left'])}, {value_to_code(node['right'])})"

def expr_to_code(node):
    if node is None:
        return "False"
    if node["type"] == "cmp":
        return f"({value_to_code(node['left'])} {node['op']} {value_to_code(node['right'])})"
    if node["type"] == "and":
        return f"({expr_to_code(node['left'])}) & ({expr_to_code(node['right'])})"
    if node["type"] == "or":
        return f"({expr_to_code(node['left'])}) | ({expr_to_code(node['right'])})"
    if node["type"] == "cross":
        return value_to_code(node)

def generate_signal_function(ast):
    entry = expr_to_code(ast["entry"])
    exit_ = expr_to_code(ast["exit"])

    def signal_fn(df):
        return pd.DataFrame({
            "entry": eval(entry),
            "exit": eval(exit_)
        }, index=df.index)

    return signal_fn
