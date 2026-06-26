import gymnasium as gym

def init_list(x, y, z):
    #initialize 3d list, helper function
    return [[[0.0 for _ in range(z)] for _ in range(y)] for _ in range(x)]


def random_policy_learn(env, games=1000):
    #find transition model though random policy

    #get all states and actions from environment
    states = env.observation_space.n
    actions = env.action_space.n

    #init move count structure
    N = init_list(states, actions, states)

    #sum of rewards
    rewards = init_list(states,actions, states)

    #loop to play games and find model
    for _ in range(games):
        #start new game
        state, info = env.reset()
        #game status
        terminated = False
        truncated = False

        #ensure game is continuing
        while not (terminated or truncated):
            #choose a random action
            action = env.action_space.sample()
            #perform action
            next_state, reward, terminated, truncated, info = env.step(action)

            #update specific action count and rewards
            N[state][action][next_state] += 1
            rewards[state][action][next_state] += reward

            #iterate
            state = next_state
    
    #build T_hat, transition probabilities
    #build R_hat, expected rewards
    T_hat = init_list(states, actions, states)
    R_hat = init_list(states, actions, states)

    #iterate over actions to build model
    for s in range(states):
        for a in range(actions):
            #get number of times action a was taken at state s
            total = sum(N[s][a])

            #apply values to T_hat and R_hat
            if total > 0:
                for s2 in range(states):
                    T_hat[s][a][s2] = N[s][a][s2] / total

                for s2 in range(states):
                    if N[s][a][s2] > 0:
                        R_hat[s][a][s2] = rewards[s][a][s2] / N[s][a][s2]

    return T_hat, R_hat

def value_iteration(T_hat, R_hat, gamma = 0.99, theta = 0.000001):
    #get optimal value function

    #get states and actions from transition model
    states = len(T_hat)
    actions = len(T_hat[0])

    #init value funtion
    v = [0.0 for _ in range(states)]

    #loop v until we conveerge
    while True:
        #init delta to track largest change
        delta = 0.0
        #create copy to preserve
        v1 = v.copy()

        #Update state values
        for s in range(states):
            action_values = []

            #for each action, get expected value
            for a in range(actions):
                val = 0.0
                for s2 in range(states):
                    val += T_hat[s][a][s2] * (R_hat[s][a][s2] + gamma * v[s2])
                action_values.append(val)
            
            #get max action
            v1[s] = max(action_values)

        #compute difference between old and new values
        delta = max(delta, max(abs(v1[s] - v[s]) for s in range(states)))
        #iterate
        v = v1

        #if converge, break
        if delta < theta: 
            break
    return v

def get_policy(T_hat, R_hat, v_star, gamma=0.99):
    #get the policy from value function

    #get states and actions from model
    states = len(T_hat)
    actions = len(T_hat[0])

    #init the policy
    policy = [0 for _ in range(states)]

    #iterate, get action vals
    for s in range(states):
        action_values = []

        #compute expected value of each action under the value function
        for a in range(actions):
            val = 0.0
            for s2 in range(states):
               val += T_hat[s][a][s2] * (R_hat[s][a][s2] + gamma * v_star[s2]) 

            action_values.append(val)

        #update policy with best action at state
        policy[s] = action_values.index(max(action_values))

    return policy


def evaluate_policy(env, policy, games=20):
    #test policy
    total_reward = 0

    #loop games
    for i in range(1, games + 1):
        #start new game
        state, info = env.reset()
        #game status
        terminated = False
        truncated = False
        total = 0

        #perform policy
        while not (terminated or truncated):
            action = policy[state]
            state, reward, terminated, truncated, info = env.step(action)
            total += reward

        #track rewards
        total_reward += total
        print(f"Game {i}: reward = {total}")

    avg_reward = total_reward / games
    print(f"\nAverage reward: {avg_reward:.3f}")


if __name__ == "__main__":
    #init frozen lake game environment
    env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)

    T_hat, R_hat = random_policy_learn(env, games=1000)

    V_star = value_iteration(T_hat, R_hat)

    policy = get_policy(T_hat, R_hat, V_star)

    evaluate_policy(env, policy, games=20)