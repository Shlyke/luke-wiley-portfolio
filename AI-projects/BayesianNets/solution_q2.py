import csv
import random

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


def read_dataset(csv_path):
    #read csv dataset into list of (x1, x2, y)
    data = []
    with open(csv_path, "r", newline="") as f:
        dataset = csv.DictReader(f)
        #get x1:glucose, x2:bloodpressure, and y diabetes (output)
        for r in dataset:
            x1 = int(r["glucose"])
            x2 = int(r["bloodpressure"])
            y = int(r["diabetes"])
            data.append((x1, x2, y))
    return data

def split_data(rows, ratio=0.7, seed=0):
    #split rows into train/test
    #use stratified sampling by y

    #get randomm
    rng = random.Random(seed)

    #y0: no diabetes
    #y1: diabetes
    y0 = []
    y1 = []
    #iterate and sort on y
    for (x1, x2, y) in rows:
        if y == 0:
            y0.append((x1, x2, y))
        else:
            y1.append((x1, x2, y))

    #randomize order
    rng.shuffle(y0)
    rng.shuffle(y1)

    #get training set based on ratio
    train0 = int(len(y0) * ratio)
    train1 = int(len(y1) * ratio)

    #split the train and test data from each set
    train = y0[:train0] + y1[:train1]
    test = y0[train0:] + y1[train1:]

    #randomize again
    rng.shuffle(train)
    rng.shuffle(test)

    return train, test


def learn_cpts(train):
    #learn CPTs 
    #compute prior probabilities of y
    #compute  conditional probabilities of x1 given y
    #compute conditionl probabiliities of x2 given y

    #init count structs, get num of 1's and 0's for y 
    y_vals = {0: 0, 1: 0}

    #count X1 given Y, and X2 given Y
    x1_vals = {0: {}, 1: {}}
    x2_vals = {0: {}, 1: {}}

    #iterate over training data, update count structs
    for (x1, x2, y) in train:
        y_vals[y] += 1

        if x1 not in x1_vals[y]:
            x1_vals[y][x1] = 0
        x1_vals[y][x1] += 1

        if x2 not in x2_vals[y]:
            x2_vals[y][x2] = 0
        x2_vals[y][x2] += 1

    #compute probability of y
    total = y_vals[0] + y_vals[1]
    pY = {}
    #edge case no values
    if total == 0:
        pY[0] = 0.0
        pY[1] = 0.0
    else:
        pY[0] = y_vals[0] / total
        pY[1] = y_vals[1] / total

    #compute probability of x1 & x2 based on y
    #init cpt structs
    pX1 = {0: {}, 1: {}}
    pX2 = {0: {}, 1: {}}

    for y in [0, 1]:
        #num vals in y
        num = y_vals[y]
        #check if num = 0
        if num == 0:
            continue

        #fill cpt for x1
        for x1 in x1_vals[y]:
            pX1[y][x1] = x1_vals[y][x1] / num
        #fill cpt for x2
        for x2 in x2_vals[y]:
            pX2[y][x2] = x2_vals[y][x2] / num

    return pY, pX1, pX2


def Y_distribution(x1, x2, pY, pX1, pX2):
    #compute probability of y based on x1 & x2

    #init scores struct
    scores = {0: 0.0, 1: 0.0}
    #scores based on how compatible x1 and x2 aae with it

    #iterate over values of y, score how compatible with x1 and x2
    for y in [0, 1]:
        #get score y
        score = pY.get(y, 0.0)

        #mult score by px1 given y
        if x1 in pX1[y]:
            score *= pX1[y][x1]
        else:
            score *= 0.0

        #mult score by px2 given y
        if x2 in pX2[y]:
            score *= pX2[y][x2]
        else:
            score *= 0.0

        #add score to scores
        scores[y] = score

    #check if both are 0, return to prior
    if scores[0] == 0.0 and scores[1] == 0.0:
        scores = {0: pY.get(0, 0.0), 1: pY.get(1, 0.0)}

    return normalize(scores)


def prob_table(rows, pY, pX1, pX2):
    #build table to save prob values
    lookup = {}
    #iterate over each row, using x1, x2 key, find dist
    for (x1, x2, y_true) in rows:
        key = (x1, x2)
        if key not in lookup:
            lookup[key] = Y_distribution(x1, x2, pY, pX1, pX2)
    return lookup


def get_class(dist):
    #get class: 1 if P(Y=1) > P(Y=0) else 0
    if dist[1] > dist[0]:
        return 1
    return 0


def accuracy(rows, lookup):
    #compute prediction accuracy on test data using lookup table
    correct = 0
    total = 0
    #iterate over rows, check accuracy
    for (x1, x2, y_true) in rows:
        dist = lookup[(x1, x2)]
        #predicted y
        y_pred = get_class(dist)
        if y_pred == y_true:
            correct += 1
        total += 1
    if total == 0:
        return 0.0
    return correct / total


def print_prior(pY):
    #print P(Y)
    print("2.1.1")
    print(f"  Y=0: {pY[0]:.8f}")
    print(f"  Y=1: {pY[1]:.8f}")


def print_conditional(table, label, x_name):
    #print conditional table P(X|Y) for both y values
    print(f"{label} P({x_name} | Y)")
    for y in [0, 1]:
        print(f"  Y={y}:")
        #sort by numeric x value
        xs = list(table[y].keys())
        xs.sort()
        for x in xs:
            print(f"    {x_name}={x}: {table[y][x]:.8f}")

def print_predictions(test_rows, lookup):
    for (x1, x2, y_true) in test_rows:
        dist = lookup[(x1, x2)]
        y_pred = get_class(dist)
        print(f"  (X1={x1}, X2={x2}) -> Y_pred={y_pred}")


def print_lookup(lookup):
    #print lookup table for P(Y | X1, X2)
    print("2.2.2")
    keys = list(lookup.keys())
    keys.sort()
    for (x1, x2) in keys:
        dist = lookup[(x1, x2)]
        print(f"  (X1={x1}, X2={x2}) -> Y=0: {dist[0]:.8f}, Y=1: {dist[1]:.8f}")


if __name__ == "__main__":
    #load dataset
    csv_path = "Naive-Bayes-Classification-Data.csv"
    rows = read_dataset(csv_path)

    #2.0 split data (stratified 70/30)
    train, test = split_data(rows, ratio=0.7, seed=0)

    #2.1 learn CPTs from training data
    pY, pX1, pX2 = learn_cpts(train)

    #print 2.1 answers
    print_prior(pY)
    print_conditional(pX1, "2.1.2", "X1")
    print_conditional(pX2, "2.1.3", "X2")

    #2.2 inference by enumeration + lookup
    print("2.2.1")
    lookup = prob_table(test, pY, pX1, pX2)
    print_lookup(lookup)

    #2.3 predictions + accuracy
    print("2.3.1")
    print_predictions(test, lookup)
    print("2.3.2")
    acc = accuracy(test, lookup)
    print(f"  Accuracy: {acc:.8f}")
