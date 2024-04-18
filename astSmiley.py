from dataclasses import dataclass

@dataclass(slots=True)
class AST:
    line: int

@dataclass(slots=True)
class Expression:
    type: str

@dataclass(slots=True)
class Unary(Expression):
    op: str
    expr: Expression

@dataclass(slots=True)
class Binary(Expression):
    lhs: Expression
    op: str
    rhs: Expression

@dataclass(slots=True)
class Literal(Expression):
    pass

@dataclass(slots=True)
class Bool(Literal):
    val: bool

@dataclass(slots=True)
class Int(Literal):
    val: int

@dataclass(slots=True)
class Str(Literal):
    val: str

@dataclass(slots=True)
class Id(Expression):
    name: str
    constant: bool

@dataclass(slots=True)
class Statement(AST):
    pass

@dataclass(slots=True)
class Declaration(Statement):
    type: str
    name: Id

@dataclass(slots=True)
class Assign(Statement):
    id: Id
    expr: Expression

@dataclass(slots=True)
class Print(Statement):
    expr: Expression

@dataclass(slots=True)
class If(Statement):
    expr: Expression
    stmt: list[Statement]

@dataclass(slots=True)
class Else(Statement):
    expr: Expression
    stmt: list[Statement]

@dataclass(slots=True)
class While(Statement):
    expr: Expression
    stmt: list[Statement]

@dataclass(slots=True)
class Program:
    stmt: list[Statement]