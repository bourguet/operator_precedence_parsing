# Dijkstra's shunting yard 

This try to implement the shunting yard algorithm as described by Dijkstra in
[MR35](http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF).

The text makes no mention of right associativity.  In fact assignment is a statement (and
thus can't be chained), and the exponentiation operator is left associative.

MR35 sets the priority of unary - at the same value than the one of multiplication and
division.  The Revised Report's grammar is implies that it is the same as addition
and subtraction.

The text does not mention error detection.  As a consequence, I've implemented very
little of it and the parser will accept strange things. 

## References

- [MR35]()
- [Revised Report on the Algorithmic Language Algol 60](http://www.masswerk.at/algol60/report.htm)

