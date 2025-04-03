Authors:
    Shafayet Fahim (sfahim@u.rochester.edu)
    Rizouana Prome (rprome@u.rochester.edu)

This program performs inference on Bayesian networks using three standard methods:
1. Exact inference using recursive enumeration (xquery)
2. Approximate inference using rejection sampling (rquery)
3. Approximate inference via Gibbs sampling (gquery)

Program Structure:
- The program is driven by standard input, where commands are parsed and dispatched.
- Network files define variables, their domains, and conditional probability tables (CPTs).
- Upon loading a network, the program maintains global data structures to store variables, their domains, parents, and CPTs.
