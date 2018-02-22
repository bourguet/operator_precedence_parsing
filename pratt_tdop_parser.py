#! /usr/bin/env python3
"""
pratt_tdop_parser.py: Parse shell-like and C-like arithmetic.
"""

import sys
import lexer
from lexer import Token
from tree import Node, CompositeNode

#
# Default parsing functions give errors
#

class ParseError(RuntimeError):
    pass

def NullError(p, token, rbp):
    raise ParseError("%s can't be used in prefix position" % token)

def LeftError(p, token, rbp, left):
    # Hm is this not called because of binding power?
    raise ParseError("%s can't be used in infix position" % token)

#
# Parser definition
#

# min and max binding powers
MIN_BP = 0
MAX_BP = 10000

class LeftInfo(object):
    def __init__(self, led=None, lbp=MIN_BP, rbp=MIN_BP, nbp=MIN_BP):
        self.led = led or LeftError
        self.lbp = lbp
        self.rbp = rbp
        self.nbp = nbp

class NullInfo(object):
    def __init__(self, nud=None, lbp=MIN_BP, rbp=MIN_BP, nbp=MIN_BP):
        self.nud = nud or NullError
        self.lbp = lbp
        self.rbp = rbp
        self.nbp = nbp

class Parser(object):
    """Recursive TDOP parser."""

    def __init__(self):
        self.lexer = None  # iterable
        self.token = None  # current token
        self.null_lookup = {}
        self.left_lookup = {}

    """Specification for a TDOP parser."""
    
    def LookupNull(self, token):
        """Get the parsing function and precedence for a null position token."""
        try:
            null_info = self.null_lookup[token]
        except KeyError:
            raise ParseError('Unexpected token %r' % token)
        return null_info

    def LookupLeft(self, token):
        """Get the parsing function and precedence for a left position token."""
        try:
            left_info = self.left_lookup[token]
        except KeyError:
            raise ParseError('Unexpected token %r' % token)
        return left_info

    def _RegisterNud(self, lbp, rbp, nbp, nud, tokens):
        if type(tokens) is str:
            self.null_lookup[tokens] = NullInfo(
                nud=nud, lbp=lbp, rbp=rbp, nbp=nbp)
            if tokens not in self.left_lookup:
                self.left_lookup[tokens] = LeftInfo(LeftError)  # error        
        else:
            for token in tokens:
                self.null_lookup[token] = NullInfo(
                    nud=nud, lbp=lbp, rbp=rbp, nbp=nbp)
                if token not in self.left_lookup:
                    self.left_lookup[token] = LeftInfo(LeftError)  # error

    def _RegisterLed(self, lbp, rbp, nbp, led, tokens):
        if type(tokens) is str:
            if tokens not in self.null_lookup:
                self.null_lookup[tokens] = NullInfo(NullError)  # error
            self.left_lookup[tokens] = LeftInfo(
                led=led, lbp=lbp, rbp=rbp, nbp=nbp)
        else:
            for token in tokens:
                if token not in self.null_lookup:
                    self.null_lookup[token] = NullInfo(NullError)  # error
                self.left_lookup[token] = LeftInfo(
                    led=led, lbp=lbp, rbp=rbp, nbp=nbp)

    def nilfix(self, bp, nud, tokens):
        self._RegisterNud(MIN_BP, MIN_BP, MAX_BP, nud, tokens)

    def prefix(self, bp, nud, tokens):
        self._RegisterNud(MIN_BP, bp, MAX_BP, nud, tokens)

    def suffix(self, bp, led, tokens):
        self._RegisterLed(bp, MIN_BP, MAX_BP, led, tokens)

    def infixL(self, bp, led, tokens):
        self._RegisterLed(bp, bp, bp + 1, led, tokens)

    def infixR(self, bp, led, tokens):
            self._RegisterLed(bp, bp - 1, bp + 1, led, tokens)

    def infixN(self, bp, led, tokens):
            self._RegisterLed(bp, bp, bp, led, tokens)

    def AtToken(self, token_type):
        """Test if we are looking at a token."""
        return self.token.kind == token_type

    def Next(self):
        """Move to the next token."""
        try:
            t = self.lexer.__next__()
            if t.kind in ['OPER', 'SYNT']:
                t.kind = t.lexem
        except StopIteration:
            t = Token('eof', 'eof')
        self.token = t

    def Eat(self, val):
        """Assert the value of the current token, then move to the next token."""
        if val and not self.AtToken(val):
            raise ParseError('expected %s, got %s' % (val, self.token))
        self.Next()

    # Examples:
    # If we see 1*2+ , rbp = 27 and lbp = 25, so stop.
    # If we see 1+2+ , rbp = 25 and lbp = 25, so stop.
    # If we see 1**2**, rbp = 26 and lbp = 27, so keep going.
    def ParseUntil(self, rbp):
        """ Parse to the right, eating tokens until we encounter a token with binding power LESS THAN OR EQUAL TO rbp. """
        if self.AtToken('eof'):
            raise ParseError('Unexpected end of input')
        if rbp < MIN_BP:
            raise ParseError(
                'rbp=%r must be greater equal than MIN_BP=%r.' %
                (rbp, MIN_BP))
        t = self.token
        self.Next()
        null_info = self.LookupNull(t.kind)
        node = null_info.nud(self, t, null_info.rbp)
        nbp = null_info.nbp  # next bp
        lbp = self.LookupLeft(self.token.kind).lbp
        while rbp < lbp and lbp < nbp:
            t = self.token
            self.Next()
            left_info = self.LookupLeft(t.kind)
            node = left_info.led(self, t, left_info.rbp, node)
            nbp = left_info.nbp  # next bp
            lbp = self.LookupLeft(self.token.kind).lbp
        return node

    def parse(self, s):
        self.lexer = lexer.tokenize(s)
        self.Next()
        r = self.ParseUntil(0)
        if not self.AtToken('eof'):
            raise ParseError('There are unparsed tokens: %r' % self.token)
        return r

#
# Null Denotations -- tokens that take nothing on the left
#
def NullLiteral(p, token, rbp):
    """ Name or number """
    return Node(token)

def NullParen(p, token, rbp):
    """ Arithmetic grouping """
    r = p.ParseUntil(rbp)
    p.Eat(')')
    r.parenthesis = True
    return r

def NullPrefixOp(p, token, rbp):
    """Prefix operator
    Low precedence:  return, raise, etc.
      return x+y is return (x+y), not (return x) + y
    High precedence: logical negation, bitwise complement, etc.
      !x && y is (!x) && y, not !(x && y)
    """
    r = p.ParseUntil(rbp)
    return CompositeNode(token.kind, [r])

def NullIncDec(p, token, rbp):
    """ ++x or ++x[1] """
    right = p.ParseUntil(rbp)
    if right.token not in ('ID', 'get') and (
            right.token is Token and right.token.kind not in ('ID', 'get')):
        raise ParseError("Can't assign to %r (%s)" % (right, right.token))
    return CompositeNode(token.kind, [right])

#
# Left Denotations -- tokens that take an expression on the left
#

def LeftIncDec(p, token, rbp, left):
    """ i++ and i-- """
    # if left.token.kind not in ('ID', 'get'):
    #  raise tdop.ParseError("Can't assign to %r (%s)" % (left, left.token))
    token.kind = 'post' + token.kind
    return CompositeNode(token.kind, [left])

def LeftFactorial(p, token, rbp, left):
    """ 2! """
    token.kind = 'post' + token.kind
    return CompositeNode(token.kind, [left])

def LeftIndex(p, token, unused_rbp, left):
    """ index f[x+1] or f[x][y] """
    if left.token.kind not in ('ID', 'get'):
        raise ParseError("%s can't be indexed" % left)
    index = p.ParseUntil(0)
    p.Eat("]")
    token.kind = 'get'
    return CompositeNode(token.kind, [left, index])

def LeftTernaryOp(p, token, rbp, left):
    """ e.g. a > 1 ? x : y """
    # 0 binding power since any operators allowed until ':'.  See:
    #
    # http://en.cppreference.com/w/c/language/operator_precedence#cite_note-2
    #
    # "The expression in the middle of the conditional operator (between ?  and
    # :) is parsed as if parenthesized: its precedence relative to ?: is
    # ignored."
    true_expr = p.ParseUntil(0)
    p.Eat(':')
    false_expr = p.ParseUntil(rbp)
    children = [left, true_expr, false_expr]
    return CompositeNode(token.kind, children)

def LeftBinaryOp(p, token, rbp, left):
    """ Normal binary operator like 1+2 or 2*3, etc. """
    return CompositeNode(token.kind, [left, p.ParseUntil(rbp)])

def LeftAssignOp(p, token, rbp, left):
    """ Binary assignment operator like x += 1, or a[i] += 1 """
    if left.token not in (
            'ID', 'get') and left.token.kind not in ('ID', 'get'):
        raise ParseError("Can't assign to %r (%s)" % (left, left.token))
    return CompositeNode(token.kind, [left, p.ParseUntil(rbp)])

def LeftComma(p, token, rbp, left):
    """ foo, bar, baz - Could be sequencing operator, or tuple without parens """
    r = p.ParseUntil(rbp)
    if not left.parenthesis and left.token == ',':  # Keep adding more children
        left.children.append(r)
        return left
    children = [left, r]
    return CompositeNode(token.kind, children)

# For overloading of , inside function calls
COMMA_PREC = 10

def LeftFuncCall(p, token, unused_rbp, left):
    """ Function call f(a, b). """
    children = [left]
    # f(x) or f[i](x)
    # if left.token.kind not in ('ID', 'get'):
    #  raise tdop.ParseError("%s can't be called" % left)
    while not p.AtToken(')'):
        # We don't want to grab the comma, e.g. it is NOT a sequence operator.
        children.append(p.ParseUntil(COMMA_PREC))
        if p.AtToken(','):
            p.Next()
    p.Eat(")")
    token.kind = 'call'
    return CompositeNode(token.kind, children)

def cexp_parser():
    parser = Parser()
    """
    Compare the code below with this table of C operator precedence:
    http://en.cppreference.com/w/c/language/operator_precedence
    """
    parser.suffix(310, LeftIncDec, ['++', '--'])
    parser.infixL(310, LeftFuncCall, '(')
    parser.infixL(310, LeftIndex, '[')
    parser.infixL(310, LeftBinaryOp, '.')
    parser.infixL(310, LeftBinaryOp, '->')

    parser.suffix(300, LeftFactorial, '!')

    # 29 -- binds to everything except function call, indexing, postfix ops
    parser.prefix(290, NullIncDec, ['++', '--'])
    parser.prefix(290, NullPrefixOp, ['+', '!', '~', '-'])

    # Right associative: 2 ** 3 ** 2 == 2 ** (3 ** 2)
    parser.infixR(270, LeftBinaryOp, '**')

    parser.infixL(250, LeftBinaryOp, ['*', '/', '%'])
    parser.infixL(230, LeftBinaryOp, ['+', '-'])
    parser.infixL(210, LeftBinaryOp, ['<<', '>>'])
    parser.infixL(190, LeftBinaryOp, ['<', '>', '<=', '>='])
    parser.infixL(170, LeftBinaryOp, ['!=', '=='])
    parser.infixL(150, LeftBinaryOp, '&')
    parser.infixL(130, LeftBinaryOp, '^')
    parser.infixL(110, LeftBinaryOp, '|')
    parser.infixL(90, LeftBinaryOp, '&&')
    parser.infixL(70, LeftBinaryOp, '||')

    parser.infixR(50, LeftTernaryOp, '?')

    # Right associative: a = b = 2 is a = (b = 2)
    parser.infixR(
        30, LeftAssignOp, [
            '=', '+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '&=', '^=', '|='])

    parser.infixL(COMMA_PREC, LeftComma, ',')

    # 0 precedence -- doesn't bind until )
    parser.prefix(0, NullParen, '(')  # for grouping

    # 0 precedence -- never used
    parser.nilfix(0, NullLiteral, ['ID', 'NUMBER'])
    parser.nilfix(0, NullError, [')', ']', ':', 'eof'])
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
