import subprocess
import importlib.util
import tomllib
from pathlib import Path


def git_clone(repo_url: str, dest: Path):
    """
    Perform a shallow clone (depth=1) for speed and minimal storage.
    """
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(dest)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def load_entry_point(pyproject_path: Path):
    """
    Extract 'openverse.entry_point' from pyproject.toml.
    """
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    entry = data.get("openverse", {}).get("entry_point")
    if not entry:
        raise ValueError(f"No [openverse] entry_point in {pyproject_path}")
    module_name, class_name = entry.split(":")
    return module_name, class_name


def dynamic_import(env_dir: Path, module_name: str, class_name: str):
    """
    Dynamically import the environment class from the module file.
    """
    file_path = env_dir / (module_name.replace(".", "/") + ".py")
    if not file_path.exists():
        raise FileNotFoundError(f"Expected module file not found: {file_path}")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)
