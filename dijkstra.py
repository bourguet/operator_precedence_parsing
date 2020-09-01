#! /usr/bin/env python3
# Shunting yard algorithm, as described by http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF

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
    oper = parser.operators_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [parser.values_stack.pop()]))


def binary_evaluator(parser):
    oper = parser.operators_stack.pop()
    val2 = parser.values_stack.pop()
    val1 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [val1, val2]))


class Parser:
    def __init__(self):
        self.operators = {}
        self.register_infix_operator(['(', '['], 0)
        self.register_infix_operator([')', ']', ','], 1)
        self.register_infix_operator(':=', 2)
        self.register_infix_operator('==', 3)
        self.register_infix_operator('=>', 4)
        self.register_infix_operator('&', 5)
        self.register_infix_operator('|', 6)
        self.register_infix_operator('!', 7)
        self.register_infix_operator(['<', '<=', '=', '>', '>=', '!='], 8)
        self.register_infix_operator(['-', '+'], 9)
        self.register_infix_operator(['*', '/'], 10)
        self.register_unary_operator(['~'], 10)
        self.register_infix_operator('^', 11)
        self.reset()

    def reset(self):
        self.coma_interpretation = 0
        self.previous_coma_interpretation = []
        self.values_stack = []
        self.operators_stack = []

    def register_unary_operator(self, oper, prio, evaluator=None):
        if evaluator is None:
            evaluator = unary_evaluator
        if type(oper) is str:
            self.operators[oper] = OperatorDesc(oper, prio, evaluator)
        else:
            for op in oper:
                self.operators[op] = OperatorDesc(op, prio, evaluator)

    def register_infix_operator(self, oper, prio, evaluator=None):
        if evaluator is None:
            evaluator = binary_evaluator
        if type(oper) is str:
            self.operators[oper] = OperatorDesc(oper, prio, evaluator)
        else:
            for op in oper:
                self.operators[op] = OperatorDesc(op, prio, evaluator)

    def evaluate_operator(self):
        self.operators_stack[-1].evaluator(self)

    def push_operator(self, oper):
        while len(self.operators_stack) > 0 and self.operators_stack[-1].prio >= oper.prio:
            self.evaluate_operator()
        self.operators_stack.append(oper)

    def parse(self, s):
        self.reset()
        previous_was_id = False
        for tk in lexer.tokenize(s):
            if tk.kind == 'NUMBER' or tk.kind == 'ID':
                self.values_stack.append(Node(tk))
            elif tk.lexem == '(':
                self.operators_stack.append(self.operators[tk.lexem])
                self.previous_coma_interpretation.append(self.coma_interpretation)
                if previous_was_id:
                    self.coma_interpretation = 2
                else:
                    self.coma_interpretation = 0
            elif tk.lexem == '[':
                self.operators_stack.append(self.operators[tk.lexem])
                self.previous_coma_interpretation.append(self.coma_interpretation)
                self.coma_interpretation = 1
            elif tk.lexem in self.operators:
                self.push_operator(self.operators[tk.lexem])
                if tk.lexem == ')':
                    self.operators_stack.pop()
                    self.operators_stack.pop()
                    if self.coma_interpretation == 2:
                        val2 = self.values_stack.pop()
                        val1 = self.values_stack.pop()
                        self.values_stack.append(CompositeNode('call', [val1, val2]))
                    self.coma_interpretation = self.previous_coma_interpretation.pop()
                elif tk.lexem == ']':
                    self.operators_stack.pop()
                    self.operators_stack.pop()
                    val2 = self.values_stack.pop()
                    val1 = self.values_stack.pop()
                    self.values_stack.append(CompositeNode('index', [val1, val2]))
                    self.coma_interpretation = self.previous_coma_interpretation.pop()
            else:
                raise RuntimeError('Syntax error at {}'.format(tk.lexem))
            previous_was_id = tk.kind == 'ID'
        while len(self.operators_stack) > 0:
            self.evaluate_operator()
        if len(self.values_stack) != 1:
            raise RuntimeError('Internal error: value left on stack')
        return self.values_stack.pop()

    def dump(self):
        print('Operator stack')
        for oper in self.operators_stack:
            print('   {}'.format(oper))
        print('Value stack')
        for val in self.values_stack:
            print('   {}'.format(val))


def algol_exp_parser():
    parser = Parser()
    return parser


def check(s, expected):
    p = algol_exp_parser()
    tree = p.parse(s)
    sexpr = repr(tree)
    if sexpr != expected:
        print('Failed: {} => {} != {}'.format(s, sexpr, expected))


def basic_tests():
    check('a', 'a')
    check('~a * b', '(* (~ a) b)')
    check('a+b', '(+ a b)')
    check('a+b+c', '(+ (+ a b) c)')
    check('a+b*c', '(+ a (* b c))')
    check('(a+b)*c', '(* (+ a b) c)')
    check('a*b+c', '(+ (* a b) c)')
    check('a*(b+c)', '(* a (+ b c))')
    check('a(b)', '(call a b)')
    check('a[b]', '(index a b)')
    check('a(b, c)', '(call a (, b c))')
    check('a[b, c]', '(index a (, b c))')


def bad_error_detection():
    check('a b +', '(+ a b)')
    check('a b c [ , ]', '(index a (, b c))')


def self_tests():
    basic_tests()
    bad_error_detection()


def main(args):
    if len(args) == 1:
        self_tests()
    else:
        parser = algol_exp_parser()
        for s in args[1:]:
            try:
                exp = parser.parse(s)
                print('{} -> {}'.format(s, exp))
            except RuntimeError as run_error:
                print('Unable to parse {}: {}'.format(s, run_error))


if __name__ == "__main__":
    main(sys.argv)
