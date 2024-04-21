from exprSmiley import baseExpr, validateVal, evalExpr

def declarest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <declare st> ::= <type> <var id> . | <type> <const id> _is <literal> .
    var = variables.copy()
    if len(line) < 3:
        if line[1][0].islower():
            if line[2] == '_is':
                raise TypeError(f"Variable '{line[1]}' at line {lnum} cannot be assigned at declaration")
        raise SyntaxError(f"Declare statement syntax at line {lnum} is incorrect")
    if line[-1] != '.':
        raise SyntaxError(f"Line {lnum} not terminated with '.'")
    if line[1][0].islower():
        if line[2] == '_is':
            raise TypeError(f"Variable '{line[1]}' at line {lnum} cannot be assigned at declaration")
        var[line[1]] = [line[0], None]
    elif line[1][0].isupper():
        val = baseExpr(line[3:], var, lnum)[0] # This ensures that the constant is declared with a literal
        validateVal(line[0], val, lnum)
        var[line[1]] = ['const ' + line[0], val]
    return var 

def assignst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <assign st> ::= <var id> _is <expr> . | <var id> ++ . | <var id> += <expr> .
    var = variables.copy()
    if len(line) < 3:
        raise SyntaxError(f"Assign statement syntax at line {lnum} is incorrect")
    if line[1] == '_is':
        # Checks if the variable type is a constant
        if len(var[line[0]][0]) > 5:
            raise TypeError(f"Constant {line[0]} of type {var[line[0]][0]} on line {lnum} cannot be reassigned.")
        val = evalExpr(line[2:], variables, lnum) # Passes <expr> and outputs value of the entire expression
        validateVal(var[line[0]][0], val, lnum) # Checks that the type of the variable matches the type of the value
        var[line[0]][1] = val # Assigns value to variable now that the value has been validated
    elif line[1] == '++':
        if var[line[0]][0] == '_int':
            if var[line[0]][1] is None:
                raise NameError(f"Variable '{line[0]}' at line {lnum} hasn't been initialized yet")
            var[line[0]][1] += 1
        elif var[line[0]][0] == 'const _int':
            raise TypeError(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise TypeError(f"Operation '++' at line {lnum} is invalid for {var[line[0]][0]} types")
    elif line[1] == '+=':
        if var[line[0]][0] == '_int':
            if var[line[0]][1] is None:
                raise NameError(f"Variable '{line[0]}' hasn't been initialized yet")
            val = evalExpr(line[2:], variables, lnum)
            validateVal(var[line[0]][0], val, lnum)
            var[line[0]][1] += val
        elif var[line[0]][0] == 'const _int':
            raise TypeError(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise TypeError(f"Operation '+=' at line {lnum} is invalid for {var[line[0]][0]} types")
    return var

def read(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> dict[
    str, list[int | bool | str | None]]:

    # <read st> ::= _read <var id> .

    var = variables.copy()

    if len(line) != 3:
        raise Exception(f"Read statement syntax at line {lnum} is incorrect")
    if line[-1] != '.':
        raise Exception(f"Line {lnum} not terminated with '.'")
    if line[1][0].isupper():
        raise Exception(f"Variable at line {lnum} can not begin with uppercase")
    if len(var[line[1]][0]) > 5:
        raise TypeError(f"Constant {line[0]} of type {var[line[0]][0]} on line {lnum} cannot be reassigned.")

    val = evalExpr(input().strip().split(), variables, lnum)
    validateVal(var[line[1]][0], val, lnum)
    var[line[1]][1] = val

    return var

def printst(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> None:
    # <print st> ::= _writeline <expr> . | _write <expr> .
    if len(line) < 3:
        raise Exception(f"Print statement syntax at line {lnum} is incorrect")
    if line[-1] != '.':
        raise Exception(f"Line {lnum} not terminated with '.'")
    val = evalExpr(line[1:], variables, lnum)
    if line[0] == '_write':
        print(val, end='')
    elif line[0] == '_writeline':
        print(val)

def ifst(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <if st> ::= _if <expr> _then { <statement> } | _if <expr> _then { <statement> } <else>
    if len(line) < 4:
        if '_then' not in line:
            raise SyntaxError(f"Missing '_then' in line {lnum}")
        elif '{' not in line:
            raise SyntaxError(f"Missing '{{' in line {lnum}")
        else:
            raise SyntaxError(f"Missing expression in line {lnum}")
    if line[2] != '_then':
        raise SyntaxError(f"Missing '_then' in line {lnum}")
    if line[-1] != '{':
        raise SyntaxError(f"Missing'{{' in line {lnum}")
    val = evalExpr(line[1:], variables, lnum)
    if not isinstance(val, bool):
        raise TypeError(f"Value of the _if expression on line {lnum} is not type _bool")
    return val

def elsest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <else> ::= _else { <statement> } | _elseif <expr> _then { <statement> } | _elseif <expr> _then { <statement> } <else>
    pass

def whilest(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> bool:
    # <while st> ::= _while <expr> _do { <statement> }
    pass