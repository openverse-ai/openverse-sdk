# Openverse SDK (Beta)

The **Openverse SDK** provides a lightweight interface to the Openverse Hub, 
a collection of open, text-based environments designed for evaluation,
research, and experimentation with language models.

This kit allows developers to load and cache text-based game environments directly from the [Openverse Hub](https://open-verse.ai/environments).  
It is currently in **beta**, and documentation is **coming soon**.

---

## Installation

```bash
pip install openverse-sdk
```

## Quick Start

```python
from openverse import make
env = make("TicTacToe-v0")
```

Environments are automatically cached in user's local directory (~/.cache/openverse_envs) for subsequent loads.

## Documentation

Coming soon..