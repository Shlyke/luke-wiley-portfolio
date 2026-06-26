TOTAL_M = None #total missionaries global
TOTAL_C = None #total cannibals Global

class Node:
    def __init__(self, state, parent=None, depth=0):
        self.state = state #(Ml, Cl, Mr, Cr, B)
        self.parent = parent
        self.depth = depth

def parse_start_state(path = "input.txt"):
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
    parts = [p.strip() for p in line.split(",")]
    #remove commas for parsing
    if len(parts) != 5:
        #must be in Ml, Cl, Mr, Cr, B format
        raise ValueError("invalid input.txt")
    Ml, Cl, Mr, Cr = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    B = parts[4].upper()
    if B not in ("L", "R"):
        raise ValueError("invalid input.txt")
    return (Ml, Cl, Mr, Cr, B)

def goal(s):
    Ml, Cl, Mr, Cr, _ = s
    #want all missionaries and cannibals on the right bank
    return Ml == 0 and Cl == 0 and Mr == TOTAL_M and Cr == TOTAL_C

def valid(s):
    Ml, Cl, Mr, Cr, B = s
    if not (0 <= Ml <= TOTAL_M and 0 <= Mr <= TOTAL_M and Ml + Mr == TOTAL_M):
        #check total missionaries
        return False
    if not (0 <= Cl <= TOTAL_C and 0 <= Cr <= TOTAL_C and Cl + Cr == TOTAL_C):
        #check total cannibals
        return False
    if B not in ("L", "R"):
        #check boat position
        return False
    if Ml > 0 and Cl > Ml: return False
    if Mr > 0 and Cr > Mr: return False
    return True

def successors(s):
    Ml, Cl, Mr, Cr, B = s
    for m, c in [(2,0), (0,2), (1,0), (0,1), (1,1)]:
        #iterate over all possible movements, check valid, yield
        if B == "L":
            if Ml >= m and Cl >= c and 1 <= m+c <= 2:
                #check valid move, must be people to move, at least 1 up to 2
                nxt = (Ml - m, Cl - c, Mr + m, Cr + c, "R")
                #next state after move occurs
                if valid(nxt):
                    yield nxt
        else:
            if Mr >= m and Cr >= c and 1 <= m + c <= 2:
                #check valid move, must be people to move, at least 1 up to 2
                nxt = (Ml + m, Cl + c, Mr - m, Cr - c, "L")
                #next state after move occurs
                if valid(nxt):
                    yield nxt

def get_path(goal_node):
    path = []
    current = goal_node
    while current is not None:
        #append each node's parent from urrent node to get path
        path.append(current.state)
        current = current.parent
    #path is in reverse order
    path.reverse()
    return path 

def move_info(prev, nxt):
    """Return (moved_m, moved_c, direction) from prev -> nxt."""
    pMl, pCl, pMr, pCr, pB = prev
    nMl, nCl, nMr, nCr, nB = nxt
    if pB == "L" and nB == "R":
        direction = "L->R"
        moved_m = pMl - nMl
        moved_c = pCl - nCl
    else:  # pB == "R" and nB == "L"
        direction = "R->L"
        moved_m = pMr - nMr
        moved_c = pCr - nCr
    return moved_m, moved_c, direction

def edge_cost(prev, nxt, model="A"):
    m, c, direction = move_info(prev, nxt)
    if model == "A":
        # 2 per missionary + 1 per cannibal on the boat
        return 2*m + 1*c
    else:  # model == "B"
        # L->R costs 2, R->L costs 1
        return 2 if direction == "L->R" else 1
    
def h1(s):
    #heuristic 1
    Ml, Cl, Mr, Cr, B = s
    return 2*Ml + 1*Cl

def h2(s):
    #heuristic 2
    Ml, Cl, Mr, Cr, B = s
    X = 2*Ml + 1*Cl
    return (X + 2) // 3

def h3(s):
    #heuristic 2
    #takes cost of everyone on left bank, adds the cost of all minimum return trips
    Ml, Cl, Mr, Cr, B = s
    X = 2*Ml + Cl
    if X == 0:
        return 0
    trips = (X + 2) // 3
    returns = trips - (1 if B == "L" else 0)
    return X + returns

def astar(start, heuristic="h1"):
    #check if valid state
    if not valid(start):
        raise ValueError("Invalid Start State")
    #select heuristic
    if heuristic == "h1":
        heuristic_func = h1 
    if heuristic == "h2":
        heuristic_func = h2
    else:
        heuristic_func = h3
    fringe = [(heuristic_func(start), 0, Node(start, None, 0))]
    #astar uses list with sorted weights [weight, node]
    visited_cost = {start: 0}
    #stops backtracking
    #keeps track of least cost
    expansions = 0

    while fringe:
        #iterate over list to find least cost
        index = 0
        #edge decision comes from smallest f = g + h
        f_min, g_min, min_node = fringe[0]
        for i in range(1, len(fringe)):
            f_i, g_i, node_i = fringe[i]
            if f_i < f_min:
                index=i
                f_min, g_min, min_node = f_i, g_i, node_i

        #get least cost node
        f, g, node = fringe.pop(index)
        s = node.state

        #check if current least cost path to node
        if g != visited_cost.get(s, float("inf")):
            continue

        expansions += 1
    
        if goal(s):
            path = get_path(node)
            return path, g, expansions
        
        for nxt in successors(s):
            #add all valid next states, next while iteration
            step = edge_cost(s, nxt, model="A")
            new_g = g + step
            if new_g < visited_cost.get(nxt, float("inf")):
                visited_cost[nxt] = new_g
                new_f = new_g + heuristic_func(nxt)
                fringe.append((new_f, new_g, Node(nxt, node, node.depth + 1)))

    #failsafe
    return [], 0, expansions

def main():
    global TOTAL_M, TOTAL_C
    #parse to get start state
    start = parse_start_state()
    #initialize globals
    TOTAL_M = start[0] + start[2]
    TOTAL_C = start[1] + start[3]
    
    #run astar heuristic 1
    path_A, cost_A, exp_A = astar(start, heuristic="h1")
    print(f"The solution of Q3.1 (Heuristic 1) is:")
    if path_A:
        path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_A)
        print("Solution Path: " + path_str)
        print("Total cost = " + str(cost_A))
        print("Number of node expansions = " + str(exp_A))
    else:
        print("Solution Path: ")
        print("Total cost = 0")
        print("Number of node expansions = " + str(exp_A))
    print()

    #run astar heuristic 2
    path_B, cost_B, exp_B = astar(start, heuristic="h2")
    print(f"The solution of Q3.1 (Heuristic 2) is:")
    if path_B:
        path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_B)
        print("Solution Path: " + path_str)
        print("Total cost = " + str(cost_B))
        print("Number of node expansions = " + str(exp_B))
    else:
        print("Solution Path: ")
        print("Total cost = 0")
        print("Number of node expansions = " + str(exp_B))
    print()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        #initiate globals
        TOTAL_M, TOTAL_C = 3, 3
        start = (3,3,0,0,"L")
        #run astar heuristic 1
        path_A, cost_A, exp_A = astar(start, heuristic="h1")
        print(f"The solution of Q3.1 (Heuristic 1) is:")
        if path_A:
            path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_A)
            print("Solution Path: " + path_str)
            print("Total cost = " + str(cost_A))
            print("Number of node expansions = " + str(exp_A))
        else:
            print("Solution Path: ")
            print("Total cost = 0")
            print("Number of node expansions = " + str(exp_A))
        print()

        #run astar heuristic 2
        path_B, cost_B, exp_B = astar(start, heuristic="h2")
        print(f"The solution of Q3.1 (Heuristic 2) is:")
        if path_B:
            path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_B)
            print("Solution Path: " + path_str)
            print("Total cost = " + str(cost_B))
            print("Number of node expansions = " + str(exp_B))
        else:
            print("Solution Path: ")
            print("Total cost = 0")
            print("Number of node expansions = " + str(exp_B))
        print()

        #run astar heuristic 3
        path_C, cost_C, exp_C = astar(start, heuristic="h3")
        print(f"The solution of Q3.2 (Heuristic 3) is:")
        if path_C:
            path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_C)
            print("Solution Path: " + path_str)
            print("Total cost = " + str(cost_C))
            print("Number of node expansions = " + str(exp_C))
        else:
            print("Solution Path: ")
            print("Total cost = 0")
            print("Number of node expansions = " + str(exp_C))
        print()

    else:
        main()