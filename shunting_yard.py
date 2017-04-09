#! /usr/bin/env python3

import sys
import lexer
from tree import Node, CompositeNode


class OperatorDesc:
    def __init__(self, oper, lprio, rprio, evaluator):
        self.oper = oper
        self.lprio = lprio
        self.rprio = rprio
        self.evaluator = evaluator

    def __repr__(self):
        return '<Oper {} {}/{}>'.format(self.oper, self.lprio, self.rprio)


def prefix_unary_evaluator(parser):
    oper = parser.operators_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [parser.values_stack.pop()]))


def postfix_unary_evaluator(parser):
    oper = parser.operators_stack.pop()
    parser.values_stack.append(CompositeNode('post'+oper.oper, [parser.values_stack.pop()]))


def binary_evaluator(parser):
    oper = parser.operators_stack.pop()
    val2 = parser.values_stack.pop()
    val1 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode(oper.oper, [val1, val2]))


class Parser:
    def __init__(self):
        self.prefix_actions = {}
        self.prefix_operators = {}
        self.infix_operators = {}
        self.postfix_actions = {}
        self.postfix_operators = {}
        self.reset()

    def reset(self):
        self.waiting_value = True
        self.values_stack = []
        self.operators_stack = []

    def register_prefix_action(self, oper, action):
        if type(oper) is str:
            self.prefix_actions[oper] = action
        else:
            for op in oper:
                self.prefix_actions[op] = action

    def register_prefix_operator(self, oper, rprio, evaluator=None):
        if evaluator is None:
            evaluator = prefix_unary_evaluator
        if type(oper) is str:
            self.prefix_operators[oper] = OperatorDesc(oper, -1, rprio, evaluator)
        else:
            for op in oper:
                self.prefix_operators[op] = OperatorDesc(op, -1, rprio, evaluator)

    def register_infix_operator(self, oper, lprio, rprio, evaluator=None):
        if evaluator is None:
            evaluator = binary_evaluator
        if type(oper) is str:
            self.infix_operators[oper] = OperatorDesc(oper, lprio, rprio, evaluator)
        else:
            for op in oper:
                self.infix_operators[op] = OperatorDesc(op, lprio, rprio, evaluator)

    def register_postfix_action(self, oper, action):
        if type(oper) is str:
            self.postfix_actions[oper] = action
        else:
            for op in oper:
                self.postfix_actions[op] = action

    def register_postfix_operator(self, oper, lprio, evaluator=None):
        if evaluator is None:
            evaluator = postfix_unary_evaluator
        if type(oper) is str:
            self.postfix_operators[oper] = OperatorDesc(oper, lprio, -1, evaluator)
        else:
            for op in oper:
                self.postfix_operators[op] = OperatorDesc(op, lprio, -1, evaluator)

    def evaluate_operator(self):
        self.operators_stack[-1].evaluator(self)

    def push_operator(self, oper):
        # prefix operators (marked with oper.lprio == -1) never trigger the evaluation of pending operators
        if oper.lprio >= 0:
            while len(self.operators_stack) > 0 and self.operators_stack[-1].rprio >= oper.lprio:
                self.evaluate_operator()
        self.operators_stack.append(oper)
        # postfix operators (marked with oper.rprio == -1) are never put in pending state
        if oper.rprio < 0:
            self.evaluate_operator()

    def parse_for_value(self, tk):
        if tk.kind == 'NUMBER' or tk.kind == 'ID':
            self.values_stack.append(Node(tk))
            self.waiting_value = False
        elif tk.lexem in self.prefix_actions:
            self.prefix_actions[tk.lexem](self)
        elif tk.lexem in self.prefix_operators:
            self.push_operator(self.prefix_operators[tk.lexem])
        else:
            raise RuntimeError('{} is not a prefix operator or a value'.format(tk.lexem))

    def parse_for_operator(self, tk):
        if tk.lexem in self.postfix_actions:
            self.postfix_actions[tk.lexem](self)
        elif tk.lexem in self.postfix_operators:
            self.push_operator(self.postfix_operators[tk.lexem])
        elif tk.lexem in self.infix_operators:
            self.waiting_value = True
            self.push_operator(self.infix_operators[tk.lexem])
        else:
            raise RuntimeError('{} is not a postfix or an infix operator'.format(tk.lexem))

    def parse(self, s):
        self.reset()
        for tk in lexer.tokenize(s):
            if self.waiting_value:
                self.parse_for_value(tk)
            else:
                self.parse_for_operator(tk)
        if self.waiting_value:
            self.dump()
            raise RuntimeError('missing value')
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


def prefix_open_parenthesis(parser):
    parser.dump()
    raise RuntimeError('Unclosed open parenthesis')


def infix_open_parenthesis(parser):
    parser.dump()
    raise RuntimeError('Unclosed open parenthesis')


def prefix_close_parenthesis(parser):
    op1 = parser.operators_stack.pop()
    if op1.oper != '(' or op1.evaluator != infix_open_parenthesis:
        parser.dump()
        raise RuntimeError('Empty parenthesis')
    val1 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode('call', [val1]))
    parser.waiting_value = False


def postfix_close_parenthesis(parser):
    op1 = parser.operators_stack.pop()
    op2 = parser.operators_stack.pop()
    if op2.oper != '(':
        parser.dump()
        raise RuntimeError('Unopened close parenthesis')
    if op2.evaluator == infix_open_parenthesis:
        val1 = parser.values_stack.pop()
        val2 = parser.values_stack.pop()
        if type(val1) == CompositeNode and val1.token == ',':
            args = [val2] + val1.children
        else:
            args = [val2, val1]
        parser.values_stack.append(CompositeNode('call', args))
    else:
        parser.values_stack[-1].parenthesis = True


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
    parser.values_stack.append(CompositeNode('?', [val3, val2, val1]))


def infix_open_brackets(parser):
    parser.dump()
    raise RuntimeError('Unclosed open bracket')


def postfix_close_brackets(parser):
    op1 = parser.operators_stack.pop()
    op2 = parser.operators_stack.pop()
    if op2.oper != '[' or op2.evaluator != infix_open_brackets:
        parser.dump()
        raise RuntimeError('Unopened close bracket')
    val1 = parser.values_stack.pop()
    val2 = parser.values_stack.pop()
    parser.values_stack.append(CompositeNode('get', [val2, val1]))


def coma_evaluator(parser):
    oper = parser.operators_stack.pop()
    val2 = parser.values_stack.pop()
    val1 = parser.values_stack.pop()
    if type(val1) is CompositeNode and val1.token == ',' and not val1.parenthesis:
        val1.children.append(val2)
        parser.values_stack.append(val1)
    else:
        parser.values_stack.append(CompositeNode(oper.oper, [val1, val2]))


def cexp_parser():
    parser = Parser()
    parser.register_prefix_operator('(', 0, prefix_open_parenthesis)
    parser.register_postfix_operator(')', 1, postfix_close_parenthesis)
    parser.register_prefix_action(')', prefix_close_parenthesis)
    parser.register_postfix_operator(']', 1, postfix_close_brackets)
    parser.register_infix_operator(',', 2, 2, coma_evaluator)
    parser.register_infix_operator(['=', '*=', '/=', '%=', '+=', '-=', '<<=', '>>=', '&=', '|=', '^='], 4, 3)
    parser.register_infix_operator('?', 6, 0, infix_question)
    parser.register_infix_operator(':', 1, 5, infix_colon)
    parser.register_infix_operator('||', 8, 8)
    parser.register_infix_operator('&&', 10, 10)
    parser.register_infix_operator('|', 12, 12)
    parser.register_infix_operator('^', 14, 14)
    parser.register_infix_operator('&', 16, 16)
    parser.register_infix_operator(['==', '!='], 18, 18)
    parser.register_infix_operator(['<', '>', '<=', '>='], 20, 20)
    parser.register_infix_operator(['<<', '>>'], 22, 22)
    parser.register_infix_operator(['+', '-'], 24, 24)
    parser.register_infix_operator(['*', '/', '%'], 26, 26)
    parser.register_infix_operator('**', 28, 27)
    parser.register_prefix_operator(['+', '-', '++', '--', '&', '*', '~', '!'], 30)
    parser.register_postfix_operator(['++', '--', '.', '->'], 32)
    parser.register_infix_operator('(', 32, 0, infix_open_parenthesis)
    parser.register_infix_operator('[', 32, 0, infix_open_brackets)
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
