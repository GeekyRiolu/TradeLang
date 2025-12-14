from lark import Lark, Transformer

GRAMMAR = r"""
start: _NL* section (_NL+ section)* _NL*

section: ENTRY ":" _NL* expr?
       | EXIT ":" _NL* expr?

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

comparison: value OP value
OP: ">"|"<"|">="|"<="|"=="

cross_expr: "CROSS" "(" value "," value ")"

?value: indicator
      | SHIFT_EXPR
      | NAME
      | NUMBER

indicator: NAME "(" args ")"
args: value ("," value)*

SHIFT_EXPR: /[a-zA-Z_][a-zA-Z0-9_]*\.shift\(\d+\)/

_NL: /(\r?\n)+/

%import common.CNAME -> NAME
%import common.SIGNED_NUMBER -> NUMBER
%import common.WS_INLINE
%ignore WS_INLINE
"""

class ASTTransformer(Transformer):
    def start(self, items):
        out = {}
        for item in items:
            if isinstance(item, list):
                out[item[0].lower()] = item[1] if len(item) > 1 else None
        return out

    def section(self, items):
        return items

    def or_op(self, items):
        return {"type": "or", "left": items[0], "right": items[1]}

    def and_op(self, items):
        return {"type": "and", "left": items[0], "right": items[1]}

    def comparison(self, items):
        left, op, right = items
        return {
            "type": "cmp",
            "op": op.value,
            "left": left,
            "right": right
        }

    def NAME(self, tok):
        return {"type": "name", "value": tok.value}

    def NUMBER(self, tok):
        return {"type": "number", "value": float(tok)}

    def indicator(self, items):
        return {
        "type": "indicator",
        "name": items[0]["value"].lower(),
        "args": items[1]
        }

    def args(self, items):
        return items

    def cross_expr(self, items):
        return {"type": "cross", "left": items[0], "right": items[1]}

    def SHIFT_EXPR(self, tok):
        base, rest = tok.value.split(".shift(")
        return {"type": "shift", "base": base, "n": int(rest[:-1])}

def parse_dsl(text: str):
    parser = Lark(GRAMMAR, parser="lalr")
    tree = parser.parse(text)
    ast = ASTTransformer().transform(tree)
    ast.setdefault("entry", None)
    ast.setdefault("exit", None)
    return ast
