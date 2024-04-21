import parseSmiley as smile
import argparse

repl: str
input_file: str
print_vars: bool
program: list[list[str]]
variables: dict[str, list[str, bool | int | str]] # key: id, val: [type, value], types are {'_int', '_bool', '_str', 'const _int', 'const _bool', 'const _str}
cur_line: int

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
            print(f"Executing line {cur_line}: {program[cur_line - 1]}")
            execute(program[cur_line - 1])
    if print_vars:
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
    global variables, cur_line
    if len(line) == 0:
        cur_line += 1
        return
    if line[0] in {'$'}:
        cur_line += 1
        return
    if '$' in line:
        line = line[:line.index('$') + 1]
    elif '.' not in line:
        raise Exception(f"Line {cur_line} is not properly terminated")
    if line[0] in {'_int', '_str', '_bool'}:
        variables = smile.declare(line, variables, cur_line)
    elif line[0] in variables.keys():
        variables = smile.assign(line, variables, cur_line)
    elif line[0] == '_read':
        variables = smile.read(line, variables, cur_line)
    elif line[0] in {'_write', '_writeline'}:
        smile.printst(line, variables, cur_line)
    else:
        if line[0].isnumeric() or line[0][0] == '_' or line[0][0].isupper():
            raise Exception(f"'{line[0]}' at line {cur_line} is an invalid name for a variable")
        else:
            raise Exception(f"Variable '{line[0]}' at line {cur_line} hasn't been declared")
    cur_line += 1

def lineIn():
    print('Welcome to the .;] input REPL. To exit, input: _exit .')
    while True:
        userIn = input("\( '3'){ ")
        if userIn == '_exit .':
            break
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

if __name__ == "__main__":
    main()