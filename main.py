#!/usr/bin/env python3
import sys, itertools, random

# Global BN storage
variables_list = []
var_domains = {}
parents = {}
cpt = {}

def parse_network_file(filename):
    variables_list.clear()
    var_domains.clear()
    parents.clear()
    cpt.clear()

    lines = []
    with open(filename, 'r') as f:
        for line in f:
            # Remove comments
            idx = line.find('#')
            if idx != -1:
                line = line[:idx]
            line = line.strip()
            if line:
                lines.append(line)

    i = 0
    num_vars = int(lines[i]); i+=1
    for _ in range(num_vars):
        parts = lines[i].split()
        i+=1
        var = parts[0]
        dom = parts[1:]
        variables_list.append(var)
        var_domains[var] = dom
        parents[var] = []

    num_cpts = int(lines[i]); i+=1
    for _ in range(num_cpts):
        cpt_line = lines[i].split()
        i+=1
        child = cpt_line[0]
        if len(cpt_line) == 1:
            parents[child] = []
        else:
            parents[child] = cpt_line[1:]
        cpt[child] = {}
        if not parents[child]:
            dist_line = lines[i].split()
            i+=1
            cpt[child][()] = list(map(float, dist_line))
        else:
            parent_combos = list(itertools.product(*[var_domains[p] for p in parents[child]]))
            for combo in parent_combos:
                dist_line = lines[i].split()
                i+=1
                cpt[child][combo] = list(map(float, dist_line))

def prob_given_parents(variable, value, assignment):
    par = parents[variable]
    if not par:
        dist = cpt[variable][()]
    else:
        pvals = tuple(assignment[p] for p in par)
        dist = cpt[variable][pvals]
    idx = var_domains[variable].index(value)
    return dist[idx]

def draw_from(domain, dist):
    x = random.random()
    s = 0
    for val, pr in zip(domain, dist):
        s += pr
        if x <= s:
            return val
    return domain[-1]

def enumerate_all(vars_list, evidence):
    if not vars_list:
        return 1.0
    cur = vars_list[0]
    rest = vars_list[1:]
    if cur in evidence:
        p = prob_given_parents(cur, evidence[cur], evidence)
        return p * enumerate_all(rest, evidence)
    else:
        total = 0
        for val in var_domains[cur]:
            evidence[cur] = val
            p = prob_given_parents(cur, val, evidence)
            total += p * enumerate_all(rest, evidence)
        del evidence[cur]
        return total

def xquery(query_var, evidence):
    dist = []
    dom = var_domains[query_var]
    all_vars = variables_list[:]
    for val in dom:
        evidence[query_var] = val
        p = enumerate_all(all_vars, evidence)
        dist.append(p)
    del evidence[query_var]
    s = sum(dist)
    if s == 0:
        return [0.0]*len(dom)
    return [p/s for p in dist]

def prior_sample():
    sample = {}
    for var in variables_list:
        if not parents[var]:
            d = cpt[var][()]
        else:
            parent_vals = tuple(sample[p] for p in parents[var])
            d = cpt[var][parent_vals]
        sample[var] = draw_from(var_domains[var], d)
    return sample

def rquery(query_var, evidence, n=10000):
    counts = {val:0 for val in var_domains[query_var]}
    for _ in range(n):
        s = prior_sample()
        if all(s.get(evk)==evv for evk,evv in evidence.items()):
            counts[s[query_var]] += 1
    total = sum(counts.values())
    if total==0:
        return [0.0]*len(counts)
    return [counts[val]/total for val in var_domains[query_var]]

def gquery(query_var, evidence, n=10000, burn_in=1000):
    evars = set(evidence.keys())
    non_evars = [v for v in variables_list if v not in evars]
    assignment = {}
    for var in variables_list:
        if var in evidence:
            assignment[var] = evidence[var]
        else:
            assignment[var] = random.choice(var_domains[var])
    counts = {val:0 for val in var_domains[query_var]}
    for i in range(n+burn_in):
        for z in non_evars:
            domain_z = var_domains[z]
            pvals = []
            for cand_val in domain_z:
                assignment[z] = cand_val
                pz = prob_given_parents(z, cand_val, assignment)
                child_factor = 1.0
                for w in variables_list:
                    if z in parents[w]:
                        child_val = assignment[w]
                        child_factor *= prob_given_parents(w, child_val, assignment)
                pvals.append(pz*child_factor)
            s = sum(pvals)
            if s==0:
                pvals = [1.0/len(domain_z)]*len(domain_z)
            else:
                pvals = [pp/s for pp in pvals]
            chosen = draw_from(domain_z, pvals)
            assignment[z] = chosen
        if i>=burn_in:
            counts[assignment[query_var]]+=1
    tot = sum(counts.values())
    if tot==0:
        return [0.0]*len(counts)
    return [counts[val]/tot for val in var_domains[query_var]]

def main():
    random.seed(0)
    bn_loaded=False

    for line in sys.stdin:
        line=line.strip()
        if not line:
            continue
        if line.lower() in ["quit","exit"]:
            break

        tokens=line.split()
        cmd = tokens[0].lower()

        if cmd=="load":
            if len(tokens)>1:
                fname=tokens[1]
                try:
                    parse_network_file(fname)
                    bn_loaded=True
                except:
                    pass

        elif cmd in ["xquery","rquery","gquery"]:
            if not bn_loaded:
                continue
            parts=line.split("|")
            left=parts[0].strip()
            right=parts[1].strip() if len(parts)>1 else ""
            ltoks=left.split()
            if len(ltoks)<2:
                continue
            qvar=ltoks[1]
            evidence={}
            if right:
                evtokens=right.split()
                for ev in evtokens:
                    if "=" in ev:
                        k,v=ev.split("=")
                        evidence[k]=v
            if cmd=="xquery":
                dist=xquery(qvar,evidence)
            elif cmd=="rquery":
                dist=rquery(qvar,evidence,10000)
            else:
                dist=gquery(qvar,evidence,10000,1000)

            print(" ".join(f"{p:.4f}" for p in dist))

if __name__=="__main__":
    main()
