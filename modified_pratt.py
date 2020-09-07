#! /usr/bin/env python3

import sys
import lexer
from tree import Node, CompositeNode


class SymbolDesc:
    def __init__(self, token, lprio, rprio, evaluator):
        self.token = token
        self.lprio = lprio
        self.rprio = rprio
        self.evaluator = evaluator

    def __repr__(self):
        return '<Symbol {} {}/{}>'.format(self.token.lexem, self.lprio, self.rprio)


def prefix_error(parser, sym):
    arg = parser.parse_to(sym.rprio)
    if arg is None:
        return CompositeNode('NOT VALID PREFIX ' + str(sym.token), [])
    else:
        return CompositeNode('NOT VALID PREFIX ' + str(sym.token), [arg])


def postfix_error(parser, left_arg, sym):
    return CompositeNode('NOT VALID POSTFIX ' + str(sym.token), [left_arg])


def identity_evaluator(parser, sym):
    result = Node(sym.token)
    return result


def unary_prefix_evaluator(parser, sym):
    arg = parser.parse_to(sym.rprio)
    if arg is None:
        return CompositeNode('MISSING ARG ' + str(sym.token), [])
    else:
        return CompositeNode(sym.token, [arg])


def binary_evaluator(parser, left_arg, sym):
    right_arg = parser.parse_to(sym.rprio)
    return CompositeNode(sym.token, [left_arg, right_arg])


def unary_postfix_evaluator(parser, left_arg, sym):
    return CompositeNode('post' + sym.token, [left_arg])


class Parser:
    def __init__(self):
        self.lexer = None
        self.cur_token = None
        self.presymbols = {}
        self.postsymbols = {}

    def register_presymbol(self, oper, rprio, evaluator=unary_prefix_evaluator):
        if type(oper) is str:
            self.presymbols[oper] = SymbolDesc(oper, None, rprio, evaluator)
        else:
            for op in oper:
                self.presymbols[op] = SymbolDesc(op, None, rprio, evaluator)

    def register_postsymbol(self, oper, lprio, rprio, evaluator=binary_evaluator):
        if type(oper) is str:
            self.postsymbols[oper] = SymbolDesc(oper, lprio, rprio, evaluator)
        else:
            for op in oper:
                self.postsymbols[op] = SymbolDesc(op, lprio, rprio, evaluator)

    def reset(self, s):
        self.lexer = lexer.tokenize(s)
        self.advance()

    def advance(self):
        try:
            self.cur_token = self.lexer.__next__()
        except StopIteration:
            self.cur_token = None

    def prefix_sym(self):
        if self.cur_token is None:
            return None
        elif self.cur_token.kind == 'ID':
            return SymbolDesc(self.cur_token, None, None, identity_evaluator)
        elif self.cur_token.kind == 'NUMBER':
            return SymbolDesc(self.cur_token, None, None, identity_evaluator)
        elif self.cur_token.lexem in self.presymbols:
            return self.presymbols[self.cur_token.lexem]
        else:
            return SymbolDesc(self.cur_token, None, 1000, prefix_error)

    def postfix_sym(self):
        if self.cur_token is None:
            return None
        elif self.cur_token.kind == 'ID':
            return SymbolDesc(self.cur_token, 0, 1000, postfix_error)
        elif self.cur_token.kind == 'NUMBER':
            return SymbolDesc(self.cur_token, 0, 1000, postfix_error)
        elif self.cur_token.lexem in self.postsymbols:
            return self.postsymbols[self.cur_token.lexem]
        else:
            return SymbolDesc(self.cur_token, 0, 1000, postfix_error)

    def parse_to(self, prio):
        sym = self.prefix_sym()
        if sym is None:
            return None
        self.advance()
        node = sym.evaluator(self, sym)
        while True:
            sym = self.postfix_sym()
            if sym is None or prio >= sym.lprio:
                break
            self.advance()
            node = sym.evaluator(self, node, sym)
        return node

    def parse(self, s):
        self.reset(s)
        res = self.parse_to(0)
        if self.cur_token is not None:
            res = CompositeNode('REMAINING INPUT', [res, self.cur_token])
        return res


def prefix_open_parenthesis_evaluator(parser, sym):
    result = parser.parse_to(sym.rprio)
    if parser.cur_token is not None and parser.cur_token.lexem == ')':
        parser.advance()
        return result
    else:
        return CompositeNode('( ERROR', [result])


def postfix_open_parenthesis_evaluator(parser, left_arg, sym):
    if parser.cur_token is not None and parser.cur_token.lexem == ')':
        parser.advance()
        return CompositeNode('call '+str(left_arg), [])
    else:
        result = parser.parse_to(sym.rprio)
        if parser.cur_token is not None and parser.cur_token.lexem == ')':
            parser.advance()
            if result.token == ',':
                return CompositeNode('call ' + str(left_arg), result.children)
            else:
                return CompositeNode('call ' + str(left_arg), [result])
        else:
            return CompositeNode('( ERROR', [result])


def postfix_close_parenthesis_evaluator(parser, left_arg, sym):
    return CompositeNode(') ERROR', [left_arg])


def postfix_open_bracket_evaluator(parser, left_arg, sym):
    result = parser.parse_to(sym.rprio)
    if parser.cur_token is not None and parser.cur_token.lexem == ']':
        parser.advance()
        return CompositeNode('get ' + str(left_arg), [result])
    else:
        return CompositeNode('[ ERROR', [left_arg, result])


def postfix_close_bracket_evaluator(parser, left_arg, sym):
    return CompositeNode('] ERROR', [left_arg])


def coma_evaluator(parser, left_arg, sym):
    args = [left_arg]
    while True:
        args.append(parser.parse_to(sym.rprio))
        sym = parser.postfix_sym()
        if sym is None or sym.token != ',':
            break
        parser.advance()
    return CompositeNode(',', args)


def question_evaluator(parser, left_arg, sym):
    true_exp = parser.parse_to(sym.rprio)
    sym = parser.postfix_sym()
    if sym is not None and sym.token == ':':
        parser.advance()
        false_exp = parser.parse_to(sym.rprio)
        return CompositeNode('?', [left_arg, true_exp, false_exp])
    else:
        return CompositeNode('? ERROR', [left_arg, true_exp])


def colon_evaluator(parser, left_arg, sym):
    return CompositeNode(': ERROR', [left_arg])


def cexp_parser():
    parser = Parser()
    parser.register_postsymbol(',', 2, 2, coma_evaluator)
    parser.register_postsymbol(['=', '*=', '/=', '%=', '+=', '-=', '<<=', '>>=', '&=', '|=', '^='], 5, 4)
    parser.register_postsymbol('?', 7, 1, question_evaluator)
    parser.register_postsymbol(':', 1, 6, colon_evaluator)
    parser.register_postsymbol('||', 8, 9)
    parser.register_postsymbol('&&', 10, 11)
    parser.register_postsymbol('|', 12, 13)
    parser.register_postsymbol('^', 14, 15)
    parser.register_postsymbol('&', 16, 17)
    parser.register_postsymbol(['==', '!='], 18, 19)
    parser.register_postsymbol(['<', '>', '<=', '>='], 20, 21)
    parser.register_postsymbol(['<<', '>>'], 22, 23)
    parser.register_postsymbol(['+', '-'], 24, 25)
    parser.register_postsymbol(['/', '%', '*'], 26, 27)
    parser.register_postsymbol('**', 29, 28)
    parser.register_presymbol(['+', '-', '++', '--', '~', '!', '&', '*'], 30)
    parser.register_postsymbol(['++', '--'], 32, 33, unary_postfix_evaluator)
    parser.register_postsymbol(['.', '->'], 32, 33)
    parser.register_presymbol('(', 1, prefix_open_parenthesis_evaluator)
    parser.register_postsymbol('(', 100, 1, postfix_open_parenthesis_evaluator)
    parser.register_postsymbol(')', 1, 100, postfix_close_parenthesis_evaluator)
    parser.register_postsymbol('[', 100, 1, postfix_open_bracket_evaluator)
    parser.register_postsymbol(']', 1, 100, postfix_close_bracket_evaluator)
    return parser


def main(args):
    parser = cexp_parser()
    for s in args[1:]:
        try:
            exp = parser.parse(s)
            print('{} -> {}'.format(s, exp))
        except RuntimeError as run_error:
            print('Unable to parse {}: {}'.format(s, run_error))


if __name__ == "__main__":
    main(sys.argv)
