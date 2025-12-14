import re

NUMBER_MAP = {
    'k': 1_000,
    'K': 1_000,
    'm': 1_000_000,
    'M': 1_000_000,
}

def parse_number_token(tok: str):
    """Convert tokens like '1M', '1.2M', '100000' into numbers or DSL numeric text."""
    tok = tok.replace(',', '').strip()
    m = re.match(r'^(\d+(\.\d+)?)([kKmM])?$', tok)
    if not m:
        raise ValueError(f"Unrecognized number: {tok}")
    base = float(m.group(1))
    suffix = m.group(3)
    if suffix:
        return int(base * NUMBER_MAP[suffix])
    else:
        if base.is_integer():
            return int(base)
        return base

def _normalize(text: str):
    return text.strip().lower()

def nl_to_dsl(nl: str) -> str:
    """
    Convert some common English trading-rule sentences into DSL.
    This is heuristic-driven and supports the examples in the assignment.
    """
    s = nl.strip()

    s = s.replace("price closes", "close")
    s = s.replace("price close", "close")
    s = s.replace("closes", "close")
    s = s.replace("close price", "close")
    s = s.replace("price", "close")  
    s = s.replace("yesterday's", "yesterday_")
    s = s.replace("yesterday ", "yesterday_")

    s = s.replace("is above", ">")
    s = s.replace("above", ">")
    s = s.replace("is below", "<")
    s = s.replace("below", "<")
    s = s.replace("and", "AND")
    s = s.replace("or", "OR")

    s = re.sub(r'(\d+)-day moving average', r'SMA(close,\1)', s, flags=re.IGNORECASE)
    s = re.sub(r'(\d+)\s+day moving average', r'SMA(close,\1)', s, flags=re.IGNORECASE)


    s = re.sub(r'rsi\s*\(?\s*(\d+)\s*\)?', r'RSI(close,\1)', s, flags=re.IGNORECASE)

    s = re.sub(r'(\d+(\.\d+)?\s*(m|M))', lambda m: str(parse_number_token(m.group(0))), s)
    s = re.sub(r'(\d+(\.\d+)?\s*(k|K))', lambda m: str(parse_number_token(m.group(0))), s)

    s = re.sub(r'crosses?\s+above\s+yesterday[_ ]high', r'CROSS(close, high.shift(1))', s, flags=re.IGNORECASE)
    s = re.sub(r'crosses?\s+above\s+yesterday[_ ]low', r'CROSS(close, low.shift(1))', s, flags=re.IGNORECASE)
    s = re.sub(r'crosses?\s+above\s+yesterday[_ ]close', r'CROSS(close, close.shift(1))', s, flags=re.IGNORECASE)

    s = re.sub(r'crosses?\s+above\s+([^\.\,]+)', r'CROSS(close, \1)', s, flags=re.IGNORECASE)

    s = s.replace('.', '')
    s = s.replace('  ', ' ')
    entry_parts = []
    exit_parts = []

    lowered = nl.lower()
    if any(tok in lowered for tok in ['buy', 'enter', 'trigger entry', 'entry when']):
        if 'exit' in lowered or 'sell' in lowered:
            parts = re.split(r'\bexit\b|\bsell\b', s, flags=re.IGNORECASE)
            entry_parts.append(parts[0].strip())
            if len(parts) > 1:
                exit_parts.append(parts[1].strip())
        else:
            entry_parts.append(s.strip())
    else:
        entry_parts.append(s.strip())

    if 'rsi' in s.lower() and ('exit' in lowered or 'sell' in lowered or 'exit when' in lowered or 'exit:' in s.lower()):
        if s not in exit_parts:
            exit_parts.append(s.strip())

    entry_dsl = ''
    exit_dsl = ''
    if entry_parts:
        entry_dsl = ' AND '.join([p for p in entry_parts if p])
        entry_dsl = entry_dsl.replace('close close', 'close')
    if exit_parts:
        exit_dsl = ' AND '.join([p for p in exit_parts if p])

    dsl_lines = []
    if entry_dsl:
        dsl_lines.append("ENTRY:")
        dsl_lines.append(entry_dsl)
    if exit_dsl:
        dsl_lines.append("EXIT:")
        dsl_lines.append(exit_dsl)

    if not exit_dsl:
        dsl_lines.append("EXIT:")
        dsl_lines.append("")

    return "\n".join(dsl_lines)


if __name__ == "__main__":
    examples = [
        "Buy when the close price is above the 20-day moving average and volume is above 1 million.",
        "Enter when price crosses above yesterday’s high.",
        "Exit when RSI(14) is below 30.",
        "Trigger entry when volume increases by more than 30 percent compared to last week."
    ]
    for e in examples:
        print("NL:", e)
        print(nl_to_dsl(e))
        print('----')
