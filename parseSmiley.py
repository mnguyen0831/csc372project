def declare(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
    # <declare st> ::= <type> <var id> . | <type> <const id> _is <literal> .
    var = variables.copy()
    if len(line) < 3:
        if line[1][0].islower():
            if line[2] == '_is':
                raise Exception(f"Variable '{line[1]}' at line {lnum} cannot be assigned at declaration")
        raise Exception(f"Declare statement syntax at line {lnum} is incorrect")
    if line[-1] != '.':
        raise Exception(f"Line {lnum} not terminated with '.'")
    if line[1][0].islower():
        var[line[1]] = [line[0], None]
    elif line[1][0].isupper():
        val = baseExpr(line[3:], var, lnum)[0] # This ensures that the constant is declared with a literal
        validateVal(line[0], val, lnum)
        var[line[1]] = ['const ' + line[0], val]
    return var 

def assign(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> dict[str,  list[int | bool | str | None]]:
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
                raise Exception(f"Variable '{line[0]}' at line {lnum} hasn't been initialized yet")
            var[line[0]][1] += 1
        elif var[line[0]][0] == 'const _int':
            raise Exception(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise Exception(f"Operation '++' at line {lnum} is invalid for {var[line[0]][0]} types")
    elif line[1] == '+=':
        if var[line[0]][0] == '_int':
            if var[line[0]][1] is None:
                raise Exception(f"Variable '{line[0]}' hasn't been initialized yet")
            val = evalExpr(line[2:], variables, lnum)
            validateVal(var[line[0]][0], val, lnum)
            var[line[0]][1] += val
        elif var[line[0]][0] == 'const _int':
            raise Exception(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise Exception(f"Operation '+=' at line {lnum} is invalid for {var[line[0]][0]} types")
    return var

#####################    EXPRESSIONS    ###########################################################################################################

# Pass in the portion of line that is the expression, which should be the 
# rest of the line (include the '.' token), the current variables list, and the line number lnum
# ex.
# In the line 'b _is "The answer is: " + c + "." .' 
# a = ['b', '_is', '"The', 'answer', 'is:', '"', '+', 'c', '+', '"."', '.']
# pass in a[2:], which is: ['"The', 'answer', 'is:', '"', '+', 'c', '+', '"."', '.']
def evalExpr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> int | bool | str:
    return expr(line, variables, lnum)[0]

def expr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    val = None
    cur = None
    if line[0] in {'-', '^'}:
        val, cur = unaryExpr(line, variables, lnum)
    elif line[0] in {'('}:
        val, cur = parenExpr(line, variables, lnum)
    else:
        val, cur = baseExpr(line, variables, lnum)
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
    if len(cur) != 0 and cur[0] != '.' and cur[0] != '_do':
        raise ValueError(f"Token '{cur[0]}' on line {lnum} is an invalid operator")
    return val, cur

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
        raise Exception(f"Missing parentheses on line {lnum}")
    return expr(lineStr[:i - 1].split(), variables, lnum)[0], lineStr[i:].split()

def baseExpr(line: list[str], variables: dict[str,  list[int | bool | str | None]], lnum: int) -> tuple[str | int | bool, list[str]]:
    lenVal = 0
    val = None
    if line[0] in variables.keys():
        return variables[line[0]][1]
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
            lhs = lhs // rhs
        else:
            lhs = lhs % rhs
    return lhs, cur

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

def validateInt(i: str, lnum: int) -> int:
    try:
        val = int(i)
    except:
        raise TypeError(f"'{i}' at line {lnum} is not a valid _int value")
    return val

def validateBool(b: str, lnum: int) -> bool:
    if b in {':)','(:',':^)', '(^:', ':`)', '(`:'}:
        val = True
    elif b in {':(','):',':^(', ')^:', ':`(', ')`:'}:
        val = False
    else:
        raise Exception(f"'{b}' at line {lnum} is not a valid _bool value")
    return val

def validateStr(s: str, lnum: int) -> str:
    if '"' in [*s] and '"' in [*s][1:]:
        val = s[s.index('"') + 1: s[1:].index('"') + 1]
    else:
        raise Exception(f"line {lnum} does not have a valid _str value")
    return val

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