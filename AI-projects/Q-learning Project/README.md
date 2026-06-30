# Reinforcement Learning

A reinforcement learning project implementing model-free and model-based learning algorithms using Gymnasium environments. The project trains agents with Q-Learning, learns Markov Decision Process (MDP) models through exploration, and computes optimal policies using Value Iteration.

Developed for CMPSC 442: Artificial Intelligence at Penn State.

## Features

- Q-Learning agent for the Blackjack environment
- ε-greedy exploration with decaying exploration rate
- Model-based reinforcement learning for FrozenLake
- Transition and reward model estimation from experience
- Value Iteration for optimal value function computation
- Policy extraction and evaluation using learned MDPs

## Main Components

- Q-Learning implementation
- Blackjack policy training and evaluation
- Random policy data collection
- Transition and reward model estimation
- Value Iteration
- Policy extraction and evaluation

## File Structure

- `solution_q1.py` – Q-Learning implementation for Blackjack (my work)
- `solution_q2.py` – Model-based reinforcement learning and Value Iteration for FrozenLake (my work)

## How to Run

```bash
pip install gymnasium

python solution_q1.py
python solution_q2.py
```
