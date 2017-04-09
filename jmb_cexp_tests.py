# Some additional tests, coming mainly from regressions and related examples


def reg_tests(t_parse):
    t_parse('a()', '(call a)')
    t_parse('a(+1)', '(call a (+ 1))')
    t_parse('a()+1', '(+ (call a) 1)')
    t_parse('a, b, c', '(, a b c)')
    t_parse('(a, b, c)', '(, a b c)')
    t_parse('f(a, b, c)', '(call f a b c)')
    t_parse('f(a, b, c), d', '(, (call f a b c) d)')
    t_parse('(a, b, c), d', '(, (, a b c) d)')


def all(t_parse):
    reg_tests(t_parse)
