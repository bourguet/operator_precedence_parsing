#! /usr/bin/env python3

import shunting_yard
import andychu_cexp_tests
import jmb_cexp_tests


def check_parsing(s, expected):
    p = shunting_yard.cexp_parser()
    tree = p.parse(s)

    sexpr = repr(tree)
    if sexpr != expected:
        print('Failed: {} => {} != {}'.format(s, sexpr, expected))

andychu_cexp_tests.all(check_parsing)
jmb_cexp_tests.all(check_parsing)
