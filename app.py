import streamlit as st
import pandas as pd
import numpy as np

from nl_dsl import nl_to_dsl
from dsl_parser import parse_dsl
from ast_python import generate_signal_function
from backtest import simple_backtest

st.set_page_config(page_title="TradeLang Demo", layout="wide")

st.title("📈 TradeLang — Natural Language Trading Strategy Tester")

st.markdown("""
Type a trading strategy in **plain English** and see how it gets:
- Converted into a DSL
- Parsed into an AST
- Executed on market data
""")

# -------- Input --------
nl_input = st.text_area(
    "🧠 Natural Language Strategy",
    value="Buy when the close price is above the 20-day moving average and volume is above 1M. Exit when RSI(14) is below 30.",
    height=120
)

run_btn = st.button("🚀 Run Strategy")

# -------- Sample Data --------
def load_sample_data():
    dates = pd.date_range("2023-01-01", periods=80)
    close = np.linspace(100, 130, len(dates)) + np.random.normal(0, 1, len(dates))
    df = pd.DataFrame({
        "close": close,
        "open": close + np.random.normal(0, 0.5, len(dates)),
        "high": close + 1,
        "low": close - 1,
        "volume": np.random.randint(700_000, 1_500_000, len(dates))
    }, index=dates)
    return df

df = load_sample_data()

# -------- Execution --------
if run_btn:
    try:
        dsl = nl_to_dsl(nl_input)
        ast = parse_dsl(dsl)
        signal_fn = generate_signal_function(ast)
        signals = signal_fn(df)
        result = simple_backtest(df, signals)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📜 Generated DSL")
            st.code(dsl, language="text")

            st.subheader("📊 Backtest Result")
            st.json(result)

        with col2:
            st.subheader("📈 Signals Preview")
            preview = pd.concat([df, signals], axis=1)
            st.dataframe(preview.tail(15))

            st.subheader("📉 Entry / Exit Count")
            st.write({
                "Entries": int(signals["entry"].sum()),
                "Exits": int(signals["exit"].sum())
            })

    except Exception as e:
        st.error("❌ Error while executing strategy")
        st.exception(e)

st.markdown("---")
st.caption("TradeLang · NL → DSL → AST → Execution")
