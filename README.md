# Operator precedence parsers

## Overview

Here are some parsers applying variant of operator precedence.

- `dijkstra.py` is a implementation trying to follow Dijkstra's description of the
  shunting-yard algorithm.
  
- `knuth.py` is an implementation of Knuth's "modern" translation algorithm of 1962

- `shunting_yard.py` is a parser for C-like expressions using a modified shunting yard
  algorithm to improve error detection and add handling for things not handled by the
  Dijkstra one.  It is quite full featured (unary prefix and postfix, function calls,
  ternary operator).
  
- `operator_precedence.py` is a parser for C-like expression using the operator
  precedence algorithm.
  
- `modified_operator_precedence.py` is a parser for C-like expressions using a modified
  operator precedence algorithm.  It adds the possibility to make the difference
  between prefix and postfix operators.
  
## Relationships

`dijkstra.py` and `shunting_yard.py` are strongly related.  The first is a style
exercise of implementing the algorithm described in the paper while avoiding to solve
problems not described in the papers such as error handling, ternary operator, unary
operator handling without lexer intervention...  `shunting_yard.py` is yet another
variation on the way I've always implemented the shunting yard algorithm when I needed
an expression parser.  The main characteristic of those algorithms, along with tagging
operators with priorities which is common to all parsers showed here, is the use of
two stacks: one for values, one for operators.  `shunting_yard.py` adds to that a state
which indicates if the parser is expecting an operator or a value.  That state allows
two things: error detection and making a difference between prefix and postfix operators.

Moving to one combined stack and thus to a clear shift-reduce algorithm gave 
`operator_precedence.py` when implemented according to the descriptions in the literature,
and `modified_operator_precedence.py` when trying to adapt the previous result so that it
can work with different priority for pre and post context.  The result is quite pleasing
to me: it can parses everything I wanted with less kludges than `shunting_yard.py` (by that
I mean the presence of the `action` rules -- which is used to handle `f()` -- and the
explicit manipulation of the parser states in the various evaluators -- especially when
it comes to set `waiting_value`), and I'm more confident about the possibility to detect
input errors.

`knuth.py` shares the single stack characteristic with `operator_precedence.py', but in spirit
is closer to `dijkstra.py` and `shunting_yard.py`.

## On priority and associativity

The more general form of priority description is a full matrix, stating for each
operator pairs if
- the first has priority
- they are part of a distfix construct
- the second has priority
- they can not be consecutive

That full generality is the one described in the literature for operator precedence
and simple precedence parsing, but in practice the matrix is reduced using a table
giving a left and right priority for each pair and comparing the right priority of
the left operator with the left priority of the right operator. That technique has
for consequence that the error case can no more directly detected (and thus error
detection is moved to a more semantic analysis phase instead of being able to
influence the parsing). That reduction is made in operator_precedence.py and
modified_operator_precedence.py.

That technique is not that intuitive (equality of priority means that the operators
are part of a distfix construct), it is possible to remove the distinction between
giving the priority to the second operator and the distfix construct (the parser
has to do the same thing for both) to the node building (and the node building has
then to modify the stacks).  That is done in the shunting_yard.py and is needed in
the weak precedence algorithm.  Having different priority is then present only
for right associative operators and parenthesis.

It is possible to even reduce to a simple table of priority if you add a tagging
for right associative operators.  You have then to modify the comparison function
to take the associativity into account.  And you have to introduce special handling
of parenthesis.  dijkstra.py shows the special handling of the parenthesis.

## On operator classification

- unary means one argument
- binary means two arguments
- n-ary means n arguments
- prefix means before the argument
- infix means between the argument
- postfix means after the argument
- distfix means that the operator is split

Examples: 

- grouping parenthesis are prefix, distfix, postfix and unary.
 
- function call parenthesis are postfix, distfix and binary (or n-ary if you consider
all the arguments separated with the comas)

## References

The first two books are monographies, the next four are text books
targeted at students.  The last two are papers which have only an historical
interest now but served as basis for `dijkstra.py` and `knuth.py`.

Books tend to mention operator precedence, simple and weak precedence techniques
which can be described in a the formal context of shift-reduce
parsing and thus related to LR(1) parsing.  None seem to mention the shunting yard
algorithm by name nor describe the use of two stacks which seem to me to be its
major feature contrasting it from operator precedence.   None mention the recursive
implementations (precedence climbing, Pratt), excepted that Grune and Jacobs have
the paper in their 227-page 
[Annotated Bibliography](https://dickgrune.com/Books/PTAPG_2nd_Edition/CompleteList.pdf).

- _The Theory of Parsing, Translation and Compiling, Volume 1: Parsing_ by A.V. Aho
and J.D. Ullman.  And oldie (1972) but the more theoretical book I've looked at on
the subject.  Operator precedence, simple precedence, weak precedence are
considered as well as other techniques, everything considered in a grammar parsing
context.
 
- _Parsing Techniques, A Practical Guide_ by D. Grune and C.J.H. Jacobs.  The more
  complete review of parsing techniques I know.

- _Principle of Compiler Design_, A.V. Aho and J.D. Ullman.  The first dragon book.
 
- _Compilers: Principles, Techniques and Tools_, A.V. Aho, R. Sethi and J.D. Ullman.
  The second dragon book.  Very similar description of precedence techniques than
  in the first dragon book.
  
- _Compilers: Principles, Techniques and Tools, 2nd edition_, A.V. Aho, M.S. Lam,
  R. Sethi and J.D. Ullman.  The third dragon book.  Seems to have dropped the
  description of operator precedence.

- _Crafting a compiler_, C.N. Fisher and R.J. LeBlanc, Jr.  

- _Making a translator for Algol 60_, E.W. Dijkstra, second part of M35 available at
  [http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF](http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF).
  `dijkstra.py` aims to be an implementation of the algorithm described there.

- _A History of Writing Compilers_, D.E. Knuth, 1962, reprinted in _Selected Papers
  on Computer Languages_, 2003.  `knuth.py` aims to be an implementation of the
  algorithm described in Figure 4, _A version of the "modern" translation algorithm_.

## Potential future work

This style exercise already fulfilled more its goal.  I'll probably go back to other
interests shortly.  Yet, there are some points I may do in a more or less close
future.

- Improve the notes and descriptions.

- Fix bugs and clean up the parsers.

- Implement recursive precedence parsers (precedence climbing, Pratt) in order to get
  a better feel about how they are related to the one currently implemented.  I've the
  impression -- but not yet backed up by such an experiment -- that they are "just"
  replacing an explicit stack with the call stack of the implementation language.  That
  probably makes them well suited to be integrated with a recursive descent parser for
  the rest of the language if needed, included the possibility of switching back to
  recursive descend for sub-expressions.

- Maybe implementation of other historical description of precedence based algorithms
  if they seem to offer an interest.

- Examine variations between push and pull parsers and how they work when embedded in
  a wider context (says in a recursive descend parser for the non-expression part). The
  current parsers are push parsers but they depend on a termination phase which is
  triggered at the end of input.  That's not viable if partial parsing of input is needed.

Something I'll probably not do is to implement the simple and weak precedence
algorithms.  The additional power they give does not seem a good return for the
additional effort and is not useful for parsing expression. I feel that if you
need it, you are better to use either a recursive descent parser or a parser
generator based on LALR(1), LL(1) or even more powerful.
