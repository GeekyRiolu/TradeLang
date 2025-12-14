import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from nl_dsl import nl_to_dsl
from dsl_parser import parse_dsl
from ast_python import generate_signal_function
from backtest import simple_backtest

st.set_page_config(
    page_title="TradeLang — Strategy Tester",
    layout="wide"
)

st.title("📈 TradeLang — Natural Language Trading Strategy Tester")

st.markdown("""
TradeLang lets you write trading strategies in **plain English**
and converts them into **executable trading logic**.
""")

with st.expander("ℹ️ How to write a valid strategy", expanded=True):
    st.markdown("""
### ✅ Supported sentence patterns

**ENTRY rules**
- Buy when the close price is above the 20-day moving average
- Buy when price crosses above the 20-day moving average
- Buy when volume is above 1M
- Combine conditions using **and**

**EXIT rules**
- Exit when RSI(14) is below 50
- Exit when price crosses below the 20-day moving average
- Exit when volume is below 900K

### ⚠️ Rules to remember
- Always include **one Buy rule** and **one Exit rule**
- Write **one sentence per line**
- Avoid free-form words like *strong*, *fast*, *significant*
- Do not use commas inside conditions

### ✅ Recommended example
Buy when price crosses above the 20-day moving average.
Exit when price crosses below the 20-day moving average.

pgsql
Copy code
""")

examples = {
    "Select an example": "",
    "MA Crossover (Best Demo)":
        "Buy when price crosses above the 20-day moving average.\n"
        "Exit when price crosses below the 20-day moving average.",

    "Trend + RSI Exit":
        "Buy when the close price is above the 20-day moving average.\n"
        "Exit when RSI(14) is below 50.",

    "Volume Breakout":
        "Buy when the close price is above the 20-day moving average and volume is above 1M.\n"
        "Exit when RSI(14) is below 60."
}

selected_example = st.selectbox(
    "📌 Try a supported example strategy",
    list(examples.keys())
)

nl_input = st.text_area(
    "🧠 Natural Language Strategy",
    value=examples[selected_example],
    height=140,
    placeholder="Line 1: Buy rule\nLine 2: Exit rule"
)

run_btn = st.button("🚀 Run Strategy")

def load_sample_data():
    dates = pd.date_range("2023-01-01", periods=120)
    t = np.arange(len(dates))
    close = 115 + 10 * np.sin(t / 6) + np.random.normal(0, 1, len(dates))

    return pd.DataFrame({
        "open": close + np.random.normal(0, 0.5, len(dates)),
        "high": close + 1,
        "low": close - 1,
        "close": close,
        "volume": np.random.randint(700_000, 1_500_000, len(dates))
    }, index=dates)

df = load_sample_data()

def plot_price_signals(df, signals):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["close"], label="Close Price")

    entry_points = df[signals["entry"]]
    exit_points = df[signals["exit"]]

    ax.scatter(entry_points.index, entry_points["close"], marker="^", s=80, label="Entry")
    ax.scatter(exit_points.index, exit_points["close"], marker="v", s=80, label="Exit")

    ax.set_title("Price with Entry / Exit Signals")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.grid(True)

    return fig

if run_btn:
    if not nl_input.strip():
        st.warning("⚠️ Please enter a strategy or select an example.")
        st.stop()

    lines = [l.strip() for l in nl_input.splitlines() if l.strip()]

    if len(lines) < 2:
        st.error("❌ Strategy must contain two lines: Buy rule and Exit rule.")
        st.stop()

    if not lines[0].lower().startswith("buy"):
        st.error("❌ First line must start with a BUY rule.")
        st.stop()

    if not lines[1].lower().startswith("exit"):
        st.error("❌ Second line must start with an EXIT rule.")
        st.stop()

    unsupported_words = ["strong", "weak", "significant", "quick", "fast"]
    if any(word in nl_input.lower() for word in unsupported_words):
        st.warning("⚠️ Some words may not be supported. Consider simplifying the strategy.")

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
            st.subheader("📈 Price Chart with Signals")
            fig = plot_price_signals(df, signals)
            st.pyplot(fig)

            st.subheader("🔢 Signal Counts")
            st.write({
                "Entry Signals": int(signals["entry"].sum()),
                "Exit Signals": int(signals["exit"].sum())
            })

            if result["trades"] == 0:
                st.info(
                    "ℹ️ No trades were executed because the exit condition "
                    "was never satisfied on this data."
                )

    except Exception:
        st.error("❌ Unable to parse or execute the strategy.")
        st.info("💡 Tip: Use one of the example strategies above or follow the input rules.")

st.markdown("---")
st.caption("TradeLang · NL → DSL → AST → Execution")