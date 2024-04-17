from dataclasses import dataclass

@dataclass(slots=True)
class AST:
    line: int

@dataclass(slots=True)
class Token(AST):
    token: str

@dataclass(slots=True)
class Id(Token):
    pass

@dataclass(slots=True)
class VariableId(Id):
    name: str
    type: str

@dataclass(slots=True)
class BoolConstantId(Id):
    name: str
    val: bool

@dataclass(slots=True)
class IntConstantId(Id):
    name: str
    val: int

@dataclass(slots=True)
class StrConstantId(Id):
    name: str
    val: str

@dataclass(slots=True)
class Expression(AST):
    type: str

@dataclass(slots=True)
class Literal(Expression):
    token: str

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
class Statement(AST):
    pass

@dataclass(slots=True)
class Declaration(Statement):
    type: str
    name: Id

@dataclass(slots=True)
class Assign(Statement):
    id: VariableId
    expr: Expression = None

@dataclass(slots=True)
class Print(Statement):
    expr: Expression

@dataclass(slots=True)
class If(Statement):
    expr: Expression
    stmt: Statement

@dataclass(slots=True)
class Else(Statement):
    expr: Expression = None
    stmt: Statement