import os
import io
import tarfile

def make_tarball(path: str):
    """Tar-gzip a directory to memory."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(path, arcname=os.path.basename(path))
    buf.seek(0)
    return buf.read()