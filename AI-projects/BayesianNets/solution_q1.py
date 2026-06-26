def normalize(data):
    #normalize data set
    #need contitional probablilites to continue
    total = 0.0
    for k in data:
        total += data[k]
    if total == 0.0:
        return data
    normalized = {}
    for k in data:
        normalized[k] = data[k] / total
    return normalized


def restrict(factor, var, val):
    #reduce vars for factor
    #restrict factor to var=value

    #skip factor if not var
    if var not in factor["vars"]:
        return factor

    #get var index from each factor
    i = factor["vars"].index(var)
    new_vars = []
    for v in factor["vars"]:
        if v != var:
            new_vars.append(v)

    #create new table without specified restriced var 
    new_table = {}
    #get correct var from factor
    for k in factor["table"]:
        if k[i] == val:
            new_k = []
            #remove restricted var
            for x in range(len(k)):
                if x != i:
                    new_k.append(k[x])
            new_table[tuple(new_k)] = factor["table"][k]

    return {"vars": new_vars, "table": new_table}


def join(f1, f2):
    #multiply two factors(join)
    vars1 = f1["vars"]
    vars2 = f2["vars"]

    #set union of vars 
    new_vars = []
    for v in vars1:
        new_vars.append(v)
    for v in vars2:
        #no duplicate
        if v not in new_vars:
            new_vars.append(v)

    #get var index in factor
    i1 = {}
    i2 = {}
    for v in new_vars:
        if v in vars1:
            #give index
            i1[v] = vars1.index(v)  
        else:
            #v not in factor
            i1[v] = -1
        if v in vars2:
            #give index
            i2[v] = vars2.index(v) 
        else:
            #v not in factor
            i2[v] = -1

    #create new table for mult factors
    new_table = {}

    #iterate over all valid assignments 
    for a1 in f1["table"]:
        for a2 in f2["table"]:
            valid = True
            #check shared vars
            for v in vars1:
                if v in vars2:
                    #if shared var, get val
                    if i1[v] != -1 and i2[v] != -1:
                        if a1[i1[v]] != a2[i2[v]]:
                            valid = False
                            break
            #if not valid, continue        
            if not valid:
                continue

            #init joined list
            joined = []
            #iterate over unioned vars
            for v in new_vars:
                #check var factor
                if i1[v] != -1:
                    joined.append(a1[i1[v]])
                else:
                    joined.append(a2[i2[v]])
            joined_t = tuple(joined)

            #perform join/multiplication
            new_table[joined_t] = f1["table"][a1] * f2["table"][a2]

    return {"vars": new_vars, "table": new_table}


def eliminate(factor, var):
    #eliminate var from factor
    #sum over possible vals

    #check factor for var
    if var not in factor["vars"]:
        return factor

    #get index of var
    i = factor["vars"].index(var)
    #init new vars list
    new_vars = []
    #add all vars that arent var in lilst
    for v in factor["vars"]:
        if v != var:
            new_vars.append(v)

    #init new table to eliminate rows by combining
    new_table = {}
    for a in factor["table"]:
        #ini key w/o var
        new_a = []
        #add vars to key if not var
        for k in range(len(a)):
            if k != i:
                new_a.append(a[k])
        new_key = tuple(new_a)

        #sum over all prob into new key
        #init new key
        if new_key not in new_table:
            new_table[new_key] = 0.0
        new_table[new_key] += factor["table"][a]

    return {"vars": new_vars, "table": new_table}


def extraction(factor, var):
    #Create dict where only var exists
    #remove all vars that arent var
    if factor["vars"] != [var]:
        f = factor
        #check extra vars, if exist, eliminate
        for v in list(f["vars"]):
            if v != var:
                f = eliminate(f, v)
        factor = f

    #init distributon dict
    extracted = {}
    #add key to dict, should only have var
    for a in factor["table"]:
        extracted[a[0]] = factor["table"][a]
    return extracted

def bayesian_table():
    #create bayesian table dictionaries
    #P(B)
    B = {
        "vars": ["B"],
        "table": {
            ("+b",): 0.001,
            ("-b",): 0.999
        }
    }

    #P(E)
    E = {
        "vars": ["E"],
        "table": {
            ("+e",): 0.002,
            ("-e",): 0.998
        }
    }

    #P(A | B, E)
    A = {
        "vars": ["B", "E", "A"],
        "table": {
            ("+b", "+e", "+a"): 0.95,
            ("+b", "+e", "-a"): 0.05,
            ("+b", "-e", "+a"): 0.94,
            ("+b", "-e", "-a"): 0.06,
            ("-b", "+e", "+a"): 0.29,
            ("-b", "+e", "-a"): 0.71,
            ("-b", "-e", "+a"): 0.001,
            ("-b", "-e", "-a"): 0.999
        }
    }

    #P(J | A)
    J = {
        "vars": ["A", "J"],
        "table": {
            ("+a", "+j"): 0.90,
            ("+a", "-j"): 0.10,
            ("-a", "+j"): 0.05,
            ("-a", "-j"): 0.95
        }
    }

    #P(M | A)
    M = {
        "vars": ["A", "M"],
        "table": {
            ("+a", "+m"): 0.70,
            ("+a", "-m"): 0.30,
            ("-a", "+m"): 0.01,
            ("-a", "-m"): 0.99
        }
    }

    #return list of factor dicts
    return [B, E, A, J, M]


def variable_elimination(var, evidence, factors, order):
    #variable elimination process
    #restrict factors based on evidence
    #loop(join factors, eliminate factors)
    #join, eliminate to sum out and normalize result

    #restrict all factors using restrict function
    new_factors = []
    #loop over factors, restrict, add to new factors list
    for f in factors:
        #copy to preserve
        f2 = f
        for ev in evidence:
            f2 = restrict(f2, ev, evidence[ev])
        new_factors.append(f2)

    #eliminate variables using elimnate  and join function
    for z in order:
        #collect factors with z
        bucket = []
        rest = []
        #loop over factors, add ones with z to bucket, rest to rest
        for f in new_factors:
            if z in f["vars"]:
                bucket.append(f)
            else:
                rest.append(f)

        #edge case, nothing to eliminate
        if len(bucket) == 0:
            new_factors = rest
            continue

        #join factors in bucket 
        joined = bucket[0]
        for i in range(1, len(bucket)):
            joined = join(joined, bucket[i])

        #eliminate, so factor no longer has z
        reduced = eliminate(joined, z)

        #append new factor with rest, loop
        rest.append(reduced)
        new_factors = rest

    #multiply remaining factors
    result = new_factors[0]
    for i in range(1, len(new_factors)):
        result = join(result, new_factors[i])

    #if extra vars, sum out 
    for v in list(result["vars"]):
        if v != var:
            result = eliminate(result, v)

    return result


if __name__ == "__main__":
    #get bayesian network
    factors = bayesian_table()

    #var: P(B | J=+j)
    var = "B"
    evidence = {"J": "+j"}

    #eliminate all vars except var and evidence
    elimination_order = ["E", "A", "M"]

    #run VE
    f = variable_elimination(var, evidence, factors, elimination_order)

    #extract + normalize
    dist = extraction(f, "B")
    dist = normalize(dist)

    #print result as a probability distribution table
    print("P(B | J=+j)")
    #consistent ordering
    for k in ["+b", "-b"]:
        print(f"  {k}: {dist[k]:.8f}")
