from lark import Lark, Transformer, v_args, Token

GRAMMAR = r"""
start: section*

section: ENTRY ":" expr?
       | EXIT ":" expr?

ENTRY.2: /ENTRY/i
EXIT.2: /EXIT/i

?expr: or_expr
?or_expr: and_expr
        | or_expr "OR" and_expr   -> or_op
?and_expr: atom
         | and_expr "AND" atom    -> and_op

?atom: "(" expr ")"
     | comparison
     | cross_expr

?comparison: value comp_op value    -> comparison

?cross_expr: "CROSS" "(" value "," value ")"  -> cross

?value: indicator
      | NAME
      | NUMBER
      | SHIFT_EXPR

indicator: NAME "(" [args] ")"
args: value ("," value)*

comp_op: ">"|"<"|">="|"<="|"=="

SHIFT_EXPR: /[a-zA-Z_][a-zA-Z0-9_]*\.shift\(\d+\)/

%import common.CNAME -> NAME
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""

from lark import Token
from lark import Tree

class ASTTransformer(Transformer):
    def start(self, items):
        out = {}
        for sec in items:
            if not sec:
                continue
            typ = sec[0]
            expr = sec[1] if len(sec) > 1 else None
            key = typ.lower()
            out[key] = expr
        return out

    def section(self, items):
        return items

    def ENTRY(self, tok):
        return str(tok)

    def EXIT(self, tok):
        return str(tok)

    def or_op(self, items):
        left, right = items
        return {"type": "or", "left": left, "right": right}

    def and_op(self, items):
        left, right = items
        return {"type": "and", "left": left, "right": right}

    def comparison(self, items):
        left, op, right = items
        return {"type": "cmp", "op": str(op), "left": left, "right": right}

    def comp_op(self, items):
        return Token('COMP', items[0].value)

    def NAME(self, tok):
        return {"type": "name", "value": str(tok)}

    def NUMBER(self, tok):
        txt = tok.value
        if "." in txt:
            v = float(txt)
        else:
            v = int(txt)
        return {"type": "number", "value": v}

    def indicator(self, items):
        name = items[0] if isinstance(items[0], dict) and items[0].get('type') == 'name' else items[0]
        func_name = name['value'] if isinstance(name, dict) else str(name)
        args = []
        if len(items) > 1:
            args = items[1]
        return {"type": "indicator", "name": func_name.lower(), "args": args}

    def args(self, items):
        return items

    def cross(self, items):
        left, right = items
        return {"type": "cross", "left": left, "right": right}

    def SHIFT_EXPR(self, tok):
        return {"type": "shift_expr", "value": tok.value}

def parse_dsl(text: str):
    parser = Lark(GRAMMAR, start='start', parser='lalr', propagate_positions=False, maybe_placeholders=False)
    tree = parser.parse(text)
    ast = ASTTransformer().transform(tree)
    if 'entry' not in ast:
        ast['entry'] = None
    if 'exit' not in ast:
        ast['exit'] = None
    return ast

if __name__ == "__main__":
    sample = """ENTRY:
close > SMA(close,20) AND volume > 1000000
EXIT:
RSI(close,14) < 30
"""
    ast = parse_dsl(sample)
    import json
    print(json.dumps(ast, indent=2))
