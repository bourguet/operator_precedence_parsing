#! /usr/bin/env python3

import operator_precedence
import andychu_cexp_tests
import jmb_cexp_tests


def check_parsing(s, expected):
    p = operator_precedence.cexp_parser()
    try:
        tree = p.parse(s)
        sexpr = repr(tree)
        if sexpr != expected:
            if expected == '':
                print('Failing to parse: {} => {}'.format(s, sexpr))
            else:
                print('UNEXPECTED Failure to parse: {} => {} != {}'.format(s, sexpr, expected))
    except RuntimeError as error:
        if expected == '':
            print('Exception while parsing {} => {}'.format(s, error))
        else:
            print('UNEXPECTED exception while parsing: {} => {}, expected {}'.format(s, error, expected))


andychu_cexp_tests.all(check_parsing)
jmb_cexp_tests.all_tests(check_parsing)
