import os
from pathlib import Path
from .utils import git_clone, load_entry_point, dynamic_import

CACHE_DIR = Path(os.path.expanduser("~/.cache/openverse_envs"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)

GITEA_BASE = "http://52.221.207.255:3000/openverse_hub"

def make(id: str, force_reload: bool = False):
    """
    Load an Openverse environment by name.

    1. Checks cache (~/.cache/openverse_envs/<id>).
    2. If missing or force_reload=True, clones from Gitea.
    3. Parses pyproject.toml for entry_point.
    4. Dynamically loads and instantiates the environment class.
    """
    env_name = id.strip()
    env_dir = CACHE_DIR / env_name

    if env_dir.exists() and not force_reload:
        print(f"Using cached environment: {env_dir}")
    else:
        if force_reload and env_dir.exists():
            os.system(f"rm -rf '{env_dir}'")
        repo_url = f"{GITEA_BASE}/{env_name}.git"
        git_clone(repo_url, env_dir)

    # Load pyproject.toml
    pyproject_path = env_dir / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError(f"No pyproject.toml found in {env_dir}")

    module_name, class_name = load_entry_point(pyproject_path)
    EnvClass = dynamic_import(env_dir, module_name, class_name)
    env_instance = EnvClass()

    print(f"Loaded environment: {class_name} from {env_name}")
    return env_instance
