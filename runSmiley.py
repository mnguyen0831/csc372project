from scanSmiley import scanLine, scanSmiley
import parseSmiley as smile
import argparse

input_line: str
input_file: str
output_file: str
print_ast: bool
print_vars: bool
program: list[list[str]]
variables: dict[str, list[str, bool | int | str]] # key: id, val: [type, value], types are {'_int', '_bool', '_str', 'const _int', 'const _bool', 'const _str}
cur_line: int

# Files can be run using:
# python runSmiley.py --input-file 'sample.;]'
# python runSmiley.py --input-line '1 + 2 + 3 .'

def main() -> None:
    global program, variables, print_ast, print_vars, cur_line
    variables = dict()
    cur_line = 1
    print(smile.expr('"Answer is: " + ( ( 1 + ( 1 * 5 ) - 4 ) % 2 ) + "." .'.split(), variables, 1))
    getInput()
    if input_file is None:
        program = [scanLine(input_line)]
    else:
        program = scanSmiley(input_file)
    while cur_line - 1 < len(program):
        print(f"Executing line {cur_line}: {program[cur_line - 1]}")
        execute(program[cur_line - 1])
    if print_ast:
        print("Print AST not implemented.")
    if print_vars:
        print("\nVariables:\n----------")
        for var in variables.keys():
            print(f"{var} : {variables[var]}")

def getInput() -> None:
    global input_line, input_file, output_file, print_ast, print_vars
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--input-line', type=str, help='Line to run')
    parser.add_argument('--input-file', type=str, default=None, help='File name to run')
    parser.add_argument('--output-file', type=str, help='File to write to output')
    parser.add_argument('--ast', type=bool, default=False, help='Prints out Syntax Tree')
    parser.add_argument('--vars', type=bool, default=False, help='Prints out Variable Dictionary')
    args = parser.parse_args()
    input_line = args.input_line
    input_file = args.input_file
    output_file = args.output_file
    print_ast = args.ast
    print_vars = args.vars

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
        #print(f"Variables updated: {variables}")
    elif line[0] in variables.keys():
        variables = smile.assign(line, variables, cur_line)
        #print(f"Variables updated: {variables}")
    elif line[0] == '_read':
        pass # variables = smile.read(line, variables, cur_line)
    elif line[0] in {'_write', '_writeline'}:
        pass #smile.print(line, variables)
    else:
        if line[0].isnumeric() or line[0][0] == '_' or line[0][0].isupper():
            raise Exception(f"'{line[0]}' at line {cur_line} is an invalid name for a variable")
        else:
            raise Exception(f"Variable '{line[0]}' at line {cur_line} hasn't been declared")
    cur_line += 1


if __name__ == "__main__":
    main()