from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

class Type(Enum):
    VOID = "void"
    CHAR = "char"
    SHORT = "short"
    INT = "int"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"

    def __str__(self):
        return self.value   #per stampare int e non Type.INT di python


@dataclass
class Node:                 #per salvare posizione di errore nel codice
    line: int = field(default=0, kw_only=True, repr=False, compare=False)
    column: int = field(default=0, kw_only=True, repr=False, compare=False)


@dataclass
class Expr(Node):
    ty: Optional[Type] = field(default=None, kw_only=True, repr=False, compare=False)


@dataclass
class Stmt(Node):
    pass


@dataclass
class IntLit(Expr):
    value : int


@dataclass
class FloatLit(Expr):
    value: float


@dataclass
class CharLit(Expr):
    value: str


@dataclass
class StringLit(Expr):
    value: str 


@dataclass
class Var(Expr):
    name : str


@dataclass
class Unary(Expr):
    op: str             # "+", "-", "!"
    operand: Expr


@dataclass
class Binary(Expr):
    op: str             # + - * / % == != < <= > >= && ||
    left: Expr
    right: Expr


@dataclass
class Cast(Expr):
    target: Type
    operand: Expr


@dataclass
class Assign(Expr):
    target: Expr        # deve essere una Var: lo verifica l'analisi semantica
    value: Expr


@dataclass
class Call(Expr):
    name: str
    args: list[Expr]


@dataclass
class VarDecl(Stmt):
    type: Type
    name: str
    init: Optional[Expr] = None


@dataclass
class Param(Node):
    type: Type
    name: str


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class EmptyStmt(Stmt):
    pass


@dataclass
class Block(Stmt):
    stmts: list[Stmt]


@dataclass
class If(Stmt):
    cond: Expr
    then: Block
    otherwise: Optional[Union[Block, "If"]] = None


@dataclass
class While(Stmt):
    cond: Expr
    body: Block


@dataclass
class DoWhile(Stmt):
    body: Block
    cond: Expr


@dataclass
class For(Stmt):
    init: Optional[Union[VarDecl, Expr]]
    cond: Optional[Expr]
    step: Optional[Expr]
    body: Block


@dataclass
class Return(Stmt):
    value: Optional[Expr] = None


@dataclass
class Break(Stmt):
    pass


@dataclass
class Read(Stmt):
    target: Var


@dataclass
class Write(Stmt):
    value: Expr


@dataclass
class Continue(Stmt):
    pass


@dataclass
class FunctionDecl(Node):
    return_type: Type
    name: str
    params: list[Param]
    body: Block


@dataclass
class Program(Node):
    items: list[Union[FunctionDecl, VarDecl]]