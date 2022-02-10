#! /usr/bin/env python3

import sys
import lexer
from tree import Node, CompositeNode


class SymbolDesc:
    def __init__(self, token, prio):
        self.token = token
        self.prio = prio

    def __repr__(self):
        return '<Symbol {} {}>'.format(self.token.lexem, self.prio)


class Parser:
    def __init__(self):
        self.lexer = None
        self.cur_token = None
        self.min_prio = 1000000000
        self.max_prio = 0
        self.symbols = {}

    def register_oper(self, oper, prio):
        if prio <= self.min_prio:
            self.min_prio = prio - 1
        if prio >= self.max_prio:
            self.max_prio = prio + 1
        if type(oper) is str:
            self.symbols[oper] = SymbolDesc(oper, prio)
        else:
            for op in oper:
                self.symbols[op] = SymbolDesc(op, prio)

    def get_prio(self, token):
        if token is not None and token.lexem in self.symbols:
            return self.symbols[token.lexem].prio
        else:
            return -1

    def reset(self, s):
        self.lexer = lexer.tokenize(s)
        self.advance()

    def advance(self):
        try:
            self.cur_token = self.lexer.__next__()
        except StopIteration:
            self.cur_token = None

    def parse_factor(self):
        if self.cur_token is None:
            return None
        elif self.cur_token.kind == 'ID':
            result = Node(self.cur_token)
            self.advance()
            return result
        elif self.cur_token.kind == 'NUMBER':
            result = Node(self.cur_token)
            self.advance()
            return result
        else:
            return Node(lexer.Token('ERROR', 'MISSING VALUE'))

    def parse_exp(self, prio):
        left_arg = self.parse_factor()
        while prio < self.get_prio(self.cur_token):
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_exp(self.get_prio(oper))
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse(self, s):
        self.reset(s)
        res = self.parse_exp(self.min_prio)
        if self.cur_token is not None:
            res = CompositeNode('REMAINING INPUT', [res, self.cur_token])
        return res


def parser():
    result = Parser()
    result.register_oper(['||'], 8)
    result.register_oper(['&&'], 10)
    result.register_oper(['=='], 18)
    result.register_oper(['+', '-'], 24)
    result.register_oper(['*', '/'], 26)
    return result
