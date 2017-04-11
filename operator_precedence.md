# Operator precedence parsing

This is a parser for the same C-like expression language than shunting_yard.py but
implemented following the operator precedence algorithm.  The class of grammars
it is able to parse is called the operator grammars and is characterized by 

- no production has consecutive non-terminals
- it is inversible: you can deduce the non-terminal from the production
- there are some more consistency conditions

Note that this algorithm is unable to handle unary operators which don't have the 
same priority as the binary one.