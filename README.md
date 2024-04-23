# Smiley
### Langauge designed by Matthew Nguyen, Dylan Wilson, Omari Hughes, and Oscar Fischer

## How to run a Smiley file
In the folder containing exprSmiley.py, parseSmiley.py, and runSmiley.py, run the command:
    ```
    python runSmiley.py --file 'file_name'
    ```
The file extension does not matter.

### Flags
All flags are optional, and may be used with any combination of other flags.
#### --file
Takes a singular input: the name of the file to run.

#### --repl
Starts up the REPL after executing the input file, if there was one. The variables created and
assigned during the file execution are accessible from the REPL. 

#### --vars
Prints out the full variable list after the input file has been executed, and the REPL has been
exited.

#### --print-flow
Prints out the line number and tokenization as the line is executed.

## Language Basics
### Grammar
```
# Program
<program> ::= <statement>

# IDs
<id> ::= <var id> | <const id>
<var id> ::= starts with lowercase char, ends at whitespace
<const id> ::= starts with uppercase char, ends at whitespace 
<type> ::= _int | _str | _bool

# Literals
<literal> ::= <int> | <string> | <boolean>
<int> ::= 0-9 | 0-9<int> 
<string> :: = "string"
<boolean> ::= <true> | <false> 
<true> ::= :) | (: | :^) | (^: | :’) | (’:
<false> ::= :( | ): | :^( | )^: | :’( | )‘:

# Statements
<statement> ::= <declaration st> | <assign st> | <read st> | <print st> | <if st> | <while st> | <statement> <statement> | <comment>
<comment> ::= $ anything
<declaration st> ::= <type> <var id> | <type> <const id> _is <literal> . 
<assign st> ::= <var id> _is <expr> . | <var id> ++ . | <var id> += <expr> .
<read st> ::= _read <var id> .
<print st> ::= _writeline <expr> . | _write <expr> .
<if st> ::= _if <expr> _then { <statement> } | _if <expr> _then { <statement> } <else>
<else> ::= _else { <statement> } | _elseif <expr> _then { <statement> } | _elseif <expr> _then { <statement> } <else>
<while st> ::= _while <expr> _do { <statement> }

# Expressions
<expr> ::= <unary expr> | <binary expr> 
<binary expr> ::= <unary expr> <binary op> <expr> | <binary op> <expr>
<unary expr> ::= <unary op> <base expr> | <base expr> 
<base expr> ::= <id> | <literal> | ( <expr> ) 

# Operators
<unary op> ::= - | ^
<binary op> ::= <multi op> | <add op> | <comp op>
<multi op> ::= * | / | %
<add op> ::= + | -
<comparator op> ::= & | | | <= | < | >= | > | = | !=
```

### General Syntax Rules
Every statement needs to be on a new line by itself, except in the case of inline comments. 
Additionally, _if, and _while structures follow similar rules, where the closing bracket needs to
be on a line by itself, and any _elseif and _else branches need to begin with a closing bracket and
end the line with an opening bracket. Also, indentation is not tracked.

#### _if Example:
```
_if <expr> _then {
    $ Do something
} _elseif <expr> _then {
    $ Do something
} _else {
    $ Do something
}
```

#### _while Example:
```
_while <expr> _do {
    $ Do something
}
```

### Variable and Constant IDs
Variables must start with a lowercase alphabet character, and end at the first whitespace.
Alternatively, constants must start with an uppercase alphabet character, also ending at the first
whitespace. Variables and constants may contain any combination of characters outside of whitespace
otherwise. 

### Literal Values
Smiley has 3 types: _int, _bool, and _str. _ints are used in the syntax as ints would be in Python 
and Java. However, _bools have a different format, where both true and false have multiple aliases 
that would be accepted. _strs in Smiley must be surrounded by "s, or else the _str value may be
mistaken for an ID or operator.

### Comments
The Smiley interpreter will ignore everything past a '$' character, even in a string. In order to
use the '$' character, '$$' must be used. 

### Variable and Constant Declaration and Assignment
All variables must be declared, and then assigned in a separate line. Alternatively, constants 
must be assigned a literal value at declaration. Variables cannot be reassigned using the '++' or
'+=' operator without first being assigned a value, and Constants may not be reassigned at all.

### Reading User Input
_read statements are used to read user input into a variable. The _read statement will validate
the input to ensure that the input is at least a valid Smiley literal, and give an example if it
is not. _read also tells the user the type of the variable they are reading into if an incorrect
type is given.

### Printing Out Expressions
_write prints the inner expression to the terminal with no newline character at the end, while
_writeline does the same with a newline character at the end.

### General Expression Rules
Every operator and operand must be separated by whitespace, otherwise it will be mistaken for an
invalid ID or operator.

#### Atypical/Special Operators
'^'
    _bool negation
    Placed in front of the _bool value

'%'
    Smiley's modulo operator

'+'
    When used with two _ints, it is normal addition
    When preceeded by a _str type, it coerces the value of the following expression into a _str

'='
    Comparison operator that is equivalent to Python's '==' operator