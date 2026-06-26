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

def dfs(start):
    #check if valid state
    if not valid(start):
        raise ValueError("Invalid Start State")
    stack = [Node(start, None, 0)]
    #dfs utilizes stack
    visited = set()
    #stops backtracking
    expansions = 0

    while stack:
        #remove from stack to operate on state
        node = stack.pop()
        s = node.state

        #if in visited, pop next state
        if s in visited:
            continue
        #if not in visited, add to visited, operate
        visited.add(s)
        expansions += 1
        if goal(s):
            path = get_path(node)
            cost = len(path) - 1
            return path, cost, expansions
        
        for nxt in successors(s):
            #add all valid next states, next while iteration
            if nxt not in visited:
                stack.append(Node(nxt, node, node.depth +1))

    #failsafe
    return [], 0, expansions

def bfs(start):
    #check if valid state
    if not valid(start):
        raise ValueError("Invalid Start State")
    queue = [Node(start, None, 0)]
    #bfs utilizes Queue
    visited = set()
    #stops backtracking
    expansions = 0

    while queue:
        #remove from left of queue to operate
        node = queue.pop(0)
        s = node.state
        
        #if in visted, pop next state
        if s in visited:
            continue
        #if not in visited, add to visited, operate
        visited.add(s)
        expansions += 1
        if goal(s):
            path = get_path(node)
            cost = len(path) - 1
            return path, cost, expansions
        
        for nxt in successors(s):
            #add all valid next states, next while iteration
            if nxt not in visited:
                queue.append(Node(nxt, node, node.depth +1))

    #failsafe
    return [], 0, expansions


def main():
    global TOTAL_M, TOTAL_C
    #parse to get start state
    start = parse_start_state()
    #initialize globals
    TOTAL_M = start[0] + start[2]
    TOTAL_C = start[1] + start[3]
    #run dfs
    path_dfs, cost_dfs, exp_dfs = dfs(start)
    print("The solution of Q1.1.a (DFS) is:")
    if path_dfs:
        path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_dfs)
        print("Solution Path: " + path_str)
        print("Total cost = " + str(cost_dfs))
        print("Number of node expansions = " + str(exp_dfs))
    else:
        print("Solution Path: ")
        print("Total cost = 0")
        print("Number of node expansions = " + str(exp_dfs))
    print()

    #run bfs
    path_bfs, cost_bfs, exp_bfs = bfs(start)
    print("The solution of Q1.1.b (BFS) is:")
    if path_bfs:
        path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_bfs)
        print("Solution Path: " + path_str)
        print("Total cost = " + str(cost_bfs))
        print("Number of node expansions = " + str(exp_bfs))
    else:
        print("Solution Path: ")
        print("Total cost = 0")
        print("Number of node expansions = " + str(exp_bfs))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        #initiate globals
        TOTAL_M, TOTAL_C = 3, 3
        start = (3,3,0,0,"L")
        #run dfs
        path_dfs, cost_dfs, exp_dfs = dfs(start)
        print("The solution of Q1.1.a (DFS) is:")
        if path_dfs:
            path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_dfs)
            print("Solution Path: " + path_str)
            print("Total cost = " + str(cost_dfs))
            print("Number of node expansions = " + str(exp_dfs))
        else:
            print("Solution Path: ")
            print("Total cost = 0")
            print("Number of node expansions = " + str(exp_dfs))
        print()

        #ru bfs
        path_bfs, cost_bfs, exp_bfs = bfs(start)
        print("The solution of Q1.1.b (BFS) is:")
        if path_bfs:
            path_str = " ".join(f"({Ml},{Cl},{Mr},{Cr},{B})" for (Ml,Cl,Mr,Cr,B) in path_bfs)
            print("Solution Path: " + path_str)
            print("Total cost = " + str(cost_bfs))
            print("Number of node expansions = " + str(exp_bfs))
        else:
            print("Solution Path: ")
            print("Total cost = 0")
            print("Number of node expansions = " + str(exp_bfs))
    else:
        main()