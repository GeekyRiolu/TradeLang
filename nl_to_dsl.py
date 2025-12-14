import re

def nl_to_dsl(nl: str) -> str:
    nl = nl.lower()

    entry_parts = []
    exit_parts = []

    if "20-day moving average" in nl or "20 day moving average" in nl:
        entry_parts.append("close > SMA(close,20)")

    if "volume" in nl and ("above" in nl or "greater" in nl):
        entry_parts.append("volume > 1000000")

    if "crosses above yesterday" in nl and "high" in nl:
        entry_parts.append("CROSS(close, high.shift(1))")

    if "rsi" in nl and "below" in nl:
        exit_parts.append("RSI(close,14) < 30")

    entry_expr = " AND ".join(entry_parts) if entry_parts else "False"
    exit_expr = " AND ".join(exit_parts) if exit_parts else "False"

    return f"""ENTRY:
{entry_expr}
EXIT:
{exit_expr}
"""
