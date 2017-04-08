#! /usr/bin/env python3

import re
import sys


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
        ('OPER',     r'[-+*/=<>?!:]+'),
        ('SYNT',     r'[][(),.]'),
        ('SKIP',     r'[ \t]+'),
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


class Node:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return self.token.lexem


class CompositeNode(Node):
    def __init__(self, token, children):
        Node.__init__(self, token)
        self.children = children

    def __repr__(self):
        args = ''.join([" " + repr(c) for c in self.children])
        return '(' + self.token + args + ')'


class OperatorDesc:
    def __init__(self, oper, lprio, rprio, builder):
        self.oper = oper
        self.lprio = lprio
        self.rprio = rprio
        self.builder = builder

    def __repr__(self):
        return '<Oper {} {}/{}>'.format(self.oper, self.lprio, self.rprio)


def unary_builder(parser):
    oper = parser.operators_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [parser.values_stack.pop()]))


def binary_builder(parser):
    oper = parser.operators_stack.pop()
    val2 = parser.values_stack.pop()
    val1 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [val1, val2]))


class Parser:
    def __init__(self):
        self.prefix_operators = {}
        self.infix_operators = {}
        self.postfix_operators = {}
        self.reset()

    def reset(self):
        self.waiting_value = True
        self.values_stack = []
        self.operators_stack = []

    def register_prefix_operator(self, oper, rprio, builder=None):
        if builder is None:
            builder = unary_builder
        if type(oper) is str:
            self.prefix_operators[oper] = OperatorDesc(oper, -1, rprio, builder)
        else:
            for op in oper:
                self.prefix_operators[op] = OperatorDesc(op, -1, rprio, builder)

    def register_infix_operator(self, oper, lprio, rprio, builder=None):
        if builder is None:
            builder = binary_builder
        if type(oper) is str:
            self.infix_operators[oper] = OperatorDesc(oper, lprio, rprio, builder)
        else:
            for op in oper:
                self.infix_operators[op] = OperatorDesc(op, lprio, rprio, builder)

    def register_postfix_operator(self, oper, lprio, builder=None):
        if builder is None:
            builder = unary_builder
        if type(oper) is str:
            self.postfix_operators[oper] = OperatorDesc(oper, lprio, 1000, builder)
        else:
            for op in oper:
                self.postfix_operators[op] = OperatorDesc(op, lprio, 1000, builder)

    def evaluate_operator(self):
        self.operators_stack[-1].builder(self)

    def push_operator(self, oper):
        while len(self.operators_stack) > 0 and self.operators_stack[-1].rprio >= oper.lprio:
            self.evaluate_operator()
        self.operators_stack.append(oper)

    def parse_for_value(self, tk):
        if tk.kind == 'NUMBER' or tk.kind == 'ID':
            self.values_stack.append(Node(tk))
            self.waiting_value = False
        elif tk.lexem in self.prefix_operators:
            self.operators_stack.append(self.prefix_operators[tk.lexem])
        else:
            raise RuntimeError('{} is not a prefix operator or a value'.format(tk.lexem))

    def parse_for_operator(self, tk):
        if tk.lexem in self.postfix_operators:
            self.push_operator(self.postfix_operators[tk.lexem])
        elif tk.lexem in self.infix_operators:
            self.waiting_value = True
            self.push_operator(self.infix_operators[tk.lexem])
        else:
            raise RuntimeError('{} is not a postfix or an infix operator'.format(tk.lexem))

    def parse(self, s):
        self.reset()
        for tk in tokenize(s):
            if self.waiting_value:
                self.parse_for_value(tk)
            else:
                self.parse_for_operator(tk)
        while len(self.operators_stack) > 0:
            self.evaluate_operator()
        if len(self.values_stack) == 0:
            raise RuntimeError('No value given')
        return self.values_stack.pop()

    def dump(self):
        print('Operator stack')
        for oper in self.operators_stack:
            print('   {}'.format(oper))
        print('Value stack')
        for val in self.values_stack:
            print('   {}'.format(val))


def prefix_open_parenthesis(parser):
    parser.dump()
    raise RuntimeError('Unclosed open parenthesis')


def infix_open_parenthesis(parser):
    parser.dump()
    raise RuntimeError('Unclosed open parenthesis')


def prefix_close_parenthesis(parser):
    op1 = parser.operators_stack.pop()
    op2 = parser.operators_stack.pop()
    if op2.oper != '(' or op2.builder != infix_open_parenthesis:
        parser.dump()
        raise RuntimeError('Empty parenthesis')
    val1 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode('CALL', [val1]))


def postfix_close_parenthesis(parser):
    op1 = parser.operators_stack.pop()
    op2 = parser.operators_stack.pop()
    if op2.oper != '(':
        parser.dump()
        raise RuntimeError('Unopened close parenthesis')
    if op2.builder == infix_open_parenthesis:
        val1 = parser.values_stack.pop()
        val2 = parser.values_stack.pop()
        parser.values_stack.append(CompositeNode('CALL', [val2, val1]))


def infix_question(parser):
    parser.dump()
    raise RuntimeError('? without :')


def infix_colon(parser):
    op1 = parser.operators_stack.pop()
    op2 = parser.operators_stack.pop()
    if op2.oper != '?':
        parser.dump()
        raise RuntimeError(': wihout ?')
    val1 = parser.values_stack.pop()
    val2 = parser.values_stack.pop()
    val3 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode('?:', [val3, val2, val1]))


def main(args):
    parser = Parser()
    parser.register_prefix_operator('(', 0, prefix_open_parenthesis)
    parser.register_postfix_operator(')', 1, postfix_close_parenthesis)
    parser.register_prefix_operator(')', 1, prefix_close_parenthesis)
    parser.register_infix_operator(',', 2, 2)
    parser.register_infix_operator(['=', '*=', '/=', '%=', '+=', '-=', '<<=', '>>=', '&=', '|='], 4, 3)
    parser.register_infix_operator('?', 5, 0, infix_question)
    parser.register_infix_operator(':', 1, 5, infix_colon)
    parser.register_infix_operator('||', 6, 6)
    parser.register_infix_operator('&&', 7, 7)
    parser.register_infix_operator('|', 8, 8)
    parser.register_infix_operator('^', 9, 9)
    parser.register_infix_operator('&', 10, 10)
    parser.register_infix_operator(['==', '!='], 11, 11)
    parser.register_infix_operator(['<', '>', '<=', '>='], 12, 12)
    parser.register_infix_operator(['<<', '>>'], 13, 13)
    parser.register_infix_operator(['+', '-'], 14, 14)
    parser.register_infix_operator(['*', '/', '%'], 15, 15)
    parser.register_prefix_operator(['+', '-', '++', '--', '&', '*', '~', '!'], 16)
    parser.register_postfix_operator(['++', '--', '.', '->'], 17)
    parser.register_infix_operator('(', 17, 0, infix_open_parenthesis)
    for s in args[1:]:
        try:
            exp = parser.parse(s)
            print('{} -> {}'.format(s, exp))
        except RuntimeError as run_error:
            print('Unable to parse {}: {}'.format(s, run_error))


if __name__ == "__main__":
    main(sys.argv)
