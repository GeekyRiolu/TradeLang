from lark import Lark, Transformer, Token

GRAMMAR = r"""
start: section*

section: ENTRY ":" _NL? expr?
       | EXIT ":" _NL? expr?

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

comparison: value comp_op value

cross_expr: "CROSS" "(" value "," value ")"

?value: indicator
      | SHIFT_EXPR
      | NAME
      | NUMBER

indicator: NAME "(" args ")"
args: value ("," value)*

comp_op: ">"|"<"|">="|"<="|"=="

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
        for sec in items:
            k = sec[0].lower()
            out[k] = sec[1] if len(sec) > 1 else None
        return out

    def section(self, items):
        return items

    def or_op(self, items):
        return {"type": "or", "left": items[0], "right": items[1]}

    def and_op(self, items):
        return {"type": "and", "left": items[0], "right": items[1]}

    def comparison(self, items):
        return {"type": "cmp", "op": items[1], "left": items[0], "right": items[2]}

    def comp_op(self, items):
        return items[0]

    def NAME(self, tok):
        return {"type": "name", "value": tok.value}

    def NUMBER(self, tok):
        return {"type": "number", "value": float(tok)}

    def indicator(self, items):
        return {"type": "indicator", "name": items[0]["value"], "args": items[1]}

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
