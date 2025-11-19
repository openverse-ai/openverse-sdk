import os
import io
import tarfile

def make_tarball(path: str):
    """Tar-gzip a directory to memory, ignoring any .git folder."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:

        def filter_func(tarinfo):
            # Completely skip .git directories and contents
            if ".git/" in tarinfo.name or tarinfo.name.endswith(".git"):
                return None
            return tarinfo

        tar.add(path, arcname=os.path.basename(path), filter=filter_func)

    buf.seek(0)
    return buf.read()

def normalize_repo_path(path: str) -> str:
    """
    Normalize a delete/push target path to ensure it's:
    - repo-relative
    - no leading dots, slashes
    - no traversal ('..') allowed
    - cleaned & collapsed ('a//b' → 'a/b')
    """
    if not path or not isinstance(path, str):
        raise ValueError("Invalid path")

    # Strip whitespace
    path = path.strip()

    # Remove leading "./" or "/" repeatedly
    while path.startswith("./") or path.startswith("/"):
        path = path[2:] if path.startswith("./") else path[1:]

    # Normalize the path (removes repeated slashes)
    path = os.path.normpath(path)

    # Prevent traversal outside repo
    if ".." in path.split(os.sep):
        raise ValueError("Path traversal ('..') is not allowed")

    # Final safety: ensure no leading slash remains
    path = path.lstrip("/")

    return path
