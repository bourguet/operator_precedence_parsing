#! /usr/bin/env python3

import pratt_tdop_parser
import andychu_cexp_tests
import jmb_cexp_tests


def check_parsing(s, expected):
    p = pratt_tdop_parser.cexp_parser()
    try:
        tree = p.parse(s)
        sexpr = repr(tree)
        if sexpr != expected:
            print('Failed: {} => {} != {}'.format(s, sexpr, expected))
    except RuntimeError as run_error:
        print("Unable to parse '{}': {}".format(s, run_error))


andychu_cexp_tests.all(check_parsing)
jmb_cexp_tests.all_tests(check_parsing)
