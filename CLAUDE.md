# Poker RL — CLAUDE.md

## Project Overview

This project is a from-scratch implementation of a Texas Hold'em poker engine with two reinforcement learning agents: a Deep Q-Network (DQN) agent and a Proximal Policy Optimization (PPO) agent. The agents are trained via self-play and ultimately compete head-to-head. The project is intended as a portfolio piece demonstrating both game engine design and applied reinforcement learning.

---

## Goals

1. Build a fully functional **Limit Texas Hold'em** game engine from scratch in Python, with no reliance on external poker/card game libraries.
2. Wrap the game engine in a clean **RL environment interface** (`reset`, `step`, `render`) modeled after the OpenAI Gym standard.
3. Implement a **DQN agent** that learns via self-play using experience replay and an epsilon-greedy exploration strategy.
4. Implement a **PPO agent** that learns via self-play using an actor-critic architecture and policy gradient optimization.
5. Train both agents against a **random baseline agent** first to verify learning, then transition to self-play.
6. Run **head-to-head training** where DQN and PPO are each other's opponent, allowing their strategies to diverge and co-evolve.
7. Produce **evaluation metrics and plots** that tell a clear story: win rates over training, behavioral differences between agents, and head-to-head records.

---

## Project Structure

```
poker-rl/
│
├── poker/
│   ├── card.py             # Card and Deck classes
│   ├── hand_evaluator.py   # Determines and ranks winning 5-card hands from 7 cards
│   ├── player.py           # Player state: chips, hole cards, current bet, active status
│   ├── table.py            # Game loop: blinds, dealing, betting rounds, pot resolution
│   └── environment.py      # RL wrapper: reset(), step(), state vector, reward function
│
├── agents/
│   ├── base_agent.py       # Abstract base class all agents inherit from
│   ├── random_agent.py     # Acts randomly — used as baseline sanity check
│   ├── dqn_agent.py        # DQN agent with replay buffer and epsilon-greedy exploration
│   └── ppo_agent.py        # PPO agent with actor-critic network and clipped objective
│
├── training/
│   ├── train_dqn.py        # DQN training loop (self-play and vs random)
│   ├── train_ppo.py        # PPO training loop (self-play and vs random)
│   └── train_versus.py     # Head-to-head training: DQN vs PPO
│
├── evaluation/
│   └── evaluate.py         # Tournament runner, win rate logging, matplotlib plots
│
├── models/                 # Saved model weights (.pt files)
├── results/                # Output graphs and training logs
├── tests/                  # Unit tests for the game engine
├── CLAUDE.md               # This file
└── README.md               # Public-facing project documentation
```

---

## Game Rules — No-Limit Texas Hold'em

Standard **No-Limit Texas Hold'em** rules. Bet sizes are variable, so actions are discretized into a fixed set of common bet sizes to keep the action space manageable for RL.

- **Players:** 2 (heads-up)
- **Betting structure:** No-Limit — any bet from the minimum up to a player's full stack is legal
- **Betting rounds:** Pre-flop → Flop → Turn → River
- **Actions (discretized):** `fold`, `call/check`, `raise 25% pot`, `raise 50% pot`, `raise 100% pot`, `all-in` (6 discrete actions)
- **Blinds:** Small blind = 1 unit, Big blind = 2 units
- **Winning:** Best 5-card hand from 7 cards (2 hole + 5 community), or last player standing after folds

---

## RL Environment Design

### State Vector
The state passed to agents should encode:
- Hole cards (encoded as rank + suit integers)
- Community cards (padded to 5 slots with zeros if not yet dealt)
- Current pot size (normalized)
- Player stack sizes (normalized)
- Current bet to call (normalized)
- Player position (0 = small blind / first to act, 1 = big blind)
- Action history for current round (optional, adds complexity)

### Actions
- `0` = Fold
- `1` = Call / Check
- `2` = Raise 25% pot
- `3` = Raise 50% pot
- `4` = Raise 100% pot (pot-sized raise)
- `5` = All-in

Invalid actions (e.g. raising when you lack the chips) should be masked so the agent can only select legal actions at any given state.

### Reward
- `+pot` for winning the hand
- `-amount_lost` for losing the hand
- `0` at every intermediate step (reward is only assigned at hand completion)

---

## Agent Design

### DQN Agent (`dqn_agent.py`)
- Neural network: 3–4 fully connected layers with ReLU activations, linear output
- Output: Q-value for each of the 6 actions
- Training: Experience replay buffer + target network (updated every N steps)
- Exploration: Epsilon-greedy with epsilon decaying from 1.0 to 0.05 over training

### PPO Agent (`ppo_agent.py`)
- Architecture: Actor-critic — shared base network with separate policy (actor) and value (critic) heads
- Training: Clipped surrogate objective, entropy bonus to encourage exploration
- Update: Collect N steps of experience, then run K epochs of gradient updates on the batch

---

## Training Phases

1. **Phase 1 — Baseline:** Train each agent independently against the random agent. Target: both agents should achieve a significantly positive win rate vs random within a reasonable number of hands.
2. **Phase 2 — Self-play:** Each agent plays against a frozen copy of itself that updates periodically. This stabilizes training.
3. **Phase 3 — Head-to-head:** DQN and PPO play against each other simultaneously. Both agents update continuously. Track win rates over time.

---

## Evaluation & Plots to Produce

- Win rate vs. random agent over training (one curve per agent)
- Win rate in self-play over training
- Head-to-head win rate: DQN vs PPO over time
- Average pot won per hand (measures aggression)
- Fold rate over training (measures risk aversion / bluffing behavior)

These plots should be saved to `results/` and referenced in the README.

---

## Conventions

- **Language:** Python 3.10+
- **ML framework:** PyTorch (preferred over TensorFlow for flexibility)
- **No poker/card game libraries** — the game engine is built from scratch
- **Testing:** Unit tests for `card.py`, `hand_evaluator.py`, and `table.py` should be written before any RL code
- **Reproducibility:** All training runs should accept a `--seed` argument and log hyperparameters
- **Dependencies:** `torch`, `numpy`, `matplotlib`, `pytest` — keep the dependency list minimal

---

## Key Design Decisions & Rationale

| Decision | Rationale |
|---|---|
| No-Limit Hold'em with discretized bets | Realistic rules; variable bet sizes discretized into 6 actions to keep the action space manageable |
| Heads-up (2 players) | Simplifies environment dynamics; standard for poker AI research |
| Build game engine from scratch | Demonstrates full-stack understanding; better portfolio piece |
| DQN + PPO both implemented | Enables direct comparison; DQN is Q-value based, PPO is policy-gradient based |
| Head-to-head training | Agents co-evolve, producing emergent strategy differences |
| PyTorch over keras-rl | More control, more widely used in research, better for custom architectures |

---

## Known Challenges

- **Hand evaluator correctness:** The 7-card → best 5-card evaluation with tie-breaking logic is the trickiest part of the game engine. Test this exhaustively before moving to RL.
- **Reward sparsity:** Rewards only arrive at hand end, which can slow learning. Consider reward shaping if convergence is slow.
- **Non-stationarity:** In self-play and head-to-head training, the opponent changes over time, which can destabilize training. Periodic freezing of the opponent's weights helps.
- **Evaluation fairness:** When evaluating head-to-head, control for position (who is small blind) since position is a significant advantage in poker.