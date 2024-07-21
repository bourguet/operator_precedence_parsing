#! /usr/bin/env python3

import sys
import lexer
from tree import Node, CompositeNode


class SymbolDesc:
    def __init__(self, symbol, lprio, rprio, evaluator):
        self.symbol = symbol
        self.lprio = lprio
        self.rprio = rprio
        self.evaluator = evaluator

    def __repr__(self):
        return '<Symbol {} {}/{}>'.format(self.symbol, self.lprio, self.rprio)


def identity_evaluator(args):
    if len(args) == 1 and type(args[0]) == SymbolDesc:
        return Node(args[0].symbol)
    else:
        return CompositeNode('ID ERROR', args)


def binary_evaluator(args):
    if len(args) != 3 or type(args[0]) == SymbolDesc or type(args[1]) != SymbolDesc or type(args[2]) == SymbolDesc:
        return CompositeNode('BINARY ERROR', args)
    return CompositeNode(args[1].symbol, [args[0], args[2]])


class Parser:
    def __init__(self):
        self.presymbols = {}
        self.presymbols['$soi$'] = SymbolDesc('$soi$', 0, 0, None)
        self.postsymbols = {}
        self.postsymbols['$soi$'] = SymbolDesc('$soi$', 0, 0, None)

    def register_presymbol(self, oper, lprio, rprio, evaluator=None):
        if evaluator is None:
            evaluator = unary_evaluator
        if type(oper) is str:
            self.presymbols[oper] = SymbolDesc(oper, lprio, rprio, evaluator)
        else:
            for op in oper:
                self.presymbols[op] = SymbolDesc(op, lprio, rprio, evaluator)

    def register_postsymbol(self, oper, lprio, rprio, evaluator=None):
        if evaluator is None:
            evaluator = binary_evaluator
        if type(oper) is str:
            self.postsymbols[oper] = SymbolDesc(oper, lprio, rprio, evaluator)
        else:
            for op in oper:
                self.postsymbols[op] = SymbolDesc(op, lprio, rprio, evaluator)

    def advance(self):
        try:
            self.cur_token = self.lexer.__next__()
        except StopIteration:
            self.cur_token = None

    def reset(self, s):
        self.lexer = lexer.tokenize(s)
        self.advance()
        self.stack = [self.presymbols['$soi$']]

    def id_symbol(self, id):
        return SymbolDesc(id, 999, 1000, identity_evaluator)

    def evaluate_handle(self, args):
        for i in args:
            if type(i) == SymbolDesc:
                return i.evaluator(args)
        raise RuntimeError('Internal error: no evaluator found in {}'.format(args))

    def evaluate(self):
        idx = len(self.stack)-1
        if type(self.stack[idx]) != SymbolDesc:
            idx -= 1
        curprio = self.stack[idx].lprio
        while type(self.stack[idx-1]) != SymbolDesc or self.stack[idx-1].rprio == curprio:
            idx -= 1
            if type(self.stack[idx]) == SymbolDesc:
                curprio = self.stack[idx].lprio
        args = self.stack[idx:]
        self.stack[idx:] = []
        self.stack.append(self.evaluate_handle(args))

    def tos_symbol(self):
        idx = len(self.stack)-1
        while type(self.stack[idx]) != SymbolDesc:
            idx -= 1
        return self.stack[idx]

    def cur_sym(self, allow_presymbol):
        if self.cur_token is None:
            return None
        elif self.cur_token.kind == 'ID':
            return self.id_symbol(self.cur_token)
        elif self.cur_token.kind == 'NUMBER':
            return self.id_symbol(self.cur_token)
        elif allow_presymbol and self.cur_token.lexem in self.presymbols:
            return self.presymbols[self.cur_token.lexem]
        elif self.cur_token.lexem in self.postsymbols:
            return self.postsymbols[self.cur_token.lexem]
        else:
            return None

    def parse(self, s):
        self.reset(s)
        while True:
            sym = self.cur_sym(type(self.stack[-1]) == SymbolDesc)
            if sym is None:
                break
            while self.tos_symbol().rprio > sym.lprio:
                self.evaluate()
                sym = self.cur_sym(False)
            self.stack.append(sym)
            self.advance()
        while len(self.stack) > 2 or (len(self.stack) == 2 and type(self.stack[-1]) == SymbolDesc):
            self.evaluate()
        if len(self.stack) == 1:
            res = None
        elif len(self.stack) == 2:
            res = self.stack[1]
        if self.cur_token is not None:
            res = CompositeNode('REMAINING INPUT', [res, self.cur_token])
        return res


def open_parenthesis_evaluator(args):
    if (len(args) == 3
            and type(args[0]) == SymbolDesc and args[0].symbol == '('
            and type(args[1]) != SymbolDesc
            and type(args[2]) == SymbolDesc and args[2].symbol == ')'):
        return args[1]
    elif (len(args) == 3
            and type(args[0]) != SymbolDesc
            and type(args[1]) == SymbolDesc and args[1].symbol == '('
            and type(args[2]) == SymbolDesc and args[2].symbol == ')'):
        return CompositeNode('call', [args[0]])
    elif (len(args) == 4
            and type(args[0]) != SymbolDesc
            and type(args[1]) == SymbolDesc and args[1].symbol == '('
            and type(args[2]) != SymbolDesc
            and type(args[3]) == SymbolDesc and args[3].symbol == ')'):
        if args[2].token == ',':
            callargs = args[2].children
        else:
            callargs = [args[2]]
        callargs.insert(0, args[0])
        return CompositeNode('call', callargs)
    else:
        return CompositeNode('( ERROR', args)


def close_parenthesis_evaluator(args):
    return CompositeNode(') ERROR', args)


def open_bracket_evaluator(args):
    if (len(args) == 4
            and type(args[0]) != SymbolDesc
            and type(args[1]) == SymbolDesc and args[1].symbol == '['
            and type(args[2]) != SymbolDesc
            and type(args[3]) == SymbolDesc and args[3].symbol == ']'):
        return CompositeNode('get', [args[0], args[2]])
    else:
        return CompositeNode('[ ERROR', args)


def close_bracket_evaluator(args):
    return CompositeNode('] ERROR', args)


def coma_evaluator(args):
    return CompositeNode(',', [x for x in args if type(x) != SymbolDesc])


def unary_evaluator(args):
    if len(args) != 2:
        return CompositeNode('UNARY ERROR', args)
    if type(args[0]) == SymbolDesc and type(args[1]) != SymbolDesc:
        return CompositeNode(args[0].symbol, [args[1]])
    elif type(args[0]) != SymbolDesc and type(args[1]) == SymbolDesc:
        return CompositeNode('post'+args[1].symbol, [args[0]])
    else:
        return CompositeNode('UNARY ERROR', args)


def question_evaluator(args):
    if (len(args) != 5
            or type(args[0]) == SymbolDesc
            or type(args[1]) != SymbolDesc or args[1].symbol != '?'
            or type(args[2]) == SymbolDesc
            or type(args[3]) != SymbolDesc or args[3].symbol != ':'
            or type(args[4]) == SymbolDesc):
        return CompositeNode('? ERROR', args)
    return CompositeNode('?', [args[0], args[2], args[4]])


def colon_evaluator(args):
    return CompositeNode(': ERROR', args)


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
    parser.register_presymbol(['+', '-', '++', '--', '~', '!', '&', '*'], 31, 30, unary_evaluator)
    parser.register_postsymbol(['++', '--'], 32, 33, unary_evaluator)
    parser.register_postsymbol(['.', '->'], 32, 33)
    parser.register_postsymbol('(', 100, 1, open_parenthesis_evaluator)
    parser.register_postsymbol(')', 1, 100, close_parenthesis_evaluator)
    parser.register_postsymbol('[', 100, 1, open_bracket_evaluator)
    parser.register_postsymbol(']', 1, 100, close_bracket_evaluator)
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
