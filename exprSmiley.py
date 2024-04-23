"""
    Pass in the portion of line that is the expression, which should be the rest of the 
    line (include the '.' token), the current variables list, and the line number lnum
    Ex.
    In the line 'b _is "The answer is: " + c + "." .' 
    a = ['b', '_is', '"The', 'answer', 'is:', '"', '+', 'c', '+', '"."', '.']
    pass in a[2:], which is: ['"The', 'answer', 'is:', '"', '+', 'c', '+', '"."', '.']
"""
def evalExpr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> int | bool | str:
    return expr(line, variables, lnum)[0]


"""
    Sorts through the expression token by token, sending the expression to the correct
    parsing function accordingly, returning the value of the entire expression as val,
    and the rest of the line that hasn't been evaluated as cur
"""
def expr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    val = None
    cur = None

    # Evaluate the left hand side expression
    if line[0] in {'-', '^'}:
        val, cur = unaryExpr(line, variables, lnum)
    elif line[0] in {'('}:
        val, cur = parenExpr(line, variables, lnum)
    else:
        val, cur = baseExpr(line, variables, lnum)

    # Evaluate the right hand side expression
    if len(cur) != 0 and cur[0] in {'*', '/', '%'}:
        val, cur = multiExpr(val, cur, variables, lnum)
    if len(cur) != 0 and cur[0] in {'+', '-'}:
        val, cur = addExpr(val, cur, variables, lnum)
    if len(cur) != 0 and cur[0] in {'!=', '<', '<=', '=', '>', '>='}:
        val, cur = compExpr(val, cur, variables, lnum)
    if len(cur) != 0 and cur[0] in {'&'}:
        val, cur = andExpr(val, cur, variables, lnum)
    if len(cur) != 0 and cur[0] in {'|'}:
        val, cur = orExpr(val, cur, variables, lnum)

    # Check that the expression has been terminated correctly
    if len(cur) != 0 and cur[0] != '.' and cur[0] != '_do' and cur[0] != '_then':
        raise SyntaxError(f"Token '{cur[0]}' on line {lnum} is an invalid operator")
    return val, cur


"""
    Parses and evaluates the unary expression
"""
def unaryExpr(line: list[str], variables: dict[str, list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    val = None
    cur = None
    if line[0] == '-':
        val, cur = expr(line[1:], variables, lnum)
        if not isinstance(val, int):
            raise TypeError(f"value '{val}' on line {lnum} is not an _int, and cannot be used with the '-' operator")
        val = -val
    elif line[0] == '^':
        val, cur = expr(line[1:], variables, lnum)
        if not isinstance(val, bool):
            raise TypeError(f"value '{val}' on line {lnum} is not a _bool, and cannot be used with the '^' operator")
        val = not val
    return val, cur


"""
    Parses and evaluates the expression inside the parentheses
"""
def parenExpr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    lineStr = (' ').join(line)[1:]
    parens = 1
    i = 0
    for char in lineStr:
        if parens == 0:
            break
        if char == ')':
            parens -= 1
        elif char == '(':
            parens += 1
        i += 1
    if parens != 0:
        raise SyntaxError(f"Missing parentheses on line {lnum}")
    return expr(lineStr[:i - 1].split(), variables, lnum)[0], lineStr[i:].split()


"""
    Parses and evaluates the base expression
"""
def baseExpr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    lenVal = 0
    val = None
    if line[0] in variables.keys():
        val = variables[line[0]][1]
        lenVal = len(line[0])
    elif line[0].isnumeric():
        val = validateInt(line[0], lnum)
        lenVal = len(line[0])
    elif line[0][0] == '"':
        val = validateStr((' ').join(line), lnum)
        lenVal = len(val) + 2
    elif line[0] in {':)', '(:', ':^)', '(^:', ':`)', '(`:', ':(', '):', ':^(', ')^:', ':`(', ')`:'}:
        val = validateBool(line[0], lnum)
        lenVal = len(line[0]) 
    else:
        raise ValueError(f"Token '{line[0]}' on line {lnum} is not a valid value")
    return val, (' ').join(line)[lenVal:].split()


"""
    Parses and evaluates the multiplication/division/mod expression
"""
def multiExpr(val: int, line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    cur = line.copy()
    lhs = val
    while len(cur) != 0 and cur[0] in {'*', '/', '%'}:
        op = cur[0]
        if cur[1] == '-':
            rhs, cur = unaryExpr(cur[1:], variables, lnum)
        elif cur[1] == '(':
            rhs, cur = parenExpr(cur[1:], variables, lnum)
        elif cur[1] != '.':
            rhs, cur = baseExpr(cur[1:], variables, lnum)
        else:
            break
        validateLR(op, lhs, rhs, lnum)
        if op == '*':
            lhs = lhs * rhs
        elif op == '/':
            if rhs == 0:
                lhs = 0
            else:
                lhs = lhs // rhs
        else:
            if rhs == 0:
                lhs = 0
            else:
                lhs = lhs % rhs
    return lhs, cur


"""
    Parses and evaluates the addition/subtraction expression
"""
def addExpr(val: int, line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    cur = line.copy()
    lhs = val
    while len(cur) != 0 and cur[0] in {'+', '-'}:
        op = cur[0]
        if cur[1] == '-':
            rhs, cur = unaryExpr(cur[1:], variables, lnum)
        elif cur[1] == '(':
            rhs, cur = parenExpr(cur[1:], variables, lnum)
        elif cur[1] != '.':
            rhs, cur = baseExpr(cur[1:], variables, lnum)
        else:
            break
        if len(cur) != 0 and cur[0] in {'*', '/', '%'}:
            rhs, cur = multiExpr(rhs, cur, variables, lnum)
        validateLR(op, lhs, rhs, lnum)
        if op == '+':
            if isinstance(lhs, str):
                lhs = lhs + str(rhs)
            else:
                lhs = lhs + rhs
        else:
            lhs = lhs - rhs
    return lhs, cur


"""
    Parses and evaluates the comparison expression
"""
def compExpr(val: int | str, line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    cur = line.copy()
    lhs = val
    while len(cur) != 0 and cur[0] in {'!=', '<', '<=', '=', '>', '>='}:
        op = cur[0]
        if cur[1] == '-':
            rhs, cur = unaryExpr(cur[1:], variables, lnum)
        elif cur[1] == '(':
            rhs, cur = parenExpr(cur[1:], variables, lnum)
        elif cur[1] != '.':
            rhs, cur = baseExpr(cur[1:], variables, lnum)
        else:
            break
        if len(cur) != 0 and cur[0] in {'*', '/', '%'}:
            rhs, cur = multiExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'+', '-'}:
            rhs, cur = addExpr(rhs, cur, variables, lnum)
        validateLR(op, lhs, rhs, lnum)
        if op == '!=':
            lhs = lhs != rhs
        elif op == '<':
            lhs = lhs < rhs
        elif op == '<=':
            lhs = lhs <= rhs
        elif op == '=':
            lhs = lhs == rhs
        elif op == '>':
            lhs = lhs > rhs
        else:
            lhs = lhs >= rhs
    return lhs, cur


"""
    Parses and evaluates the and expression
"""
def andExpr(val: bool, line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    cur = line.copy()
    lhs = val
    while len(cur) != 0 and cur[0] in {'&'}:
        op = cur[0]
        if cur[1] == '-':
            rhs, cur = unaryExpr(cur[1:], variables, lnum)
        elif cur[1] == '(':
            rhs, cur = parenExpr(cur[1:], variables, lnum)
        elif cur[1] != '.':
            rhs, cur = baseExpr(cur[1:], variables, lnum)
        else:
            break
        if len(cur) != 0 and cur[0] in {'*', '/', '%'}:
            rhs, cur = multiExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'+', '-'}:
            rhs, cur = addExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'!=', '<', '<=', '=', '>', '>='}:
            rhs, cur = compExpr(rhs, cur, variables, lnum)
        validateLR(op, lhs, rhs, lnum)
        lhs = lhs and rhs
    return lhs, cur


"""
    Parses and evaluates the or expression
"""
def orExpr(val: bool, line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    cur = line.copy()
    lhs = val
    while len(cur) != 0 and cur[0] in {'|'}:
        op = cur[0]
        if cur[1] == '-':
            rhs, cur = unaryExpr(cur[1:], variables, lnum)
        elif cur[1] == '(':
            rhs, cur = parenExpr(cur[1:], variables, lnum)
        elif cur[1] != '.':
            rhs, cur = baseExpr(cur[1:], variables, lnum)
        else:
            break
        if len(cur) != 0 and cur[0] in {'*', '/', '%'}:
            rhs, cur = multiExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'+', '-'}:
            rhs, cur = addExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'!=', '<', '<=', '=', '>', '>='}:
            rhs, cur = compExpr(rhs, cur, variables, lnum)
        if len(cur) != 0 and cur[0] in {'&'}:
            rhs, cur = andExpr(rhs, cur, variables, lnum)
        validateLR(op, lhs, rhs, lnum)
        lhs = lhs or rhs
    return lhs, cur


"""
    Validates int token
"""
def validateInt(i: str, lnum: int) -> int:
    try:
        val = int(i)
    except:
        raise TypeError(f"'{i}' at line {lnum} is not a valid _int value")
    return val


"""
    Validates bool token
"""
def validateBool(b: str, lnum: int) -> bool:
    if b in {':)','(:',':^)', '(^:', ':`)', '(`:'}:
        val = True
    elif b in {':(','):',':^(', ')^:', ':`(', ')`:'}:
        val = False
    else:
        raise Exception(f"'{b}' at line {lnum} is not a valid _bool value")
    return val


"""
    Validates str token
"""
def validateStr(s: str, lnum: int) -> str:
    if '"' in [*s] and '"' in [*s][1:]:
        val = s[s.index('"') + 1: s[1:].index('"') + 1]
    else:
        raise Exception(f"line {lnum} does not have a valid _str value")
    return val


"""
    Validates the type of val
"""
def validateVal(type: str, val: int | bool | str, lnum: int) -> None:
    raiseError = False
    if type == '_int' and not isinstance(val, int):
        raiseError = True
    if type == '_bool' and not isinstance(val, bool):
        raiseError = True
    if type == '_str' and not isinstance(val, str):
        raiseError = True
    if raiseError:
        raise TypeError(f'Value {val} on line {lnum} is not type {type}')
    

"""
    Validates the left hand side value and the right hand side value of the operator token
"""
def validateLR(op: str, lhs: int | bool | str, rhs: int | bool | str, lnum: int) -> None:
    raiseError = False
    val = None
    type = None
    if op in {'+', '-', '*', '/', '%', "<", "<=", ">", ">="}:
        if op == '+' and isinstance(lhs, str):
            return
        elif not isinstance(lhs, int):
            raiseError = True
            val = lhs
        elif not isinstance(rhs, int):
            raiseError = True
            val = rhs
        type = '_int'
    if op in {"!=", "=="}:
        return
    if op in {"|", "&"}:
        if not isinstance(lhs, bool):
            raiseError = True
            val = lhs
        elif not isinstance(rhs, bool):
            raiseError = True
            val = rhs
        type = '_bool'
    if raiseError:
        print(f"lhs: {lhs}, rhs: {rhs}")
        raise TypeError(f"Value {val} on line {lnum} cannot be used with '{op}' not type {type}")
 
    
"""
    Validates that a constant or variable has been declared
"""
def validateName(name: str, variables: dict[str,  list[int | bool | str | None]]) -> bool:
    if name not in variables.keys():
        return False
    return True