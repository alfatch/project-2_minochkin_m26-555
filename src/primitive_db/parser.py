# src/primitive_db/parser.py
import shlex


def parse_condition(tokens):
    if len(tokens) != 3 or tokens[1] != '=':
        return None
    return {tokens[0]: tokens[2]}


def parse_set_clause(tokens):
    if len(tokens) % 3 != 0:
        return None
    result = {}
    for i in range(0, len(tokens), 3):
        if tokens[i + 1] != '=':
            return None
        result[tokens[i]] = tokens[i + 2]
    return result


def parse_values(values_str):
    values_str = values_str.strip()
    if not (values_str.startswith('(') and values_str.endswith(')')):
        return None
    inner = values_str[1:-1]

    lexer = shlex.shlex(inner, posix=True)
    lexer.whitespace += ','
    lexer.whitespace_split = True
    lexer.quotes = '"\'' 

    try:
        return list(lexer)
    except ValueError:
        return None