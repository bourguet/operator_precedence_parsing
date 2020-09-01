# Operator precedence parsers

## Introduction

This is a repository of expression parsers.  It contains implementations following
closely the description of the parsers in the literature (`dijkstra.py`, `knuth.py` and
`operator_precedence.py`) as well as variations featured enough to parse C expressions
(`shunting_yard.py`, `modified_operator_precedence.py`, `recursive_operator_precedence.py`
and `pratt.py`).

This work was triggered by Andy Chu [blog posts](https://www.oilshell.org/blog/2017/03/31.html)
and [repository](https://github.com/andychu/pratt-parsing-demo) on Pratt parsers.
I first though that Pratt parser was a recursive implementation of the shunting yard algorithm.
That is retrospectively lacking of though clarity: the major characteristic of the shunting
yard algorithm is the use of two stacks, one for operands, one for operators. Operator
precedence was a better target for unification with Pratt.  Even replacing shunting yard by
operator precedence,I was mistaken as it can be clearly see when comparing the `parse_to`
method of both Pratt and recursive operator precedence here. Pratt is applying its evaluation
function as soon as a symbol is recognized, operator precedence is applying it when the whole
expression has been recognized.

## Overview

Here is a small description of the expression parsers presented in this repository.

- `dijkstra.py` is a implementation trying to follow Dijkstra's description of the
  shunting-yard algorithm.
  
- `knuth.py` is an implementation of Knuth's "modern" translation algorithm of 1962.

- `operator_precedence.py` is a parser for C-like expressions using the operator
  precedence algorithm as described in the literature.
  
- `shunting_yard.py` is a parser for C-like expressions using a modified shunting yard
  algorithm to improve error detection and add handling for things not handled by the
  Dijkstra one.  It is quite full featured (unary prefix and postfix, function calls,
  ternary operator).
  
- `modified_operator_precedence.py` is a parser for C-like expressions using a modified
  operator precedence algorithm.  It adds the possibility to make the difference
  between prefix and postfix operators.
  
- `recursive_operator_precedence.py` is a recursive implementation of
  `modified_operator_precedence.py` and adds no new features to it.  Its purpose is to be
  compared with Pratt algorithm.

- `pratt.py` is an implementation of Pratt parser, also known as _Top Down Operator
  Precedence_, which is the name used by Vaughan Pratt, or _Precedence Climbing_.

- `pratt_tdop_parser.py` is an implementation of Pratt parser by Calin Barbat.  Since
  it was contributed I wrote `pratt.py` which is closer in structure and naming convention
  to the other parsers here and thus better suited for the purpose of this repository:
  comparing the algorithms.
   
## Relationships

`dijkstra.py` and `shunting_yard.py` are strongly related.  The first is a style
exercise of implementing the algorithm described in the paper while avoiding to solve
problems not described in the paper such as error handling, ternary operator, unary
operator handling without lexer intervention...  `shunting_yard.py` is yet another
variation on the way I've always implemented the shunting yard algorithm when I needed
an expression parser.  The main characteristic of those algorithms, along with tagging
operators with priorities which is common to all parsers showed here, is the use of
two stacks: one for values, one for operators.  `shunting_yard.py` adds to that a state
which indicates if the parser is expecting an operator or a value.  That state allows
two things: improved error detection and making a difference between prefix and postfix
operators.

`knuth.py` uses a single stack instead of an operator and an operand one.

The algorithm described in the literature under the name of operator precedence also use
a single stack and is implemented in `operator_precedence.py`.  The literature I've
consulted does not consider the case where pre and post contexts can have different
priorities; `modified_operator_precedence.py` shows how to do so.  The result is quite pleasing
to me: it can parses everything I wanted with less kludges than `shunting_yard.py` (by that
I mean the presence of the `action` rules -- which is used to handle `f()` -- and the
explicit manipulation of the parser states in the various evaluators -- especially when
it comes to set `waiting_value`), and I'm more confident about the possibility to detect
input errors in a systematic way.  `recursive_operator_precedence.py` is a recursive
implementation of `modified_operator_precedence.py` and brings nothing new.  Well, it does
not have to iterate on the stack to find the handle, but that's something which could be done
also in a non-recursive implementation.

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
influence the parsing). That reduction is made in `operator_precedence.py`, 
`modified_operator_precedence.py` and `recursive_operator_precedence.py`.

That technique is not that intuitive (equality of priority means that the operators
are part of a distfix construct), it is possible to remove the distinction between
giving the priority to the second operator and the distfix construct (the parser
has to do the same thing for both) to the node building (and the node building has
then to modify the stacks).  That is done in `shunting_yard.py` and is needed in
the weak precedence algorithm.  Having different priorities is then present only
to handle right associative operators and some special cases (parenthesis for
instance).

It is possible to even reduce to a simple table of priority if you add a tagging
for right associative operators.  You have then to modify the comparison function
to take the associativity into account.  And you have to introduce special handling
for parenthesis and other related special cases.  `dijkstra.py` shows the special
handling of the parenthesis.

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
targeted at students.

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
  Describe operator precedence and state that it is a useful method for hand written
  parsers in conjunction with recursive descend.  Describe also simple and weak
  precedence. 
 
- _Compilers: Principles, Techniques and Tools_, A.V. Aho, R. Sethi and J.D. Ullman.
  The second dragon book.  Very similar description of precedence techniques than
  in the first dragon book.
  
- _Compilers: Principles, Techniques and Tools, 2nd edition_, A.V. Aho, M.S. Lam,
  R. Sethi and J.D. Ullman.  The third dragon book.  Seems to have dropped the
  description of operator precedence.

- _Crafting a compiler_, C.N. Fisher and R.J. LeBlanc, Jr.  Show a quick overview
  of simple precedence and operator precedence, but does not consider them as anything
  more than precursors of LR parsing.

- _Making a translator for Algol 60_, E.W. Dijkstra, second part of M35 available at
  [http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF](http://www.cs.utexas.edu/~EWD/MCReps/MR35.PDF).
  `dijkstra.py` aims to be an implementation of the algorithm described there.

- _A History of Writing Compilers_, D.E. Knuth, 1962, reprinted in _Selected Papers
  on Computer Languages_, 2003.  `knuth.py` aims to be an implementation of the
  algorithm described in Figure 4, _A version of the "modern" translation algorithm_.

- _Top Down Operator Precedence_, Vaughan R. Pratt, 1973 available at
  [http://tdop.github.io/](http://tdop.github.io/).  Original description of
  Pratt's algorithm.
  
- _Pratt Parsing Index and Updates_, Andy Chu, blog post available at
  [http://www.oilshell.org/blog/2017/03/31.html](http://www.oilshell.org/blog/2017/03/31.html),
  the blog entry which triggered me into writing this.
  
## Potential future work

This style exercise already fulfilled more than its starting goal.  I'll probably go back
to other interests shortly.  Yet, there are some points I may do in a more or less close
future.

- Improve the notes and descriptions.

- Fix bugs and clean up the parsers.

- Maybe implementation of other historical description of precedence based algorithms
  if they seem to offer an interest.

- Examine variations between push and pull parsers and how they work when embedded in
  a wider context (says in a recursive descend parser for the non-expression part). The
  current parsers are push parsers but they depend on a termination phase which is
  triggered at the end of input.  That's not viable if partial parsing of input is needed.

Some things I'll probably not do:

- (well I did!, still keeping this until I move or rewrite all the relevant information)
  implement precedence climbing and Pratt.  After reading Pratt's paper,
  I think that 
  implementing them would not bring me something over what I got from understanding
  [Andy Chu's implementation](https://github.com/andychu/pratt-parsing-demo).  I had
  the mistaken impression that they were "just" replacing an explicit stack with the
  call stack of the implementation language but that was not clear enough from Andy's
  code.  It was not clear because that's not the case.  Compare Pratt's algorithm with
  `recursive_operator_precedence.py`, which is a recursive implementation of operator
  precedence, to see the difference.  Pratt and operator climbing are really top down
  techniques: they call semantic actions as soon as possible, they don't delay the call
  until the whole handle is seen as operator precedence does.  My current characterization
  is that they are to LL parsing and recursive descent what operator precedence is to LR
  and shift-reduce: they use a precedence relationship to simplify the grammar description
  and parser implementation at the cost of producing a skeleton parse tree instead of
  a full parse tree (i.e. they don't show unit rule application).  That cost is small:
  unit rule are more noise than anything else in the context of expressions and are absent
  of most if not all related AST.  That's probably what makes them well suited to be
  integrated with a recursive descent parser for the rest of the language as they are
  a recursive descent variant and thus offer the same flexibility, for instance they allow
  the parsing to be partially driven by more semantic considerations (what' `(a)+b` in C,
  a cast or an addition? you can solve that without playing lexer tricks in a recursive descent
  parser) and a convenient place to do error handling and recovery.

- implement the simple and weak precedence algorithms.  The additional power they give does
  not seem a good return for the additional effort and is not useful for parsing expression.
  I feel that if you need it, you are better to use either a recursive descent parser or a parser
  generator based on LALR(1), LL(1) or even more powerful.
