#! /usr/bin/env python3

import sys
import lexer
from tree import Node, CompositeNode


class Parser:
    def __init__(self):
        self.lexer = None
        self.cur_token = None

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

    def parse_mult(self):
        left_arg = self.parse_factor()
        while self.cur_token is not None and (self.cur_token.lexem == "*" or self.cur_token.lexem == "/"):
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_factor()
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse_add(self):
        left_arg = self.parse_mult()
        while self.cur_token is not None and (self.cur_token.lexem == "+" or self.cur_token.lexem == "-"):
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_mult()
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse_eq(self):
        left_arg = self.parse_add()
        while self.cur_token is not None and self.cur_token.lexem == "==":
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_add()
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse_and(self):
        left_arg = self.parse_eq()
        while self.cur_token is not None and self.cur_token.lexem == "&&":
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_eq()
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse_or(self):
        left_arg = self.parse_and()
        while self.cur_token is not None and self.cur_token.lexem == "||":
            oper = self.cur_token
            self.advance()
            right_arg = self.parse_and()
            left_arg = CompositeNode(oper.lexem, [left_arg, right_arg])
        return left_arg

    def parse(self, s):
        self.reset(s)
        res = self.parse_or()
        if self.cur_token is not None:
            res = CompositeNode('REMAINING INPUT', [res, self.cur_token])
        return res


def parser():
    return Parser()
