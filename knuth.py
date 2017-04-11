#! /usr/bin/env python3
# An implementation of _A version of the "modern" translation algorithm_
# of _A History of Writing Compilers_, D.E. Knuth, 1962, reprinted in _Selected Papers
# on Computer Languages_, 2003.

import sys
import lexer
from tree import Node, CompositeNode


class OperatorDesc:
    def __init__(self, oper, prio, evaluator):
        self.oper = oper
        self.prio = prio
        self.evaluator = evaluator

    def __repr__(self):
        return '<Oper {} {}/{}>'.format(self.oper, self.lprio, self.rprio)


def unary_evaluator(parser):
    val = parser.stack.pop()
    oper = parser.stack.pop()
    parser.stack.append(CompositeNode(oper.oper, [val]))


def binary_evaluator(parser):
    val2 = parser.stack.pop()
    oper = parser.stack.pop()
    val1 = parser.stack.pop()
    parser.stack.append(CompositeNode(oper.oper, [val1, val2]))


class Parser:
    def __init__(self):
        self.binary_operators = {}
        self.unary_operators = {}
        self.register_binary_operator(['@', ')'], 0)
        self.register_unary_operator(['('], 0)
        # := behaves partly as an unary operator (it is pushed unconditionally) and partly as a binary operator
        # it has two arguments
        self.unary_operators[':='] = OperatorDesc(':=', 0, binary_evaluator)
        self.register_binary_operator(['+', '-'], 1)
        self.register_binary_operator(['*', '/'], 2)
        self.register_binary_operator('^', 3)
        self.register_unary_operator(['ABS', 'SQRT', 'COS'], 4)
        self.reset()

    def reset(self):
        self.stack = [self.binary_operators['@']]

    def register_unary_operator(self, oper, prio, evaluator=None):
        if evaluator is None:
            evaluator = unary_evaluator
        if type(oper) is str:
            self.unary_operators[oper] = OperatorDesc(oper, prio, evaluator)
        else:
            for op in oper:
                self.unary_operators[op] = OperatorDesc(op, prio, evaluator)

    def register_binary_operator(self, oper, prio, evaluator=None):
        if evaluator is None:
            evaluator = binary_evaluator
        if type(oper) is str:
            self.binary_operators[oper] = OperatorDesc(oper, prio, evaluator)
        else:
            for op in oper:
                self.binary_operators[op] = OperatorDesc(op, prio, evaluator)

    def tokenize(self, s):
        for tk in lexer.tokenize(s):
            yield tk
        yield lexer.Token('OPER', '@')

    def parse(self, s):
        self.reset()
        for tk in self.tokenize(s):
            if tk.lexem in self.binary_operators:
                S = self.binary_operators[tk.lexem]
                emulate_goto = False
                while S.prio <= self.stack[-2].prio:
                    if self.stack[-2].oper == '@':
                        return self.stack[-1]
                    elif self.stack[-2].oper == '(':
                        v = self.stack.pop()
                        self.stack.pop()
                        self.stack.append(v)
                        # the algorithm is described with a flow chart which is not structured...
                        emulate_goto = True
                        break
                    else:
                        self.stack[-2].evaluator(self)
                if emulate_goto:
                    continue
            elif tk.lexem in self.unary_operators:
                S = self.unary_operators[tk.lexem]
            else:
                S = Node(tk)
            self.stack.append(S)

    def dump(self):
        print('Operator stack')
        for oper in self.operators_stack:
            print('   {}'.format(oper))
        print('Value stack')
        for val in self.values_stack:
            print('   {}'.format(val))


def check(s, expected):
    p = Parser()
    tree = p.parse(s)
    sexpr = repr(tree)
    if sexpr != expected:
        print('Failed: {} => {} != {}'.format(s, sexpr, expected))


def basic_tests():
    check('a', 'a')
    check('a+b', '(+ a b)')
    check('a+b+c', '(+ (+ a b) c)')
    check('a+b*c', '(+ a (* b c))')
    check('(a+b)*c', '(* (+ a b) c)')
    check('a*b+c', '(+ (* a b) c)')
    check('a*(b+c)', '(* a (+ b c))')
    check('COS a', '(COS a)')
    check('U := B := X + COS(Y*Z)/W', '(:= U (:= B (+ X (/ (COS (* Y Z)) W))))')


def self_tests():
    basic_tests()


def main(args):
    if len(args) == 1:
        self_tests()
    else:
        parser = Parser()
        for s in args[1:]:
            try:
                exp = parser.parse(s)
                print('{} -> {}'.format(s, exp))
            except RuntimeError as run_error:
                print('Unable to parse {}: {}'.format(s, run_error))

if __name__ == "__main__":
    main(sys.argv)
