# Some tests for rd_to_pratt


def all_tests(t_parse):
    t_parse('a+b', '(+ a b)')
    t_parse('a-b', '(- a b)')
    t_parse('a+b-c', '(- (+ a b) c)')
    t_parse('a-b+c', '(+ (- a b) c)')
    t_parse('a*b', '(* a b)')
    t_parse('a==b', '(== a b)')
    t_parse('a || b', '(|| a b)')
    t_parse('a && b', '(&& a b)')
    t_parse('a * b == c', '(== (* a b) c)')
    t_parse('a == b * c', '(== a (* b c))')
    t_parse('a * b + c * d == a * b + c * d || a && b', '(|| (== (+ (* a b) (* c d)) (+ (* a b) (* c d))) (&& a b))')


def check_parsing(parser, s, expected):
    try:
        tree = parser.parse(s)
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
