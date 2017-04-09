# Operator precedence parsers

Here are some parsers applying variant of operator precedence.

- dijkstra.py is a implementation trying to follow Dijkstra's description of the
  shunting-yard algorithm.
  
- shunting_yard.py is a parser for C-like expressions.  It is quite full featured (unary
  prefix and postfix, function calls, ternary operator)