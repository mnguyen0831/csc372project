def declare(line: list[str], variables: dict[str, list[str, bool | int | str]], lnum: int) -> dict[str, list[str, bool | int | str]]:
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
        if line[2] != '_is':
            raise Exception(f"Constant {line[1]} at line {lnum} must be assigned at declaration")
        if len(line) != 5:
            raise Exception(f"Declare statement syntax at line {lnum} is incorrect")
        if line[0] == '_int':
            try:
                val = int(line[3])
            except:
                raise Exception(f"'{line[3]}' at line {lnum} is not a valid int value")
            else:
                var[line[1]] = ['const ' + line[0], val]
        elif line[0] == '_bool':
            if line[3] in {':)','(:',':^)', '(^:', ':`)', '(`:'}:
                val = True
            elif line[3] in {':(','):',':^(', ')^:', ':`(', ')`:'}:
                val = False
            else:
                raise Exception(f"'{line[3]}' at line {lnum} is not a valid boolean value")
            var[line[1]] = ['const ' + line[0], val]
        else:
            var[line[1]] = ['const ' + line[0], line[3]]
    return var 

def assign(line: list[str], variables: dict[str, list[str, bool | int | str]], lnum: int) -> dict[str, list[str, bool | int | str]]:
    # <assign st> ::= <var id> _is <expr> . | <var id> ++ . | <var id> += <expr> .
    var = variables.copy()
    if len(line) < 3:
        raise Exception(f"Assign statement syntax at line {lnum} is incorrect")
    if line[1] == '_is':
        if len(line[0][0]) > 5:
            raise Exception(f"Constant {line[0]} of type {var[line[0]][0]} on line {lnum} cannot be reassigned.")
        var[line[0]][1] = expr(var[line[0]][0], line[2:], var, lnum)
    elif line[1] == '++':
        if var[line[0]][0] == '_int':
            if var[line[0]][1] is None:
                raise Exception(f"Variable '{line[0]}' hasn't been initialized yet")
            var[line[0]][1] += 1
        elif var[line[0]][0] == 'const _int':
            raise Exception(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise Exception(f"Operation '++' at line {lnum} is invalid for {var[line[0]][0]} types")
    elif line[1] == '+=':
        if var[line[0]][0] == '_int':
            if var[line[0]][1] is None:
                raise Exception(f"Variable '{line[0]}' hasn't been initialized yet")
            pass # var[line[0]][1] += expr(line[2:], variables)
        elif var[line[0]][0] == 'const _int':
            raise Exception(f"Constant '{line[0]}' at line {lnum} cannot be reassigned")
        else:
            raise Exception(f"Operation '+=' at line {lnum} is invalid for {var[line[0]][0]} types")
    return var
        
# Pass in the type expected (_int, _str, _bool), the portion of line that is the expression, which should be the 
# rest of the line (include the '.' token), the current variables list, and the line number lnum
def expr(type: str, line: list[str], variables: dict[str, list[str, bool | int | str]], lnum: int) -> str | int | bool:
    print("Entered Expression")
    if type == '_int':
        return int(line[0])
    elif type == '_str':
        return line[0]
    elif type == '_bool':
        if line[0] in {':)','(:',':^)', '(^:', ':`)', '(`:'}:
            return True
        elif line[0] in {':(','):',':^(', ')^:', ':`(', ')`:'}:
            return False
    return None