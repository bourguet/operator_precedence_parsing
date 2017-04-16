# A lexer used by all the parsers
# A simple lexer for C like expressions.  The major difference with C is that consecutive operators have
# to be separated with white spaces.

import re


class Token:
    def __init__(self, kind, lexem):
        self.kind = kind
        self.lexem = lexem

    def __repr__(self):
        return '<Token {} \'{}\'>'.format(self.kind, self.lexem)


def tokenize(code):
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),
        ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
        ('OPER',     r'[-~+*/%=<>?!:|&^@]+'),
        ('SYNT',     r'[][(),.]'),
        ('SKIP',     r'[ \t\n]+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise RuntimeError('{} unexpected'.format(value))
        else:
            yield Token(kind, value)
