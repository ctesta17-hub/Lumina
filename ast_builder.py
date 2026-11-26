import ast as pyast
from pathlib import Path
from lark import Lark, Transformer, v_args
from ast_nodes import *


GRAMMAR = Path(__file__).with_name("grammar.lark")

_parser = Lark.open(
    str(GRAMMAR),
    parser="lalr",
    propagate_positions=True,            #tiene traccia della posizione per ogni regola
    maybe_placeholders=True,            #le parti [...] arrivano con None
)

def _posNode(meta) -> dict:
    if getattr(meta, "empty", True):
        return {}
    return {"line" : meta.line, "column" : meta.column}


def _flattenList(items: list) -> list:  #appiattisce le liste annidate (es. var_decl multiple)
    out = []
    for x in items:
        if isinstance(x, list):
            out.extend(_flattenList(x)) #ricorsiva in caso di annidamenti multipli
        else:
            out.append(x)
    return out


@v_args(meta=True)                      #tiene traccia nella posizione per l'analisi semantica
class ASTBuilder(Transformer):
    def start(self, meta, children):
        return Program(_flattenList(children), **_posNode(meta))


    def global_var(self, meta, children):   #lista di var_decl
        return children[0]


    def function(self, meta, children):
        ret, name, params, body = children
        return FunctionDecl(ret, str(name), params, body, **_posNode(meta))


    def params(self, meta, children):
        return list(children)


    def param(self, meta, children):
        ty, name = children
        return Param(ty, str(name), **_posNode(meta))


    def var_decl(self, meta, children):
        ty, *declarators = children
        decls = []
        for name, init, pos_node in declarators:
            decls.append(VarDecl(ty, name, init, **pos_node))
        return decls

    
    def declarator(self, meta, children):
        name, init = children
        return (str(name), init, _posNode(meta))


    def t_void(self, meta, children): return Type.VOID
    def t_int(self, meta, children): return Type.INT
    def t_long(self, meta, children): return Type.LONG
    def t_short(self, meta, children): return Type.SHORT
    def t_float(self, meta, children): return Type.FLOAT
    def t_double(self, meta, children): return Type.DOUBLE
    def t_char(self, meta, children): return Type.CHAR
    def t_string(self, meta, children): return Type.STRING


    def block(self, meta, children):
        return Block(_flattenList(children), **_posNode(meta))


    def expr_stmt(self, meta, children):
        return ExprStmt(children[0], **_posNode(meta))


    def empty_stmt(self, meta, children):
        return EmptyStmt(**_posNode(meta))


    def condition(self, meta, children):
        return children[0]


    def if_stmt(self, meta, children):
        cond = children[0]
        then = children[1]
        otherwise = children[2]
        return If(cond, then, otherwise, **_posNode(meta))


    def while_stmt(self, meta, children):
        cond, body = children
        return While(cond, body, **_posNode(meta))


    def do_while_stmt(self, meta, children):
        body, cond = children
        return DoWhile(body, cond, **_posNode(meta))


    def for_stmt(self, meta, children):
        init, cond, step, body = children
        return For(init, cond, step, body, **_posNode(meta))


    def for_decl(self, meta, children):
        ty, (name, init, posNode) = children
        return VarDecl(ty, name, init, **posNode)


    def for_expr(self, meta, children):
        return children[0]


    def ret_stmt(self, meta, children):
        if(len(children) > 0):
            value = children[0]
        else:
            value = None
        return Return(value, **_posNode(meta))


    def read_stmt(self, meta, children):
        name = children[0]
        return Read(Var(str(name), line=name.line, column=name.column), **_posNode(meta))


    def write_stmt(self, meta, children):
        return Write(children[0], **_posNode(meta))


    def br_stmt(self, meta, children):
        return Break(**_posNode(meta))


    def cnt_stmt(self, meta, children):
        return Continue(**_posNode(meta))


    def assign(self, meta, children):
        target, value = children
        return Assign(target, value, **_posNode(meta))


    def lor(self, meta, children):
        return Binary("||", children[0], children[1], **_posNode(meta))


    def land(self, meta, children):
        return Binary("&&", children[0], children[1], **_posNode(meta))


    def binop(self, meta, children):
        left, op, right = children
        return Binary(str(op), left, right, **_posNode(meta))


    def unary_arith(self, meta, children):
        op, operand = children
        return Unary(str(op), operand, **_posNode(meta))


    def lnot(self, meta, children):
        return Unary("!", children[0], **_posNode(meta))


    def cast(self, meta, children):
        target, operand = children
        return Cast(target, operand, **_posNode(meta))


    def call(self, meta, children):
        name, args = children
        return Call(str(name), args or [], **_posNode(meta))


    def args(self, meta, children):
        return list(children)


    def int_lit(self, meta, children):
        return IntLit(int(children[0]), **_posNode(meta))
    

    def float_lit(self, meta, children):
        return FloatLit(float(children[0]), **_posNode(meta))


    def char_lit(self, meta, children):
        return CharLit(pyast.literal_eval(str(children[0])), **_posNode(meta))


    def string_lit(self, meta, children):
        return StringLit(pyast.literal_eval(str(children[0])), **_posNode(meta))


    def var(self, meta, children):
        return Var(str(children[0]), **_posNode(meta))


def lex(source: str):
    return list(_parser.lex(source))


def parse(source: str):
    return _parser.parse(source)


def build_ast(source: str):
    return ASTBuilder().transform(parse(source))