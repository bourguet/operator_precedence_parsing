#! /usr/bin/env python3

import rd_to_pratt_5 as parser
import rd_to_pratt_tests


def check_parsing(s, expected):
    rd_to_pratt_tests.check_parsing(parser.parser(), s, expected)


rd_to_pratt_tests.all_tests(check_parsing)
