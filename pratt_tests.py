#! /usr/bin/env python3

import pratt
import andychu_cexp_tests
import jmb_cexp_tests


def check_parsing(s, expected):
    p = pratt.cexp_parser()
    tree = p.parse(s)
    sexpr = repr(tree)
    if sexpr != expected:
        print('Failed: {} => {} != {}'.format(s, sexpr, expected))


andychu_cexp_tests.all(check_parsing)
jmb_cexp_tests.all_tests(check_parsing)
