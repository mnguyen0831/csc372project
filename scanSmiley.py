def scanSmiley(fname: str) -> list[list[str]]:
    print(f"Open: {fname}")
    file = open(fname, 'r')
    lines = file.readlines()
    tokens: list[list[str]] = list()

    for line in lines:
        tokens.append(line.split())
    return tokens

def scanLine(line: str) -> list[str]:
    return line.split()