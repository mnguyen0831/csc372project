import parseSmiley as smile
import argparse

repl: str
input_file: str
print_vars: bool
program: list[list[str]]
variables: dict[str, list[str, bool | int | str]] # key: id, val: [type, value], types are {'_int', '_bool', '_str', 'const _int', 'const _bool', 'const _str}
cur_line: int # The current line of code that the program is on

# Files can be run using:
# python runSmiley.py --input-file 'sample.;]'
# python runSmiley.py --repl

def main() -> None:
    global repl, input_file, program, variables, print_vars, cur_line
    variables = dict()
    cur_line = 1
    getInput()
    if repl:
        lineIn()
    elif len(input_file) > 0:
        program = scanSmiley(input_file)
        while cur_line - 1 < len(program):
            execute(program[cur_line - 1])
    if print_vars:
        printVars()

def printVars() -> None:
    global variables
    print("\nVariables:\n----------")
    for var in variables.keys():
        print(f"{var} : {variables[var]}")   

def getInput() -> None:
    global repl, input_file, print_vars
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--repl', action='store_true', help='Line to run')
    parser.add_argument('--input-file', type=str, default='', help='File name to run')
    parser.add_argument('--vars', action='store_true', help='Prints out Variable Dictionary')
    args = parser.parse_args()
    repl = args.repl
    input_file = args.input_file
    print_vars = args.vars

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
        tokens.append(line.split())
    return tokens

def execute(line: list[str]) -> None:
    global program, variables, cur_line
    print(f"Executing line {cur_line}: {program[cur_line - 1]}")
    if len(line) == 0:
        cur_line += 1
        return
    if line[0] in {'$', '}'}:
        cur_line += 1
        return
    if '$' in line:
        line = line[:line.index('$') + 1]
    elif '.' not in line and '{' not in line and '}' not in line:
        raise Exception(f"Line {cur_line} is not properly terminated")
    if line[0] in {'_int', '_str', '_bool'}:
        variables = smile.declarest(line, variables, cur_line)
    elif line[0] in variables.keys():
        variables = smile.assignst(line, variables, cur_line)
    elif line[0] == '_read':
        variables = smile.readst(line, variables, cur_line)
    elif line[0] in {'_write', '_writeline'}:
        smile.printst(line, variables, cur_line)
    elif line[0] in {'_if'}: # Handle closing bracket and elifs in ifFlow()
        ifFlow(line)
    elif line[0] in {'_while'}: # Handle closing bracket in whileFlow()
        pass #whileFlow
        variables = smile.read(line, variables, cur_line)
    else:
        if line[0].isnumeric() or line[0][0] == '_' or line[0][0].isupper():
            raise NameError(f"'{line[0]}' at line {cur_line} is an invalid name for a variable")
        else:
            raise NameError(f"Variable '{line[0]}' at line {cur_line} hasn't been declared")
    cur_line += 1

def lineIn():
    print('Welcome to the .;] input REPL.\nTo exit, input: "_exit ."\nTo see existing variables, input: "_vars ."')
    while True:
        userIn = input("\( '3'){ ").strip()
        if userIn == '_exit .':
            break
        elif userIn == '_vars .':
            printVars()
            continue
        try:
            execute(userIn.split())
        except NameError:
            print("The variable you attempted to use has not been initialized. Please try again.")
        except SyntaxError:
            print("Something in your syntax was invalid. Please try again.")
        except TypeError:
            print("The input expression does not match the type expected. Please try again.")
        except ValueError:
            print("An input value is invalid. Please try again.")
        except Exception:
            print("The input line was invalid. Please try again.")

# If flow walks through the if structure
def ifFlow(line):
    global program, variables, cur_line
    val = smile.ifst(line, variables, cur_line)
    end, branches = getIfStructure(cur_line)
    if val:
        cur_line += 1
        while cur_line < branches[0]:
            execute(program[cur_line - 1])
            cur_line += 1
        cur_line -= 1
    else:
        for i in range(len(branches)):
            cur_line = branches[i]
            val = smile.elsest(program[cur_line - 1], variables, cur_line)
            if val:
                cur_line += 1
                if len(branches) == i + 1:
                    endLine = end
                else:
                    endLine = branches[i + 1]
                while cur_line < endLine:
                    execute(program[cur_line - 1])
                    cur_line += 1
                break
    cur_line = end - 1

# Finds structure of if statement
# [0] is the line number of the final }
# [1] is a list of all of the line numbers of the elif/else branches of the if statement
def getIfStructure(start: int) -> tuple[int, list[int]]:
    global program
    branches: list[int] = list()
    cur = start + 1
    while True:
        if len(program[cur - 1]) > 0:
            if len(program[cur - 1]) > 2:
                if program[cur - 1][0] == '}':
                    if program[cur - 1][1] == '_elseif':
                        branches.append(cur)
                    elif program[cur - 1][1] == '_else':
                        branches.append(cur)
                elif program[cur - 1][0] == '_if':
                    cur = getIfStructure(cur)[0] + 1
            if len(program[cur - 1]) == 1:
                if program[cur - 1][0] == '}':
                    end = cur - 1
                    break
        cur += 1
    end = cur
    return end, branches

def whileFlow():
    pass

def getWhileStructure():
    pass

if __name__ == "__main__":
    main()