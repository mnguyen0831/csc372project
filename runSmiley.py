import parseSmiley as smile
from exprSmiley import raiseErr
import argparse


"""
    Command line flags
"""
input_file: str
repl: str
print_vars: bool
print_flow: bool


"""
    The list of all of the lines in the input program, where each line is split by 
    whitespace.
    Ex. program[i] = ['token1', 'token2', 'token3', '.']
"""
program: list[list[str]]


"""
    The current line of code that the program is on. It corresponds to the
    index cur_line - 1 in the 'program' global variable.
"""
cur_line: int


"""
    List of variables that exist in the program.
    key: id
    val: [type, value]
    type can be {'_int', '_bool', '_str', 'const _int', 'const _bool', 'const _str}
"""
variables: dict[str, list[str, bool | int | str]]


"""
    Files can be run using:
    python runSmiley.py --file 'sample.;]'

    Flags:
    --file [file-name]
        Opens, parses, and executes the file named 'file-name'. The file extension does
        not matter.
    --repl
        Opens up the Smiley REPL. If used with --file, the file will be executed 
        first, then the REPL will open and use the variable pool from the previously
        executed program.
    --vars
        Prints the final list of variables after both the program and REPL have 
        finished executing.
    --print-flow
        Prints the line number and the tokenized line of each line as it is executed. 
"""
def main() -> None:
    global repl, input_file, program, variables, print_vars, cur_line
    variables = dict()
    cur_line = 1
    getInput()
    if len(input_file) > 0:
        program = scanSmiley(input_file)
        while cur_line - 1 < len(program):
            execute(program[cur_line - 1])
    if repl:
        lineIn()
    if print_vars:
        printVars()


"""
    Prints all of the existing variables, their types, and their values.
"""
def printVars() -> None:
    global variables
    print("\nVariables:\n----------")
    for var in variables.keys():
        type: str = variables[var][0]
        val: int | str | bool = variables[var][1]
        print(f"{type} {var} _is {val}")
    print()


"""
    Grabs all of the command line arguments that were used with runSmiley.py, and 
    assigns the global variables accordingly.
"""
def getInput() -> None:
    global repl, input_file, print_vars, print_flow
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--file', type=str, default='', help='File name to run')
    parser.add_argument('--repl', action='store_true', help='Opens REPL')
    parser.add_argument('--vars', action='store_true', help='Prints out variable dictionary')
    parser.add_argument('--print-flow', action='store_true', help='Prints out the flow of the program')
    args = parser.parse_args()
    repl = args.repl
    input_file = args.file
    print_vars = args.vars
    print_flow = args.print_flow


"""
    Scans in the input file name, and stores it into the global program variable. 
    Does not store any comments into the program variable.
"""
def scanSmiley(fname: str) -> list[list[str]]:
    try:
        file = open(fname, 'r')
    except FileNotFoundError:
        print(f"File '{fname}' does not exist")
        lines = []
    else:
        print(f"Open: '{fname}'")
        lines = file.readlines()
    tokens: list[list[str]] = list()

    for line in lines:
        tokens.append(line.strip().split())
    return tokens


"""
    Sends the input line to the correct parsing function, which also executes the line.
    Increments the cur_line as well.
"""
def execute(line: list[str]) -> None:
    global program, variables, cur_line, print_flow
    if print_flow and cur_line != 0:
        print(f"Executing line {cur_line}: {program[cur_line - 1]}")
    
    # Ignore comment
    if '$' in line:
        line = line[:line.index('$')]

    # Empty line
    if len(line) == 0:
        cur_line += 1
        return

    # Check that the line contains a proper line terminator
    if '.' not in line and '{' not in line and '}' not in line:
        raiseErr(f"SyntaxError: Line {cur_line} is not properly terminated", cur_line)

    # Pass line along to the appropriate parsing and execution function
    if line[0] in {'_int', '_str', '_bool'}:
        variables = smile.declarest(line, variables, cur_line)
    elif line[0] in variables.keys():
        variables = smile.assignst(line, variables, cur_line)
    elif line[0] == '_read':
        variables = smile.readst(line, variables, cur_line)
    elif line[0] in {'_write', '_writeline'}:
        smile.printst(line, variables, cur_line)
    elif line[0] in {'_if'}:
        ifFlow(line)
    elif line[0] in {'_while'}:
        whileFlow(line)
    elif line[0] in {'}'}:
        pass
    else:
        if line[0].isnumeric() or line[0][0] == '_' or line[0][0].isupper():
            raiseErr(f"NameError: '{line[0]}' at line {cur_line} is an invalid name for a variable", cur_line)
        else:
            raiseErr(f"NameError: Variable '{line}' at line {cur_line} hasn't been declared", cur_line)
    cur_line += 1


"""
    Starts up the REPL. If the REPL is used in tandem with an input file, the REPL will
    use the variable list from the input file. If not, the REPL will begin with an
    empty variable list.
"""
def lineIn() -> None:
    global cur_line
    print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('|   Welcome to the .;] input REPL.                |')
    print('|   To exit, input: "_exit ."                     |')
    print('|   To see existing variables, input: "_vars ."   |')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    while True:
        cur_line = 0
        userIn = input("s( '3'){ ").strip()
        valid = True
        if userIn == '_exit .':
            break
        elif userIn == '_vars .':
            printVars()
            continue
        for statement in {'_if', '_while', '_elseif', '_else'}:
            if statement in userIn.split():
                print("\t_if statements, and _while statements are unsupported in the REPL. Please try again.")
                valid = False
                break
        if not valid:
            continue
        try:
            execute(userIn.split())
        except Exception:
            pass # Exception is printed out by parser


"""
    ifFlow walks the program through the _if structure, returning to the main function
    once the _if structure has ended, updating the cur_line variable to the line number
    of the final bracket in the _if structure. 
"""
def ifFlow(line) -> None:
    global program, variables, cur_line

    # Validate the _if syntax, and evaluate the expression
    val = smile.ifst(line, variables, cur_line)

    # Pull out all of the line numbers for the _elseifs, and _else
    end, branches = getIfStructure(cur_line)

    # Execute first _then if the _if expr is True
    if val:
        cur_line += 1
        if len(branches) > 0:
            endBranch = branches[0]
        else:
            endBranch = end     
        while cur_line < endBranch:
            execute(program[cur_line - 1])

    # Iterate through the _elseif exprs and execute that branch if True
    else:
        for i in range(len(branches)):
            cur_line = branches[i]

            # Validate the _elseif syntax, and evaluate the expression
            conditionIsTrue = smile.elsest(program[cur_line - 1], variables, cur_line)
            if conditionIsTrue:
                cur_line += 1
                if len(branches) == i + 1:
                    endBranch = end
                else:
                    endBranch = branches[i + 1]
                while cur_line < endBranch:
                    execute(program[cur_line - 1])
                break # Jump to end of _if structure
    cur_line = end - 1


"""
    Given the line number of the _if statement, returns the line number of the final
    '}' that signifies the end of the structure, as well as a list of all of the line
    numbers of the '_elseif', and '_else' statements.
"""
def getIfStructure(start: int) -> tuple[int, list[int]]:
    global program
    branches: list[int] = list()

    # Begin at the first line in the _if structure past the _if statement
    cur = start + 1
    
    # Iterate through the program to find the end of the _if structure
    while True:
        if len(program[cur - 1]) > 0:

            # Record all of the branches of the _if structure
            if len(program[cur - 1]) > 2:
                if program[cur - 1][0] == '}':
                    if program[cur - 1][1] == '_elseif':
                        branches.append(cur)
                    elif program[cur - 1][1] == '_else':
                        branches.append(cur)

                # Skip past this nested _if structure
                elif program[cur - 1][0] == '_if':
                    cur = getIfStructure(cur)[0] + 1
                    continue

                # Skip past this nested _while structure
            if program[cur - 1][0] == '_while':
                cur = getWhileStructure(cur)
                continue

            # Locate the final '}' of the _if structure
            if len(program[cur - 1]) == 1:
                if program[cur - 1][0] == '}':
                    end = cur - 1
                    break
        cur += 1
        if cur == len(program) + 1:
            raiseErr(f"SyntaxError: _if structure beginning at line {cur_line} was not terminated", cur_line)
    end = cur
    return end, branches


'''
    whileFlow walks through the _while structure that begins on the input line, 
    returning to the main function once the _while structure has been exited, updating
    the cur_line variable to the line number after the structure's closing bracket
'''
def whileFlow(line) -> None:
    global program, variables, cur_line
    val = smile.whilest(line, variables, cur_line)
    end = getWhileStructure(cur_line)
    start = cur_line + 1

    # Execute the statements in the while loop, and reevaluate the condition
    while val:
        cur_line = start
        while cur_line < end:
            execute(program[cur_line-1])
        val = smile.whilest(line, variables, cur_line)


'''
    Returns the line number of the closing '}' for the while structure that begins on
    line start
'''
def getWhileStructure(start: int) -> int:
    global program
    brackets = 1
    cur = start

    # Get the line number of the '}' belonging to the while structure on line start - 1
    while brackets > 0:
        if '{' in program[cur]:
            brackets += 1
        if '}' in program[cur]:
            brackets -= 1
        cur += 1
    return cur


if __name__ == "__main__":
    main()