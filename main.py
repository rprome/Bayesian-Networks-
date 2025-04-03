"""
Authors:
    Shafayet Fahim (sfahim@u.rochester.edu)
    Rizouana Prome (rprome@u.rochester.edu)
"""
# Imports
import sys
import random

# Global variables
variable_names = []
variable_domains = {}
variable_parents = {}
cpts = {}

# Functions
def cartesian_product(lists):
    if not lists: return [[]]
    cp_result = []
    combinations = cartesian_product(lists[1:])
    for item in lists[0]:
        for combination in combinations:
            cp_result.append([item] + combination)
    return cp_result
def parse_network_file(filename):
    variable_names.clear()
    variable_domains.clear()
    variable_parents.clear()
    cpts.clear()

    with open(filename, 'r') as file: cleaned_lines = [line.split('#')[0].strip() for line in file if line.strip()]

    line_index = 1
    number_of_variables = int(cleaned_lines[0])

    for variable in range(number_of_variables):
        split_line = cleaned_lines[line_index].split()
        variable = split_line[0]
        domain = split_line[1:]
        variable_names.append(variable)
        variable_domains[variable] = domain
        variable_parents[variable] = []
        line_index += 1

    number_of_cpts = int(cleaned_lines[line_index])
    line_index += 1

    for cpt in range(number_of_cpts):
        split_line = cleaned_lines[line_index].split()
        child_variable = split_line[0]
        parent_variables = split_line[1:]
        variable_parents[child_variable] = parent_variables
        cpts[child_variable] = {}
        line_index += 1
        if not parent_variables:
            probabilities = [float(value) for value in cleaned_lines[line_index].split()]
            cpts[child_variable][()] = probabilities
            line_index += 1
        else:
            parent_domains = [variable_domains[parent] for parent in parent_variables]
            parent_combinations = [tuple(combination) for combination in cartesian_product(parent_domains)]
            for combination in parent_combinations:
                probabilities = [float(value) for value in cleaned_lines[line_index].split()]
                cpts[child_variable][combination] = probabilities
                line_index += 1
def probability_given_parents(variable, value, assignment):
    if not variable_parents[variable]: distribution = cpts[variable][()]
    else:
        parent_values = tuple(assignment[parent] for parent in variable_parents[variable])
        distribution = cpts[variable][parent_values]
    return distribution[variable_domains[variable].index(value)]
def draw_value_from_distribution(domain, distribution):
    random_value = random.random()
    total = 0
    for i in range(len(domain)):
        value = domain[i]
        probability = distribution[i]
        total += probability
        if random_value <= total: return value
    return domain[-1]
def recursive_enumeration(remaining_variables, assignment):
    if not remaining_variables: return 1.0

    current = remaining_variables[0]
    remaining = remaining_variables[1:]

    if current in assignment:
        prob = probability_given_parents(current, assignment[current], assignment)
        return prob * recursive_enumeration(remaining, assignment)

    total_probability = 0
    for value in variable_domains[current]:
        new_evidence = assignment.copy()
        new_evidence[current] = value
        prob = probability_given_parents(current, value, new_evidence)
        total_probability += prob * recursive_enumeration(remaining, new_evidence)
    return total_probability
def exact_query(target_variable, current_assignment):
    result_distribution = []
    query_domain = variable_domains[target_variable]

    for value in query_domain:
        extended_assignment = current_assignment.copy()
        extended_assignment[target_variable] = value
        probability = recursive_enumeration(variable_names[:], extended_assignment)
        result_distribution.append(probability)

    total = sum(result_distribution)
    normalized_distribution = []

    if total > 0:
        for probability in result_distribution:
            normalized_distribution.append(probability / total)
    else: normalized_distribution = [0.0] * len(query_domain)

    return normalized_distribution
def generate_prior_sample():
    sample = {}
    for variable in variable_names:
        if not variable_parents[variable]: distribution = cpts[variable][()]
        else:
            parent_values = tuple(sample[parent] for parent in variable_parents[variable])
            distribution = cpts[variable][parent_values]
        sample[variable] = draw_value_from_distribution(variable_domains[variable], distribution)
    return sample
def rejection_sampling(target_variable, given_assignment, sample_count):
    value_counts = {value: 0 for value in variable_domains[target_variable]}
    accepted_samples = 0
    for i in range(sample_count):
        sampled_assignment = generate_prior_sample()
        matched = True
        for variable in given_assignment:
            if sampled_assignment.get(variable) != given_assignment[variable]:
                matched = False
                break
        if matched:
            observed_value = sampled_assignment[target_variable]
            value_counts[observed_value] += 1
            accepted_samples += 1
    normalized_distribution = []
    if accepted_samples > 0:
        for value in variable_domains[target_variable]:
            probability = value_counts[value] / accepted_samples
            normalized_distribution.append(probability)
    else: normalized_distribution = [0.0] * len(variable_domains[target_variable])
    return normalized_distribution
def gibbs_sampling(target_variable, assignment, sample_count, burn_in):
    fixed_variables = assignment.keys()
    sampled = [variable_name for variable_name in variable_names if variable_name not in fixed_variables]
    current = assignment.copy()
    for sample in sampled: current[sample] = random.choice(variable_domains[sample])
    counts = {value: 0 for value in variable_domains[target_variable]}
    for step in range(sample_count + burn_in):
        for sample in sampled:
            probabilities = []
            for variable_domain in variable_domains[sample]:
                current[sample] = variable_domain
                probability = probability_given_parents(sample, variable_domain, current)
                for child in variable_names:
                    if sample in variable_parents[child]: probability *= probability_given_parents(child, current[child], current)
                probabilities.append(probability)
            total = 0
            for probability in probabilities: total += probability
            if total > 0: normalized = [p / total for p in probabilities]
            else: normalized = [1 / len(probabilities)] * len(probabilities)
            current[sample] = draw_value_from_distribution(variable_domains[sample], normalized)
        if step >= burn_in:counts[current[target_variable]] += 1
    total = sum(counts.values())
    if total == 0: return [0.0] * len(counts)
    return [counts[val] / total for val in variable_domains[target_variable]]

# Main
random.seed(0)
network_loaded = False
for input_line in sys.stdin:
    input_line = input_line.strip()
    if not input_line or input_line.lower() in ["quit", "exit"]: break
    split_input = input_line.split()
    command = split_input[0].lower()
    if command == "load" and len(split_input) > 1:
        parse_network_file(split_input[1])
        network_loaded = True
    elif command in ["xquery", "rquery", "gquery"] and network_loaded:
        parts = input_line.split("|")
        query_variable = parts[0].split()[1]
        variable_conditions = dict(part.split("=") for part in parts[1].split()) if len(parts) > 1 else {}
        if command == "xquery": result = exact_query(query_variable, variable_conditions)
        elif command == "rquery": result = rejection_sampling(query_variable, variable_conditions, 2400)
        else: result = gibbs_sampling(query_variable, variable_conditions, 1200, 120)
        print(" ".join(f"{p:.4f}" for p in result))
