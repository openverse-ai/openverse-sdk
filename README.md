# Openverse SDK & CLI (Beta)

The **Openverse SDK** provides a lightweight interface for loading and running text-based agent environments from the **Openverse Hub**.

Alongside the SDK, the package also includes the **Openverse CLI** (`openverse-cli`), a command-line tool for creating, pushing, pulling, and managing environment repositories — similar to `huggingface-cli`.

This toolkit allows researchers and developers to **create, distribute, and use environments** for benchmarking Agents and LLMs.

> **Status:** Beta — API subject to changes as features expand.
> **Docs:** [https://open-verse.ai/docs](https://open-verse.ai/docs) (coming soon)

---

# Installation

Install from PyPI:

```bash
pip install openverse-sdk
```

This installs:

* the **Python SDK** (`openverse`)
* the **Openverse CLI** (`openverse-cli`)

---

# SDK Usage

The SDK allows you to load and run environments locally.
Environments are automatically cached in:

```
~/.cache/openverse_envs/
```

### **Load an environment**

```python
from openverse import make

env = make("TicTacToe-v0")
obs = env.reset()
print(obs)
```

### **Force reload (skip cache)**

```python
env = make("WordSearch-v0", force_reload=True)
```

---

# Openverse CLI

The `openverse-cli` tool is used to **interact with the Openverse Hub**, including creating, pushing, and pulling environment repositories.
It functions similarly to `huggingface-cli`.

### Check installation:

```bash
openverse-cli --help
```

You should see all available commands.

---

# Authentication

Before using CLI functionality, log in with your **Openverse API token**:

```bash
openverse-cli login
```

The CLI will prompt for your token (input hidden) and store it in:

```
~/.openverse/token.json
```

---

# Creating an Environment Repository

To upload a new environment to the Openverse Hub:

```bash
openverse-cli create MyEnv-v0
```

This creates a new repository under your Openverse account.

---

# Pushing Environment Code

Push your local folder (defaults to `.`):

```bash
openverse-cli push MyEnv-v0 .
```

This sends a tarball of your code to the Hub, where it is stored in a Git-based repository.

---

# Pulling an Environment Repository

Download an environment’s source code:

```bash
openverse-cli pull MyEnv-v0
```

This saves the repository contents to:

```
./repo.tar.gz
```

---

# Directory Structure (SDK + CLI)

This package bundles both the SDK and the CLI:

```
openverse/
│
├── make.py         # SDK: load environments
├── utils.py        # SDK utils
│
└── cli/            # CLI implementation
    ├── cli.py      # Typer entrypoint
    ├── api.py
    ├── auth.py
    ├── config.py
    └── utils.py
```

The CLI executable is exposed via:

```toml
[project.scripts]
openverse-cli = "openverse.cli.cli:app"
```

---

# Roadmap

* Private environment support
* Versioning (`--tag v1.0`)
* Collaboration model (add/remove collaborators)
* Environment templates (`openverse-cli init`)
* Docs & tutorials

---

# Contributing

We’re actively developing Openverse and welcome contributions — environments, feedback, or discussions.

---

# License

MIT License © Openverse.ai
