Authors:
Shafayet Fahim (sfahim@u.rochester.edu)
Rizouana Prome (rprome@u.rochester.edu)

Purpose:
In this program, we are using three different inference methods to perform inference on Bayesian networks. These methods are assigned to inputs xquery, rquery, and gquery, which correspond to exact inference via recursive enumeration, approximate inference via rejection sampling, and approximate inference via Gibbs sampling, respectively. The purpose of this program is to show the differences in effectiveness between these methods, especially concerning sample count differences between rejection and Gibbs sampling.

Program Structure:
The program reads in standard input, which tells our program which network.bn file, query and condition to use. Next, network files define values for global variables representing program variables, domains, parents, and conditional probability tables. Then the program evaluates the conditional probability based on the given information for the specific variable the program is looking into, which is subsequently printed as two values representing the probability of false and true; the program runs continuously.
