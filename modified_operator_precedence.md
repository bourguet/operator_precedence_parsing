# Modified operator precedence parsing

This is a parser for the same C-like expression language than shunting_yard.py but
implemented using a modified operator precedence algorithm.  The out of the book
operator precedence algorithm is unable to handle unary operators which don't have the 
same priority and associativity as the binary one and can not drive its parsing
decision of a difference between prefix and postfix operator.  The modifications
here is a tentative to solve these issues.

The principle is the same as the one driving pre- and post- operators in shunting
yard: introduce a notion of pre and pos operators.  Instead of being driven by the
manual switch between `waiting_value` and `not waiting_value`, here one take the
advantage of the unified stack (shunting yard has two stacks, operator precedence
has one) and check if the top of stack is the result of a reduction or not to determine
the position.