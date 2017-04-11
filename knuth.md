# Knuth's "modern" translation algorithm

This is the algorithm of Figure 4.  

Table 1 show the semi-colon as an operator with a 0 priority, but nowhere it is described
how to handle it and considering it as a operator does not seem right as it would fill
up the stack.  My guess is that the stack show be emptied at that time.  I've not tried to
handle it.

`:=` is not considered as a binary operator (clearly: see the main text describing Box 2
and the fact that it has its own arrow out of Box 6), but I'm using the same routine
for evaluation as the binary operators. 

There is a bug in the handling of `@` considered as marker for end of input.  The main text
describing Box 2 implies that it should be put on the stack and the next symbol should be
read.  I'm instead going to the loop emptying the stack so that we can reach the Done state.
 
If I'm not mistaken, there is no mention about the issue of handling - as both a unary and
binary operator.

The algorithm is presented as a flowchart.  And that flowchart has the characteristic
that it is not reducible to a structured program.  I'd have used a `goto` to handle that
in another language, but that's not possible in Python.  Thus I'm using `break`, `continue`
and a boolean variable to achieve the same effect.  It could have been possible to do that
more cleanly, but I wanted to stick to the original structure (that book has a nice totally
unreadable flowchart on a double page for another article, it gives to 2017's readers 
another meaning to spaghetti code -- the 2002's postscript states that the flowchart is
probably the most complex flowchart published)

## References

- _A History of Writing Compilers_, D.E. Knuth, 1962, reprinted in _Selected Papers
  on Computer Languages_, 2003.