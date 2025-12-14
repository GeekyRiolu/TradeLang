def nl_to_dsl(nl: str) -> str:
    nl = nl.lower()

    entry_parts = []
    exit_parts = []

    if "crosses above" in nl and "moving average" in nl:
        entry_parts.append("CROSS(close, SMA(close,20))")

    if "crosses below" in nl and "moving average" in nl:
        exit_parts.append("CROSS(SMA(close,20), close)")

    if "close price is above the 20-day moving average" in nl:
        entry_parts.append("close > SMA(close,20)")

    if "volume is above" in nl:
        entry_parts.append("volume > 1000000")

    if "rsi" in nl and "below" in nl:
        exit_parts.append("RSI(close,14) < 50")

    entry_expr = " AND ".join(entry_parts) if entry_parts else "False"
    exit_expr = " AND ".join(exit_parts) if exit_parts else "False"

    return f"""ENTRY:
{entry_expr}
EXIT:
{exit_expr}
"""
