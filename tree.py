# Simple syntax tree representation used by all the parsers


class Node:
    def __init__(self, token):
        self.token = token
        self.parenthesis = False

    def __repr__(self):
        return self.token.lexem


class CompositeNode(Node):
    def __init__(self, token, children):
        Node.__init__(self, token)
        self.children = children

    def __repr__(self):
        args = ''.join([" " + repr(c) for c in self.children])
        return '(' + self.token + args + ')'
