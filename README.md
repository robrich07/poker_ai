# Poker RL

A from-scratch Texas Hold'em poker engine with reinforcement learning agents built in Python.

## Current Status

The game engine is implemented and supports 2-10 player No-Limit Texas Hold'em.

### Game Engine (`poker/`)

- **`card.py`** — Card and Deck classes. Cards encode as integers (0-51) for use as model input.
- **`hand_evaluator.py`** — Evaluates the best 5-card hand from 7 cards. Handles all hand rankings from High Card through Straight Flush, including kicker-based tiebreaking and split pots.
- **`player.py`** — Player state management: chips, hole cards, betting, fold/all-in tracking.
- **`table.py`** — Full game loop: blinds, dealing, four betting rounds, and pot resolution. Supports variable bet sizing (25%/50%/100% pot and all-in) with action masking for legal moves.

### Rules

- **No-Limit Texas Hold'em** with discretized bet sizes
- 6 discrete actions: fold, call/check, raise 25% pot, raise 50% pot, raise 100% pot, all-in
- Standard betting rounds: Pre-flop, Flop, Turn, River
- Configurable blinds and starting chips

## Planned

### RL Environment (`poker/environment.py`)
Gym-style wrapper around the engine providing `reset()`, `step()`, and `render()` methods with a normalized state vector for agent input.

### Agents (`agents/`)
- **DQN Agent** — Deep Q-Network with experience replay and epsilon-greedy exploration
- **PPO Agent** — Actor-critic architecture with clipped surrogate objective

### Training (`training/`)
Three-phase training pipeline:
1. Train each agent vs a random baseline
2. Self-play with periodic opponent freezing
3. DQN vs PPO head-to-head with co-evolution

### Evaluation (`evaluation/`)
Win rates, fold rates, aggression metrics, and head-to-head performance plots.

Testing for game engine


## Tech Stack

- Python 3.10+
- PyTorch
- NumPy, Matplotlib, pytest
- No external poker/card game libraries — engine is built from scratch

## Setup

```bash
pip install torch numpy matplotlib pytest
```

## Running Tests

```bash
pytest tests/
```
