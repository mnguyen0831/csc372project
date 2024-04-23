from exprSmiley import evalExpr, baseExpr, validateVal, validateName, raiseErr

### Have to rewrite line
def declarest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <declare st> ::= <type> <var id> . | <type> <const id> _is <literal> .
    var = variables.copy()
    if '.' not in line:
        raiseErr(f"SyntaxError: Declaration of '{line[1]}' on line {lnum} not terminated with '.'", lnum)
    if line[-1] != '.':
        raiseErr(f"SyntaxError: Declaration of '{line[1]}' on line {lnum} not terminated with '.'", lnum)
    if len(line) < 2:
        raiseErr(f"SyntaxError: Declaration statement on line '{lnum}' does not indicate a variable to declare", lnum)
    name = line[1]
    if name[0].islower():
        if '_is' in line:
            raiseErr(f"TypeError: Variable '{name}' on line {lnum} cannot be assigned at declaration", lnum)
        if len(line) > 3:
            raiseErr(f"SyntaxError: Declaration of variable '{name}' on line {lnum} can only contain the type and name", lnum)
        var[name] = [line[0], None]
    elif name[0].isupper():
        if '_is' not in line:
            raiseErr(f"SyntaxError: Constant '{name}' declaration on line {lnum} must be followed immediately by '_is'", lnum)
        if line[2] != '_is':
            raiseErr(f"SyntaxError: Constant '{name}' declaration on line {lnum} must be followed immediately by '_is'", lnum)
        if len(line) < 5:
            raiseErr(f"SyntaxError: Constant '{name}' declaration on line {lnum} must be declared with a literal of type {line[0]}", lnum)
        val = baseExpr(line[3:], var, lnum)[0]
        type = line[0]
        if type == '_int':
            if not isinstance(val, int):
                raiseErr(f"TypeError: Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}", lnum)
        elif type == '_bool':
            if not isinstance(val, bool):
                raiseErr(f"TypeError: Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}", lnum)
        elif type == '_str':
            if not isinstance(val, str):
                raiseErr(f"TypeError: Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}", lnum)
        var[name] = ['const ' + type, val]
    else:
        raiseErr(f"NameError: '{name}' on line {lnum} is not a valid name", lnum)
    return var 


def assignst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <assign st> ::= <var id> _is <expr> . | <var id> ++ . | <var id> += <expr> .
    var = variables.copy()
    name = line[0]
    if '.' not in line:
        raiseErr(f"SyntaxError: Assignment of '{name}' on line {lnum} not terminated with '.'", lnum)
    if line[-1] != '.':
        raiseErr(f"SyntaxError: Assignment of '{name}' on line {lnum} not terminated with '.'", lnum)
    if '_is' not in line and '++' not in line and '+=' not in line:
        raiseErr(f"SyntaxError: Assignment of '{name}' on line {lnum} is missing an assignment operator", lnum)
    if not validateName(name, variables):
        raiseErr(f"NameError: Variable '{name}' on line {lnum} must be declared before assignment", lnum)
    type = var[name][0]
    curVal = var[name][1]
    if len(type) > 5:
        raiseErr(f"TypeError: Constant '{name}' of type {type} on line {lnum} cannot be reassigned.", lnum)
    if line[1] == '_is':
        val = evalExpr(line[2:], variables, lnum)
        validateVal(type, val, lnum)
        var[name][1] = val
    elif line[1] == '++':
        if type == '_int':
            if curVal is None:
                raiseErr(f"NameError: Variable '{name}' on line {lnum} cannot be incremented since it hasn't been initialized yet", lnum)
            var[name][1] += 1
        else:
            raiseErr(f"TypeError: Operation '++' on line {lnum} is invalid for {type} types", lnum)
    elif line[1] == '+=':
        if type == '_int':
            if curVal is None:
                raiseErr(f"NameError: Variable '{name}' on line {lnum} cannot be added to since it hasn't been initialized yet", lnum)
            val = evalExpr(line[2:], variables, lnum)
            validateVal(type, val, lnum)
            var[name][1] += val
        elif type == '_str':
            if curVal is None:
                raiseErr(f"NameError: Variable '{name}' on line {lnum} cannot be added to since it hasn't been initialized yet", lnum)
            val = evalExpr(line[2:], variables, lnum)
            validateVal(type, val, lnum)
            var[name][1] += val
        else:
            raiseErr(f"TypeError: Operation '+=' on line {lnum} is invalid for {type} types", lnum)
    return var


def readst(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> dict[str, list[int | bool | str | None]]:
    # <read st> ::= _read <var id> .
    var = variables.copy()
    if '.' not in line:
        raiseErr(f"SyntaxError: _read statement on line {lnum} not terminated with '.'", lnum)
    if line[-1] != '.':
        raiseErr(f"SyntaxError: _read statement on line {lnum} not terminated with '.'", lnum)
    if len(line) != 3:
        raiseErr(f"SyntaxError: _read statement on line {lnum} should only contain the variable name", lnum)
    if line[1] not in var.keys():
        raiseErr(f"NameError: Variable '{line[1]}' in the _read statement on line {lnum} has not been declared", lnum)
    if len(var[line[1]][0]) > 5:
        raiseErr(f"TypeError: Constant '{line[0]}' of type {var[line[0]][0]} in the _read statement on line {lnum} cannot be reassigned.", lnum)
    
    val: int | bool | str
    type = var[line[1]][0]
    while True:
        val = input().strip().split()
        val = evalExpr(val, variables, lnum)
        if type == '_int':
            if isinstance(val, int):
                break
        elif type == '_bool':
            if isinstance(val, bool):
                break
        elif type == '_str':
            if isinstance(val, str):
                break
        print(f"The value '{val}' is not a valid {type} type")
        print('Examples of valid inputs:')
        print("\tint: - 3")
        print('\tstr: "String"')
        print("\tbool: ^ :)")
        print("Note that all operators must be separated from the operands with whitespace")
        print("Please try again")
    var[line[1]][1] = val
    return var


def printst(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> None:
    # <print st> ::= _writeline <expr> . | _write <expr> .
    if '.' not in line:
        raiseErr(f"SyntaxError: {line[0]} statement on line {lnum} not terminated with '.'", lnum)
    if line[-1] != '.':
        raiseErr(f"SyntaxError: {line[0]} statement on line {lnum} not terminated with '.'", lnum)
    if len(line) < 3:
        raiseErr(f"SyntaxError: {line[0]} statement on line {lnum} must contain an expression", lnum)
    val = evalExpr(line[1:], variables, lnum)
    if line[0] == '_write':
        print(val, end='')
    elif line[0] == '_writeline':
        print(val)


def ifst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <if st> ::= _if <expr> _then { <statement> } | _if <expr> _then { <statement> } <else>
    if '_then' not in line:
        raiseErr(f"SyntaxError: _if statment in line {lnum} must have '_then' following the expression", lnum)
    if '{' not in line:
        raiseErr(f"SyntaxError: _if statement must have '{{' at the end of line {lnum}", lnum)
    if line[-1] != '{':
        raiseErr(f"SyntaxError: _if statement '{{' at the end of line {lnum}", lnum)
    if line[-2] != '_then':
        raiseErr(f"SyntaxError: '_then' in line {lnum} must immediately precede '{{'", lnum)
    if len(line) < 4:
        raiseErr(f"SyntaxError: _if statement on line {lnum} must contain a _bool expression", lnum)
    val = evalExpr(line[1:], variables, lnum)
    if not isinstance(val, bool):
        raiseErr(f"TypeError: Value of the _if expression on line {lnum} is not type _bool", lnum)
    return val


def elsest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <else> ::= _else { <statement> } | _elseif <expr> _then { <statement> } | _elseif <expr> _then { <statement> } <else>
    if '{' not in line:
        raiseErr(f"SyntaxError: Missing '{{' at the end of line {lnum}", lnum)
    if line[-1] != '{':
        raiseErr(f"SyntaxError: Missing '{{' at the end of line {lnum}", lnum) 
    if '_else' not in line and '_elseif' not in line:
        raiseErr(f"SyntaxError: Missing '_else' or '_elseif' in line {lnum}", lnum)
    if '_else' in line:
        if line[1] != '_else':
            raiseErr(f"SyntaxError: '_else' on line {lnum} must immediately follow '}}", lnum)
        if len(line) != 3:
            raiseErr(f"SyntaxError: _else statement on line {lnum} cannot have an expression", lnum)
    elif '_elseif' in line:
        if line[1] != '_elseif':
            raiseErr(f"SyntaxError: '_elseif' on line {lnum} must immediately follow '}}'", lnum)
        if '_then' not in line:
            raiseErr(f"SyntaxError: Missing '_then' following the expression on line {lnum}", lnum)
        if line[-2] != '_then':
            raiseErr(f"SyntaxError: '_then' on line {lnum} must immediately precede '{{'", lnum)
        if len(line) < 5:
            raiseErr(f"SyntaxError: _elseif statement on line {lnum} must contain a _bool expression", lnum)
        val = evalExpr(line[2:], variables, lnum)
        if not isinstance(val, bool):
            raiseErr(f"TypeError: Value of the _elseif expression on line {lnum} is not type _bool", lnum)
        return val
    return False


def whilest(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> bool:
    # <while st> ::= _while <expr> _do { <statement> }
    if '{' not in line:
        raiseErr(f"SyntaxError: Missing '{{' at the end of line {lnum}", lnum)
    if line[-1] != '{':
        raiseErr(f"SyntaxError: Missing '{{' at the end of line {lnum}", lnum) 
    if '_do' not in line:
        raiseErr(f"SyntaxError: Missing '_do' after the expression in line {lnum}", lnum)
    if line[-2] != '_do':
            raiseErr (f"SyntaxError: Missing '_do' after the expression in line {lnum}", lnum)
    if len(line) < 4:
        raiseErr(f"SyntaxError: _while statement on line {lnum} must contain a _bool expression", lnum)
    val = evalExpr(line[1:], variables, lnum)
    if not isinstance(val, bool):
        raiseErr(f"TypeError: Value of the _while expression on line {lnum} is not type _bool", lnum)
    return val