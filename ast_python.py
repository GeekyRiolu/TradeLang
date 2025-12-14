import textwrap
import pandas as pd
import numpy as np


def sma(series: pd.Series, n: int):
    return series.rolling(int(n)).mean()

def rsi(series: pd.Series, n: int = 14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/n, adjust=False).mean()
    ma_down = down.ewm(alpha=1/n, adjust=False).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))

def cross_above(a: pd.Series, b: pd.Series):
    """Return boolean series when a crosses above b on that row (i.e., prev <= prev and now > now)."""
    prev_a = a.shift(1)
    prev_b = b.shift(1)
    return (prev_a <= prev_b) & (a > b)

def value_to_code(node):
    t = node.get('type')
    if t == 'name':
        name = node['value']
        if name in ('open','high','low','close','volume'):
            return f"df['{name}']"
        return f"df['{name}']"  
    if t == 'number':
        return repr(node['value'])
    if t == 'indicator':
        name = node['name']
        args = node.get('args', [])
        # transform args into code strings
        arg_codes = [value_to_code(a) for a in args]
        if name == 'sma':
            return f"sma({arg_codes[0]}, {int(args[1]['value'])})" if len(args) > 1 else f"sma({arg_codes[0]}, 20)"
        if name == 'rsi':
            return f"rsi({arg_codes[0]}, {int(args[1]['value'])})" if len(args) > 1 else f"rsi({arg_codes[0]}, 14)"
        return f"{name}({', '.join(arg_codes)})"
    if t == 'shift_expr':
        return f"df['{node['value'].split('.')[0]}'].shift({node['value'].split('(')[1].split(')')[0]})"
    if t == 'cross':
        left = value_to_code(node['left'])
        right = value_to_code(node['right'])
        return f"cross_above({left}, {right})"
    raise ValueError(f"Unknown value node: {node}")

def expr_to_code(node):
    if node is None:
        return "pd.Series(False, index=df.index)"
    typ = node.get('type')
    if typ == 'cmp':
        left = value_to_code(node['left'])
        right = value_to_code(node['right'])
        op = node['op']
        return f"({left} {op} {right})"
    if typ == 'and':
        return f"({expr_to_code(node['left'])}) & ({expr_to_code(node['right'])})"
    if typ == 'or':
        return f"({expr_to_code(node['left'])}) | ({expr_to_code(node['right'])})"
    if typ == 'cross':
        return value_to_code(node)
    if typ in ('name','indicator','number','shift_expr'):
        return value_to_code(node)
    raise ValueError(f"Unknown expr node type: {typ}")

def generate_signal_function(ast):
    """
    Returns a Python function object `signal_fn(df)` that returns a DataFrame with boolean columns 'entry' and 'exit'.
    We'll produce a code string and exec it into a local namespace capturing helpers.
    """
    entry_code = "pd.Series(False, index=df.index)"
    exit_code = "pd.Series(False, index=df.index)"
    if ast.get('entry'):
        entry_code = expr_to_code(ast['entry'])
    if ast.get('exit'):
        exit_code = expr_to_code(ast['exit'])

    code = f"""
def signal_fn(df):
    signals = pd.DataFrame(index=df.index)
    signals['entry'] = {entry_code}
    signals['exit']  = {exit_code}
    signals['entry'] = signals['entry'].fillna(False).astype(bool)
    signals['exit']  = signals['exit'].fillna(False).astype(bool)
    return signals
"""
    # create namespace with required helpers
    ns = {
        'pd': pd,
        'np': np,
        'sma': sma,
        'rsi': rsi,
        'cross_above': cross_above,
    }
    exec(textwrap.dedent(code), ns)
    return ns['signal_fn']

if __name__ == "__main__":
    sample_ast = {
        "entry": {"type": "and",
                  "left": {"type": "cmp", "op": ">", "left": {"type":"name","value":"close"}, "right": {"type":"indicator","name":"sma","args":[{"type":"name","value":"close"},{"type":"number","value":20}]}},
                  "right": {"type":"cmp","op":">","left":{"type":"name","value":"volume"},"right":{"type":"number","value":1000000}}
                 },
        "exit": {"type":"cmp","op":"<","left":{"type":"indicator","name":"rsi","args":[{"type":"name","value":"close"},{"type":"number","value":14}]},"right":{"type":"number","value":30}}
    }
    import pandas as pd
    dates = pd.date_range("2023-01-01", periods=30)
    df = pd.DataFrame({
        'open': 100 + (pd.Series(range(30))).cumsum() * 0.1,
        'high': 100 + (pd.Series(range(30))).cumsum() * 0.12,
        'low': 100 + (pd.Series(range(30))).cumsum() * 0.08,
        'close': 100 + (pd.Series(range(30))).cumsum() * 0.1,
        'volume': [900000]*5 + [1200000]*25
    }, index=dates)
    fn = generate_signal_function(sample_ast)
    sig = fn(df)
    print(sig.head())
