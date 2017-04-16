# Recursive operator precedence parsing

This is a parser for the same C-like expression language than shunting_yard.py but
implemented using a recursive implementation of the algorithm used in
`modified_operator_precedence.py`.

One aspect of the recursive implementation is that this parser -- as opposed to the
other parsers presented in this repository -- is a pull parser instead of a push one.
By that I mean that the other parsers have a loop on the token stream and then handle
the current token, this one keep the current token and has a procedure to get the next
one when desired (that occurs in the same function, but at different level in the
call stack thus that aspect can not be easily modified).

As it is a recursive implementation of the same algorithm as modified operator
precedence, it admits the same external interface.  All the changes compared
to `modified_operator_precedence.py`. are in the class `Parser`.