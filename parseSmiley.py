def declare(line: list[str]) -> None:
    # <declare st> ::= <type> <var id> . | <type> <const id> _is <literal> .
    # if line[1] starts with lowercase then variables[line[0]] = None
    # if line[1] starts with uppercase
    #   if line[2] == '_is'
    #       if type of line[3] is what line[0] says 
    #           variables[line[0]] = line[3]
    # if line[4] != '.'
    #   throw error
    # else throw error
    pass 