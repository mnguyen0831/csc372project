from tokenSmiley import tokenizeLine, tokenizeSmiley
import executeSmiley as smile
import argparse

input_line: str
input_file: str
output_file: str
print_ast: bool
program: list[list[str]]
variables: dict[str, bool | int | str]

# Files can be run using:
# python runSmiley.py --input-file 'sample.;]'
# python runSmiley.py --input-line '1 + 2 + 3 .'

def main() -> None:
    global program, variables
    variables = dict()
    getInput()
    if input_file is None:
        program = tokenizeLine(input_line)
    else:
        program = [tokenizeSmiley(input_file)]
    for line in program:
        execute(line)

def getInput() -> None:
    global input_line, input_file, output_file, ast
    parser = argparse.ArgumentParser(description='Reads command line arguments.')
    parser.add_argument('--input-line', type=str, help='Line to run')
    parser.add_argument('--input-file', type=str, default=None, help='File name to run')
    parser.add_argument('--output-file', type=str, help='File to write to output')
    parser.add_argument('--ast', type=bool, default=False, help='Prints out Syntax Tree')
    args = parser.parse_args()
    input_line = args.input_line
    input_file = args.input_file
    output_file = args.output_file
    print_ast = args.ast

def execute(line: list[str]) -> None:
    global variables
    if line[0] in {'$'}:
        return
    elif line[0] in {'_int', '_str', '_bool'}:
        smile.declare(line)
    elif line[0] in variables.keys():
        pass #assign(line)
    elif line[0] in {'_write', '_writeline'}:
        pass #print(line)


if __name__ == "__main__":
    main()