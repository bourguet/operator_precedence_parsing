#! /usr/bin/env python3

import shunting_yard
import andychu_cexp_tests
import jmb_cexp_tests


def check_parsing(s, expected):
    jmb_cexp_tests.check_parsing(shunting_yard.cexp_parser(), s, expected)


andychu_cexp_tests.all(check_parsing)
jmb_cexp_tests.all_tests(check_parsing)
