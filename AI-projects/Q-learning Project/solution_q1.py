import gymnasium as gym
import random
#random for action selection

def get_action(Q, state, actions, epsilon):
    #get the best action based on the state space Q, current state, # actions, and the probability to pick random epsilon
    
    #Check if state is in state space, initialize
    if state not in Q:
        Q[state] = [0.0 for _ in range(actions)]
    
    #decide if random action to explore
    if random.random() < epsilon:
        return random.randint(0, actions - 1)
    
    #If not, choose best action based on previous values
    else:
        values = Q[state]
        best = values.index(max(values))
        return best
    
def q_learning(games = 100000, alpha = 0.1, gamma = 1.0, start = 1.0, min = 0.1, decay = 0.99999):
    #perform q_learning over 100000 games
    #learing rate alpha, discount gamma, start random probability, min random probability, decay to decrease epsilon

    #init gymnasium blackjack environment
    env = gym.make("Blackjack-v1", natural=False, sab=False)
    
    #get actions: hit/stay
    actions = env.action_space.n

    #init state space
    Q = {}

    #init epsilon for learning loop
    epsilon = start

    #begin learning loop
    for i in range(games):
        #start new game
        state, info = env.reset()

        #game status
        terminated = False
        truncated = False

        #make sure game is still going
        while not (terminated or truncated):
            #add missing states
            if state not in Q:
                Q[state] = [0.0 for _ in range(actions)]

            #get best action based on random/ not random probability
            action = get_action(Q, state, actions, epsilon)

            #perform chosen action
            next_state, reward, terminated, truncated, info = env.step(action)
            
            #add missing state
            if next_state not in Q:
                Q[next_state] = [0.0 for _ in range(actions)]

            #update q-learning parameters
            best = max(Q[next_state])
            old = Q[state][action]
            target = reward + gamma * best
            Q[state][action] = old + alpha * (target - old)

            #iterate
            state = next_state

        #apply decay
        epsilon = max(min, epsilon* decay)

    return Q



def policy(Q, games=100):
    #apply the policy from q-learning
    #use state space form q-learning over 100 games

    #init gymnasium blackjack environment
    env = gym.make("Blackjack-v1", natural=False, sab=False)

    #get actions: hit/stay
    actions = env.action_space.n

    #init results
    wins = 0
    ties = 0
    losses = 0

    #loop over games
    for i in range(1, games + 1):
        #start new game
        state, info = env.reset()
        #game status
        terminated = False
        truncated = False

        #make sure game is continuing
        while not (terminated or truncated):

            #add missing states
            if state not in Q:
                Q[state] = [0.0 for _ in range(actions)]

            #apply policy, choose best action
            values = Q[state]
            action = values.index(max(values))

            #perform chosen action
            state, reward, terminated, truncated, info = env.step(action)

        #track results, print
        if reward > 0:
            wins += 1
            print(f"Game {i}: Win")
        elif reward == 0:
            ties += 1
            print(f"Game {i}: Win")
        else:
            losses += 1
            print(f"Game {i}: Loss")

    #print results
    total = wins + ties + losses
    print(f"Total Games: {total}")
    print(f"Win rate:  {wins / total:.3f}")
    print(f"Tie rate:  {ties / total:.3f}")
    print(f"Loss rate: {losses / total:.3f}")


if __name__ == "__main__":
    Q = q_learning()
    policy(Q, games=100)