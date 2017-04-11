# Operator precedence parsers

Here are some parsers applying variant of operator precedence.

- dijkstra.py is a implementation trying to follow Dijkstra's description of the
  shunting-yard algorithm.
  
- shunting_yard.py is a parser for C-like expressions using a modified shunting yard
  algorithm to improve error detection and add handling for things not handled by the
  Dijstra one.  It is quite full featured (unary prefix and postfix, function calls,
  ternary operator)
  
- operator_precedence.py is a parser for C-like expression using the operator
  precedence algorithm.
  
- modified_operator_precedence.py is a parser for C-like expressions using a modified
  operator precedence algorithm.  It adds the possibility to make de difference
  between prefix and postfix operators.