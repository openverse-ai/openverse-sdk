# Openverse SDK & CLI (Beta)

The **Openverse SDK** provides a lightweight Python interface for loading and running **text-based agent environments** hosted on the **Openverse Hub**.
It also includes the **Openverse CLI** (`openverse-cli`), a command-line tool for creating, pushing, pulling, and managing environment repositories — similar to `huggingface-cli`.

This toolkit enables researchers and developers to **create, distribute, and use reproducible evaluation environments** for benchmarking agents and LLMs.

> **Status:** Beta — APIs will expand and evolve.
> **Documentation:** [https://open-verse.ai/docs](https://open-verse.ai/docs) *(coming soon)*

---

## Installation

Install from PyPI:

```bash
pip install openverse-sdk
```

This installs:

* **Python SDK** (`openverse`)
* **Openverse CLI** (`openverse-cli`)

---

# SDK Usage

The Python SDK lets you **load, run, and cache** environments locally.
Environments are cached in:

```
~/.cache/openverse_envs/
```

### Load an Environment

```python
from openverse import make
env = make("TicTacToe-v0")
```

### Force Reload (skip cache)

```python
env = make("WordSearch-v0", force_reload=True)
```

---

# Openverse CLI

The CLI provides a simple way to **interact with the Openverse Hub**, including:

* Creating environment repositories
* Uploading (pushing) code
* Downloading (pulling) environments
* Managing tokens & authentication

Check installation:

```bash
openverse-cli --help
```

---

# Authentication

Log in using an **Openverse API Token**:

```bash
openverse-cli login
```

Your token (input hidden) is stored in:

```
~/.openverse/token.json
```

---

# Creating an Environment Repository

```bash
openverse-cli create MyEnv-v0
```

This creates a new repository under your Openverse account in the Hub.

---

# Pushing Environment Code

Push your local folder (default is `.`):

```bash
openverse-cli push MyEnv-v0 .
```

This sends a tarball of your code to the Hub and updates the Git repo.

---

# Pulling an Environment Repository

Download an environment’s source code:

```bash
openverse-cli pull MyEnv-v0
```

It will be extracted into:

```
./MyEnv-v0/
```

This mirrors HuggingFace-style behavior.

---

# Package Structure

This repository bundles both the **SDK** and the **CLI**:

```
openverse/
│
├── make.py          # SDK: environment loader
├── utils.py         # SDK utilities
│
└── cli/             # CLI implementation
    ├── cli.py       # Typer entrypoint
    ├── api.py
    ├── auth.py
    ├── config.py
    └── utils.py
```

The CLI executable is defined via:

```toml
[project.scripts]
openverse-cli = "openverse.cli.cli:app"
```

---

# Contributing

We welcome contributions — environments, issues, and feedback.
If you’re building evaluation environments or agent benchmarks, join us!

---

# License

**MIT License © Openverse.ai**
