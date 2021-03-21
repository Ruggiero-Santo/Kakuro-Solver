# Kakuro-Solver
Python implementation of a logic puzzle solver [Kakuro](https://en.wikipedia.org/wiki/Kakuro) using different algorithms of constrained programming, for Artificial Intelligence Fundamentals Exams (2017-18).

Specifically, algorithms have been implemented to reduce the domains of the variables that make up our problem (the boxes to be filled in) Node Consistency and Generalized Arc Consistency (GAC).  
We use the Backtracking algorithm to generate the various solutions in the case in which, after the reduction of the domains, there are several possible solutions of the same Kakuro.

The solution of the puzzle was logically divided into three phases:
 - Reducing the domains through Node Consistency;
 - Solution search using GAC;
 - Backtracking, for the generation of all possible solutions in case there were any.

## Node Consistency
Node Consistency requires that every unary constraint is satisfied by all values in the variable's domain. This condition can be imposed by reducing the domain of each variable to the values that satisfy all unary constraints on that variable. For example, given a variable V with a domain D<sub>V</sub> = \{1,2,3,4\} and a constraint v <= 3, node consistency would limit the domain to \{1,2,3\} and the constraint could then be discarded.  
This preprocessing step simplifies the subsequent steps.
In our case, we do not have unary constraints, so we cannot discard the constraint, but we can still reduce the domain of the variable according to the possible configurations for our associated sum. This is very useful in cases such as the sum of 3 in two boxes or 7 in three boxes that have as their only configurations {1,2} and {1,2,4} respectively.

## General Arc Consistency (GAC)
A variable is arc consistent with another if each of its admissible values is consistent with some admissible value of the second variable. Formally, a variable <i>x</i> is arc-consistent with another variable <i>y</i> if, for each value D<sub>x</sub> there exists a value in $D_y$ such that ($x_i$, $y_j$) satisfies the binary constraint between $x$ and $y$. A problem is arc-consistent if every variable is consistent with every other variable.  
A simplistic algorithm on variable pairs enforces arc-consistency on all possible pairs until no domain changes in one iteration. The AC-3 algorithm does exactly this by ignoring constraints that did not change in the last check.  
More generally, General Arc Consistency (GAC) applies the same modus operandi as AC-3, but operating on constraint relations that are no longer binary, involving only two variables, but with an arbitrary number of variables. The pseudocode in Fig [4.3](https://artint.info/2e/html/ArtInt2e.Ch4.S4.html#Ch4.F3)

## Backtrack
Backtracking is a technique for finding solutions to problems where constraints must be satisfied. Backtracking has exponential complexity, so it is inefficient in dealing with problems that are not NP-complete. Enumerating all possible solutions, it discards those that do not satisfy the constraints, exploring a virtual tree structure to keep track of the choices made and the branches visited so that it can go back to the nearest node that contained an unexplored path in case the search in the current branch is unsuccessful.  
As it has to search the whole solution tree, we use this algorithm only in the final phase of the solution where the variable domain is very small. To reduce the number of possibilities, once the branch has been chosen, i.e we choice a value, we re-execute the above algorithms to reduce even more domains of the other variables, and reduce the paths that the backtrack has to explore.