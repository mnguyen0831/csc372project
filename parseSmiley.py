from exprSmiley import evalExpr, baseExpr, validateVal, validateName

def declarest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <declare st> ::= <type> <var id> . | <type> <const id> _is <literal> .
    var = variables.copy()
    if '.' not in line:
        raise SyntaxError(f"Declaration of '{line[1]}' on line {lnum} not terminated with '.'")
    if line[-1] != '.':
        raise SyntaxError(f"Declaration of '{line[1]}' on line {lnum} not terminated with '.'")
    if len(line) < 2:
        raise SyntaxError(f"Declaration statement on line '{lnum}' does not indicate a variable to declare")
    name = line[1]
    if name[0].islower():
        if '_is' in line:
            raise TypeError(f"Variable '{name}' on line {lnum} cannot be assigned at declaration")
        if len(line) > 3:
            raise SyntaxError(f"Declaration of variable '{name}' on line {lnum} can only contain the type and name")
        var[name] = [line[0], None]
    elif name[0].isupper():
        if '_is' not in line:
            raise SyntaxError(f"Constant '{name}' declaration on line {lnum} must be followed immediately by '_is'")
        if line[2] != '_is':
            raise SyntaxError(f"Constant '{name}' declaration on line {lnum} must be followed immediately by '_is'")
        if len(line) < 5:
            raise SyntaxError(f"Constant '{name}' declaration on line {lnum} must be declared with a literal of type {line[0]}")
        val = baseExpr(line[3:], var, lnum)[0]
        type = line[0]
        if type == '_int':
            if not isinstance(val, int):
                raise TypeError(f"Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}")
        elif type == '_bool':
            if not isinstance(val, bool):
                raise TypeError(f"Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}")
        elif type == '_str':
            if not isinstance(val, str):
                raise TypeError(f"Constant '{name}' on line {lnum} cannot be assigned the value '{val}' since it is not a type {type}")
        var[name] = ['const ' + type, val]
    else:
        raise NameError(f"'{name}' on line {lnum} is not a valid name")
    return var 


def assignst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <assign st> ::= <var id> _is <expr> . | <var id> ++ . | <var id> += <expr> .
    var = variables.copy()
    name = line[0]
    if '.' not in line:
        raise SyntaxError(f"Assignment of '{name}' on line {lnum} not terminated with '.'")
    if line[-1] != '.':
        raise SyntaxError(f"Assignment of '{name}' on line {lnum} not terminated with '.'")
    if '_is' not in line and '++' not in line and '+=' not in line:
        raise SyntaxError(f"Assignment of '{name}' on line {lnum} is missing an assignment operator")
    if not validateName(name, variables):
        raise NameError(f"Variable '{name}' on line {lnum} must be declared before assignment")
    type = var[name][0]
    curVal = var[name][1]
    if len(type) > 5:
        raise TypeError(f"Constant '{name}' of type {type} on line {lnum} cannot be reassigned.")
    if line[1] == '_is':
        val = evalExpr(line[2:], variables, lnum)
        validateVal(type, val, lnum)
        var[name][1] = val
    elif line[1] == '++':
        if type == '_int':
            if curVal is None:
                raise NameError(f"Variable '{name}' on line {lnum} cannot be incremented since it hasn't been initialized yet")
            var[name][1] += 1
        else:
            raise TypeError(f"Operation '++' on line {lnum} is invalid for {type} types")
    elif line[1] == '+=':
        if type == '_int':
            if curVal is None:
                raise NameError(f"Variable '{name}' on line {lnum} cannot be added to since it hasn't been initialized yet")
            val = evalExpr(line[2:], variables, lnum)
            validateVal(type, val, lnum)
            var[name][1] += val
        elif type == '_str':
            if curVal is None:
                raise NameError(f"Variable '{name}' on line {lnum} cannot be added to since it hasn't been initialized yet")
            val = evalExpr(line[2:], variables, lnum)
            validateVal(type, val, lnum)
            var[name][1] += val
        else:
            raise TypeError(f"Operation '+=' on line {lnum} is invalid for {type} types")
    return var


def readst(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> dict[str, list[int | bool | str | None]]:
    # <read st> ::= _read <var id> .
    var = variables.copy()
    if '.' not in line:
        raise SyntaxError(f"_read statement on line {lnum} not terminated with '.'")
    if line[-1] != '.':
        raise SyntaxError(f"_read statement on line {lnum} not terminated with '.'")
    if len(line) != 3:
        raise SyntaxError(f"_read statement on line {lnum} should only contain the variable name")
    if line[1] not in var.keys():
        raise NameError(f"Variable '{line[1]}' in the _read statement on line {lnum} has not been declared")
    if len(var[line[1]][0]) > 5:
        raise TypeError(f"Constant '{line[0]}' of type {var[line[0]][0]} in the _read statement on line {lnum} cannot be reassigned.")
    
    val: int | bool | str
    while True:
        try:
            val = input().strip().split()
            val = evalExpr(val, variables, lnum)
            validateVal(var[line[1]][0], val, lnum)
        except Exception:
            print(f"The value '{val}' is not a valid {var[line[1]][0]} type")
            print('Examples of valid inputs:')
            print("\tint: - 3")
            print('\tstr: "String"')
            print("\tbool: ^ :)")
            print("Note that all operators must be separated from the operands with whitespace")
            print("Please try again")
        else:
            break
    var[line[1]][1] = val
    return var


def printst(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> None:
    # <print st> ::= _writeline <expr> . | _write <expr> .
    if '.' not in line:
        raise SyntaxError(f"{line[0]} statement on line {lnum} not terminated with '.'")
    if line[-1] != '.':
        raise SyntaxError(f"{line[0]} statement on line {lnum} not terminated with '.'")
    if len(line) < 3:
        raise SyntaxError(f"{line[0]} statement on line {lnum} must contain an expression")
    val = evalExpr(line[1:], variables, lnum)
    if line[0] == '_write':
        print(val, end='')
    elif line[0] == '_writeline':
        print(val)


def ifst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <if st> ::= _if <expr> _then { <statement> } | _if <expr> _then { <statement> } <else>
    if '_then' not in line:
        raise SyntaxError(f"_if statment in line {lnum} must have '_then' following the expression")
    if '{' not in line:
        raise SyntaxError(f"_if statement must have '{{' at the end of line {lnum}")
    if line[-1] != '{':
        raise SyntaxError(f"_if statement '{{' at the end of line {lnum}")
    if line[-2] != '_then':
        raise SyntaxError(f"'_then' in line {lnum} must immediately precede '{{'")
    if len(line) < 4:
        raise SyntaxError(f"_if statement on line {lnum} must contain a _bool expression")
    val = evalExpr(line[1:], variables, lnum)
    if not isinstance(val, bool):
        raise TypeError(f"Value of the _if expression on line {lnum} is not type _bool")
    return val


def elsest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <else> ::= _else { <statement> } | _elseif <expr> _then { <statement> } | _elseif <expr> _then { <statement> } <else>
    if '{' not in line:
        raise SyntaxError(f"Missing '{{' at the end of line {lnum}")
    if line[-1] != '{':
        raise SyntaxError(f"Missing '{{' at the end of line {lnum}") 
    if '_else' not in line and '_elseif' not in line:
        raise SyntaxError(f"Missing '_else' or '_elseif' in line {lnum}")
    if '_else' in line:
        if line[1] != '_else':
            raise SyntaxError(f"'_else' on line {lnum} must immediately follow '}}")
        if len(line) != 3:
            raise SyntaxError(f"_else statement on line {lnum} cannot have an expression")
    elif '_elseif' in line:
        if line[1] != '_elseif':
            raise SyntaxError(f"'_elseif' on line {lnum} must immediately follow '}}'")
        if '_then' not in line:
            raise SyntaxError(f"Missing '_then' following the expression on line {lnum}")
        if line[-2] != '_then':
            raise SyntaxError(f"'_then' on line {lnum} must immediately precede '{{'")
        if len(line) < 5:
            raise SyntaxError(f"_elseif statement on line {lnum} must contain a _bool expression")
        val = evalExpr(line[2:], variables, lnum)
        if not isinstance(val, bool):
            raise TypeError(f"Value of the _elseif expression on line {lnum} is not type _bool")
        return val
    return False


def whilest(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> bool:
    # <while st> ::= _while <expr> _do { <statement> }
    if '{' not in line:
        raise SyntaxError(f"Missing '{{' at the end of line {lnum}")
    if line[-1] != '{':
        raise SyntaxError(f"Missing '{{' at the end of line {lnum}") 
    if '_do' not in line:
        raise SyntaxError(f"Missing '_do' after the expression in line {lnum}")
    if line[-2] != '_do':
            raise SyntaxError(f"Missing '_do' after the expression in line {lnum}")
    if len(line) < 4:
        raise SyntaxError(f"_while statement on line {lnum} must contain a _bool expression")
    val = evalExpr(line[1:], variables, lnum)
    if not isinstance(val, bool):
        raise TypeError(f"Value of the _while expression on line {lnum} is not type _bool")
    return val